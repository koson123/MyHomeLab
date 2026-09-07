import hmac
import os
import platform
from urllib.parse import urlparse

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel

AGENT_TOKEN = os.getenv("GAMEHUB_AGENT_TOKEN", "")
DRY_RUN = os.getenv("GAMEHUB_AGENT_DRY_RUN", "true").lower() not in {"0", "false", "no"}
ALLOWED_SCHEMES = {
    scheme.strip().lower()
    for scheme in os.getenv("GAMEHUB_AGENT_ALLOWED_SCHEMES", "steam,playnite").split(",")
    if scheme.strip()
}

app = FastAPI(title="Game Hub Windows Agent", version="0.2.0")


class LaunchCommand(BaseModel):
    game_id: int
    title: str
    provider: str
    launch_ref: str


def require_bearer(authorization: str | None) -> None:
    if not AGENT_TOKEN:
        raise HTTPException(status_code=503, detail="GAMEHUB_AGENT_TOKEN is not configured")
    prefix = "Bearer "
    if not authorization or not authorization.startswith(prefix):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    supplied = authorization[len(prefix):]
    if not hmac.compare_digest(supplied, AGENT_TOKEN):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")


def validate_launch_ref(launch_ref: str) -> str:
    parsed = urlparse(launch_ref)
    scheme = parsed.scheme.lower()
    if not scheme or scheme not in ALLOWED_SCHEMES:
        raise HTTPException(status_code=400, detail=f"URI scheme '{scheme or 'none'}' is not allowed")
    if len(launch_ref) > 2048:
        raise HTTPException(status_code=400, detail="launch_ref is too long")
    return launch_ref


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "game-hub-windows-agent",
        "version": "0.2.0",
        "platform": platform.system(),
        "dry_run": DRY_RUN,
        "allowed_schemes": sorted(ALLOWED_SCHEMES),
    }


@app.post("/v1/launch")
def launch(command: LaunchCommand, authorization: str | None = Header(default=None)) -> dict:
    require_bearer(authorization)
    launch_ref = validate_launch_ref(command.launch_ref)

    if DRY_RUN:
        return {
            "status": "dry-run",
            "game_id": command.game_id,
            "title": command.title,
            "provider": command.provider,
            "launch_ref": launch_ref,
        }

    if platform.system() != "Windows":
        raise HTTPException(status_code=501, detail="This agent only performs launches on Windows")

    os.startfile(launch_ref)  # type: ignore[attr-defined]
    return {
        "status": "launched",
        "game_id": command.game_id,
        "title": command.title,
        "provider": command.provider,
    }
