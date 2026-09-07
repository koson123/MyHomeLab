import hmac
import os
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
    Installation,
    InstallationCreate,
    LaunchRequest,
    LaunchResult,
    LaunchTarget,
    LaunchTargetCreate,
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
    version="0.1.0",
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


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "game-hub", "version": "0.1.0"}


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
    raise HTTPException(
        status_code=501,
        detail=f"{definition.name} scanner is not implemented yet; provider contract is reserved",
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
