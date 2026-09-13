import hmac
import os
import re
from datetime import datetime, timezone
from typing import Annotated
from urllib.parse import urlparse

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from sqlmodel import Session, SQLModel, create_engine, select

from .models import (
    Device,
    DeviceCreate,
    Entitlement,
    EntitlementCreate,
    Game,
    GameCreate,
    ImportResult,
    Installation,
    InstallationCreate,
    LaunchRequest,
    LaunchResult,
    LaunchTarget,
    LaunchTargetCreate,
    PlayniteSnapshot,
    ProviderAccount,
    ProviderAccountCreate,
)
from .providers import PROVIDERS, list_providers

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gamehub.db")
GAMEHUB_API_KEY = os.getenv("GAMEHUB_API_KEY", "")
GAMEHUB_AGENT_TOKEN = os.getenv("GAMEHUB_AGENT_TOKEN", "")
ALLOWED_AGENT_HOSTS = {
    host.strip().lower()
    for host in os.getenv("GAMEHUB_ALLOWED_AGENT_HOSTS", "").split(",")
    if host.strip()
}

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, connect_args=connect_args)

app = FastAPI(
    title="Trevor Game Hub",
    version="0.2.0",
    description="Self-hosted game catalog, provider, device, and launch control plane.",
)


@app.on_event("startup")
def startup() -> None:
    if not GAMEHUB_API_KEY:
        raise RuntimeError("GAMEHUB_API_KEY must be set; refusing to start an unauthenticated Game Hub API")
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def require_api_key(x_gamehub_key: Annotated[str | None, Header()] = None) -> None:
    if not x_gamehub_key or not hmac.compare_digest(x_gamehub_key, GAMEHUB_API_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Game Hub API key")


ApiAuth = Depends(require_api_key)


def canonical_key_for_title(title: str, release_year: int | None, fallback: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not key:
        return fallback.lower()
    if release_year:
        return f"{key}-{release_year}"
    return key


def normalize_playnite_source(source: str | None) -> str:
    value = (source or "").strip().lower()
    if not value:
        return "playnite"
    if "steam" in value:
        return "steam"
    if "epic" in value:
        return "epic"
    if value == "gog" or "gog.com" in value:
        return "gog"
    if "xbox" in value or "microsoft" in value:
        return "xbox"
    if "playstation" in value or value == "psn":
        return "playstation"
    if "nintendo" in value:
        return "nintendo"
    if value in {"ea", "ea app", "origin"} or value.startswith("ea "):
        return "ea"
    if "ubisoft" in value or "uplay" in value:
        return "ubisoft"
    if "battle.net" in value or "battlenet" in value:
        return "battlenet"
    if "amazon" in value:
        return "amazon"
    if "itch" in value:
        return "itch"
    return "playnite"


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "game-hub", "version": "0.2.0"}


@app.get("/api/v1/providers", dependencies=[ApiAuth])
def providers() -> list[dict]:
    return list_providers()


@app.post("/api/v1/providers/{provider}/sync", dependencies=[ApiAuth])
def sync_provider(provider: str) -> dict:
    definition = PROVIDERS.get(provider)
    if not definition:
        raise HTTPException(status_code=404, detail="Unknown provider")
    if provider == "manual":
        return {"provider": provider, "status": "noop", "detail": "Manual provider has nothing to scan"}
    if provider == "playnite":
        return {
            "provider": provider,
            "status": "push",
            "detail": "Playnite sync is push-based; use POST /api/v1/import/playnite from the Playnite bridge",
        }
    raise HTTPException(
        status_code=501,
        detail=f"{definition.name} scanner is not implemented yet; provider contract is reserved",
    )


@app.post("/api/v1/import/playnite", response_model=ImportResult, dependencies=[ApiAuth])
def import_playnite(snapshot: PlayniteSnapshot, session: Session = Depends(get_session)) -> ImportResult:
    now = datetime.now(timezone.utc)
    device = session.exec(select(Device).where(Device.name == snapshot.device_name)).first()
    if device is None:
        device = Device(
            name=snapshot.device_name,
            kind="pc",
            os="Windows",
            agent_url=snapshot.agent_url,
            last_seen_at=now,
        )
        session.add(device)
        session.flush()
    else:
        if snapshot.agent_url:
            device.agent_url = snapshot.agent_url
        device.last_seen_at = now
        session.add(device)
        session.flush()

    games_created = 0
    entitlements_created = 0
    installations_upserted = 0
    launch_targets_upserted = 0

    for item in snapshot.games:
        canonical_key = canonical_key_for_title(
            item.name,
            item.release_year,
            f"playnite-{item.database_id}",
        )
        game = session.exec(select(Game).where(Game.canonical_key == canonical_key)).first()
        if game is None:
            game = Game(
                canonical_title=item.name,
                canonical_key=canonical_key,
                sort_title=item.sorting_name,
                release_year=item.release_year,
                favorite=item.favorite,
                hidden=item.hidden,
            )
            session.add(game)
            session.flush()
            games_created += 1
        else:
            if item.sorting_name and not game.sort_title:
                game.sort_title = item.sorting_name
            if item.release_year and not game.release_year:
                game.release_year = item.release_year
            game.favorite = game.favorite or item.favorite
            game.updated_at = now
            session.add(game)

        provider = normalize_playnite_source(item.source)
        external_product_id = item.game_id or item.database_id
        platform = " | ".join(item.platforms) if item.platforms else None

        entitlement = session.exec(
            select(Entitlement).where(
                Entitlement.game_id == game.id,
                Entitlement.provider == provider,
                Entitlement.external_product_id == external_product_id,
            )
        ).first()
        if entitlement is None:
            entitlement = Entitlement(
                game_id=game.id,
                provider=provider,
                platform=platform,
                ownership_type="library_access",
                external_product_id=external_product_id,
                active=True,
                playtime_seconds=item.playtime_seconds,
                play_count=item.play_count,
                last_activity=item.last_activity,
            )
            session.add(entitlement)
            entitlements_created += 1
        else:
            entitlement.platform = platform
            entitlement.active = True
            entitlement.playtime_seconds = item.playtime_seconds
            entitlement.play_count = item.play_count
            entitlement.last_activity = item.last_activity
            entitlement.updated_at = now
            session.add(entitlement)

        installation = session.exec(
            select(Installation).where(
                Installation.game_id == game.id,
                Installation.device_id == device.id,
                Installation.provider == provider,
                Installation.external_product_id == item.database_id,
            )
        ).first()
        if installation is None:
            installation = Installation(
                game_id=game.id,
                device_id=device.id,
                provider=provider,
                status="installed" if item.is_installed else "not_installed",
                external_product_id=item.database_id,
                install_path=item.install_directory,
            )
            session.add(installation)
        else:
            installation.status = "installed" if item.is_installed else "not_installed"
            installation.install_path = item.install_directory
            installation.detected_at = now
            session.add(installation)
        installations_upserted += 1

        launch_ref = f"playnite://playnite/start/{item.database_id}"
        launch_target = session.exec(
            select(LaunchTarget).where(
                LaunchTarget.game_id == game.id,
                LaunchTarget.device_id == device.id,
                LaunchTarget.method == "agent",
                LaunchTarget.launch_ref == launch_ref,
            )
        ).first()

        if item.is_installed:
            if launch_target is None:
                launch_target = LaunchTarget(
                    game_id=game.id,
                    device_id=device.id,
                    provider=provider,
                    capability="full",
                    method="agent",
                    launch_ref=launch_ref,
                    enabled=True,
                )
                session.add(launch_target)
            else:
                launch_target.provider = provider
                launch_target.capability = "full"
                launch_target.enabled = True
                session.add(launch_target)
            launch_targets_upserted += 1
        elif launch_target is not None and launch_target.enabled:
            launch_target.enabled = False
            session.add(launch_target)
            launch_targets_upserted += 1

    session.commit()

    return ImportResult(
        provider="playnite",
        device_id=device.id,
        games_received=len(snapshot.games),
        games_created=games_created,
        entitlements_created=entitlements_created,
        installations_upserted=installations_upserted,
        launch_targets_upserted=launch_targets_upserted,
    )


@app.post("/api/v1/games", response_model=Game, dependencies=[ApiAuth])
def create_game(payload: GameCreate, session: Session = Depends(get_session)) -> Game:
    existing = session.exec(select(Game).where(Game.canonical_key == payload.canonical_key)).first()
    if existing:
        raise HTTPException(status_code=409, detail="canonical_key already exists")
    game = Game.model_validate(payload)
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


@app.get("/api/v1/games", response_model=list[Game], dependencies=[ApiAuth])
def get_games(
    query: str | None = Query(default=None, max_length=200),
    session: Session = Depends(get_session),
) -> list[Game]:
    statement = select(Game)
    if query:
        statement = statement.where(Game.canonical_title.contains(query))
    return list(session.exec(statement.order_by(Game.canonical_title)).all())


@app.post("/api/v1/accounts", response_model=ProviderAccount, dependencies=[ApiAuth])
def create_account(payload: ProviderAccountCreate, session: Session = Depends(get_session)) -> ProviderAccount:
    if payload.provider not in PROVIDERS:
        raise HTTPException(status_code=400, detail="Unknown provider")
    account = ProviderAccount.model_validate(payload)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@app.get("/api/v1/accounts", response_model=list[ProviderAccount], dependencies=[ApiAuth])
def get_accounts(session: Session = Depends(get_session)) -> list[ProviderAccount]:
    return list(session.exec(select(ProviderAccount).order_by(ProviderAccount.provider)).all())


@app.post("/api/v1/entitlements", response_model=Entitlement, dependencies=[ApiAuth])
def create_entitlement(payload: EntitlementCreate, session: Session = Depends(get_session)) -> Entitlement:
    if not session.get(Game, payload.game_id):
        raise HTTPException(status_code=404, detail="Game not found")
    if payload.account_id is not None and not session.get(ProviderAccount, payload.account_id):
        raise HTTPException(status_code=404, detail="Provider account not found")
    entitlement = Entitlement.model_validate(payload)
    session.add(entitlement)
    session.commit()
    session.refresh(entitlement)
    return entitlement


@app.get("/api/v1/entitlements", response_model=list[Entitlement], dependencies=[ApiAuth])
def get_entitlements(session: Session = Depends(get_session)) -> list[Entitlement]:
    return list(session.exec(select(Entitlement)).all())


@app.post("/api/v1/devices", response_model=Device, dependencies=[ApiAuth])
def create_device(payload: DeviceCreate, session: Session = Depends(get_session)) -> Device:
    device = Device.model_validate(payload)
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


@app.get("/api/v1/devices", response_model=list[Device], dependencies=[ApiAuth])
def get_devices(session: Session = Depends(get_session)) -> list[Device]:
    return list(session.exec(select(Device).order_by(Device.name)).all())


@app.post("/api/v1/installations", response_model=Installation, dependencies=[ApiAuth])
def create_installation(payload: InstallationCreate, session: Session = Depends(get_session)) -> Installation:
    if not session.get(Game, payload.game_id):
        raise HTTPException(status_code=404, detail="Game not found")
    if not session.get(Device, payload.device_id):
        raise HTTPException(status_code=404, detail="Device not found")
    installation = Installation.model_validate(payload)
    session.add(installation)
    session.commit()
    session.refresh(installation)
    return installation


@app.get("/api/v1/installations", response_model=list[Installation], dependencies=[ApiAuth])
def get_installations(session: Session = Depends(get_session)) -> list[Installation]:
    return list(session.exec(select(Installation)).all())


@app.post("/api/v1/launch-targets", response_model=LaunchTarget, dependencies=[ApiAuth])
def create_launch_target(payload: LaunchTargetCreate, session: Session = Depends(get_session)) -> LaunchTarget:
    if not session.get(Game, payload.game_id):
        raise HTTPException(status_code=404, detail="Game not found")
    if not session.get(Device, payload.device_id):
        raise HTTPException(status_code=404, detail="Device not found")
    if payload.method == "agent" and not payload.launch_ref:
        raise HTTPException(status_code=400, detail="Agent launch targets require launch_ref")
    target = LaunchTarget.model_validate(payload)
    session.add(target)
    session.commit()
    session.refresh(target)
    return target


@app.get("/api/v1/launch-targets", response_model=list[LaunchTarget], dependencies=[ApiAuth])
def get_launch_targets(session: Session = Depends(get_session)) -> list[LaunchTarget]:
    return list(session.exec(select(LaunchTarget)).all())


def agent_host_is_allowed(agent_url: str) -> bool:
    parsed = urlparse(agent_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    return parsed.hostname.lower() in ALLOWED_AGENT_HOSTS


@app.post("/api/v1/launch", response_model=LaunchResult, dependencies=[ApiAuth])
async def launch(payload: LaunchRequest, session: Session = Depends(get_session)) -> LaunchResult:
    target = session.get(LaunchTarget, payload.launch_target_id)
    if not target or not target.enabled:
        raise HTTPException(status_code=404, detail="Enabled launch target not found")

    game = session.get(Game, target.game_id)
    device = session.get(Device, target.device_id)
    if not game or not device or not device.enabled:
        raise HTTPException(status_code=409, detail="Game or device is unavailable")

    if target.capability == "manual" or target.method == "manual":
        return LaunchResult(
            status="manual",
            game_id=game.id,
            device_id=device.id,
            launch_target_id=target.id,
            detail=f"{game.canonical_title} is tracked, but this target requires manual launch",
        )

    if target.method != "agent":
        raise HTTPException(status_code=501, detail=f"Launch method '{target.method}' is not implemented yet")
    if not device.agent_url:
        raise HTTPException(status_code=409, detail="Device has no agent_url")
    if not agent_host_is_allowed(device.agent_url):
        raise HTTPException(status_code=403, detail="Device agent host is not in GAMEHUB_ALLOWED_AGENT_HOSTS")
    if not GAMEHUB_AGENT_TOKEN:
        raise HTTPException(status_code=503, detail="GAMEHUB_AGENT_TOKEN is not configured")

    request_body = {
        "game_id": game.id,
        "title": game.canonical_title,
        "provider": target.provider,
        "launch_ref": target.launch_ref,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{device.agent_url.rstrip('/')}/v1/launch",
                json=request_body,
                headers={"Authorization": f"Bearer {GAMEHUB_AGENT_TOKEN}"},
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Device agent launch failed: {exc.__class__.__name__}") from exc

    return LaunchResult(
        status="dispatched",
        game_id=game.id,
        device_id=device.id,
        launch_target_id=target.id,
        detail=f"Launch request dispatched to {device.name}",
    )
