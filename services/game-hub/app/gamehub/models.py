from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class GameBase(SQLModel):
    canonical_title: str = Field(index=True)
    canonical_key: str = Field(index=True, sa_column_kwargs={"unique": True})
    sort_title: Optional[str] = None
    release_year: Optional[int] = Field(default=None, index=True)
    igdb_id: Optional[int] = Field(default=None, index=True)
    favorite: bool = False
    hidden: bool = False


class Game(GameBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class GameCreate(GameBase):
    pass


class ProviderAccountBase(SQLModel):
    provider: str = Field(index=True)
    display_name: str
    external_account_id: Optional[str] = Field(default=None, index=True)
    enabled: bool = True


class ProviderAccount(ProviderAccountBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)


class ProviderAccountCreate(ProviderAccountBase):
    pass


class EntitlementBase(SQLModel):
    game_id: int = Field(foreign_key="game.id", index=True)
    account_id: Optional[int] = Field(default=None, foreign_key="provideraccount.id", index=True)
    provider: str = Field(index=True)
    platform: Optional[str] = Field(default=None, index=True)
    ownership_type: str = Field(default="owned", index=True)
    external_product_id: Optional[str] = Field(default=None, index=True)
    edition: Optional[str] = None
    active: bool = True
    playtime_seconds: int = 0
    play_count: int = 0
    last_activity: Optional[datetime] = Field(default=None, index=True)


class Entitlement(EntitlementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class EntitlementCreate(EntitlementBase):
    pass


class DeviceBase(SQLModel):
    name: str = Field(index=True)
    kind: str = Field(default="pc", index=True)
    os: Optional[str] = None
    agent_url: Optional[str] = None
    enabled: bool = True


class Device(DeviceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    last_seen_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utcnow)


class DeviceCreate(DeviceBase):
    pass


class InstallationBase(SQLModel):
    game_id: int = Field(foreign_key="game.id", index=True)
    device_id: int = Field(foreign_key="device.id", index=True)
    provider: str = Field(index=True)
    status: str = Field(default="installed", index=True)
    external_product_id: Optional[str] = None
    install_path: Optional[str] = None


class Installation(InstallationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    detected_at: datetime = Field(default_factory=utcnow)


class InstallationCreate(InstallationBase):
    pass


class LaunchTargetBase(SQLModel):
    game_id: int = Field(foreign_key="game.id", index=True)
    device_id: int = Field(foreign_key="device.id", index=True)
    provider: str = Field(index=True)
    capability: str = Field(default="manual", index=True)
    method: str = Field(default="manual", index=True)
    launch_ref: Optional[str] = None
    enabled: bool = True


class LaunchTarget(LaunchTargetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)


class LaunchTargetCreate(LaunchTargetBase):
    pass


class LaunchRequest(SQLModel):
    launch_target_id: int


class LaunchResult(SQLModel):
    status: str
    game_id: int
    device_id: int
    launch_target_id: int
    detail: str


class PlayniteGameSnapshot(SQLModel):
    database_id: str
    name: str
    game_id: Optional[str] = None
    plugin_id: Optional[str] = None
    source: Optional[str] = None
    platforms: list[str] = Field(default_factory=list)
    release_year: Optional[int] = None
    is_installed: bool = False
    install_directory: Optional[str] = None
    playtime_seconds: int = 0
    play_count: int = 0
    last_activity: Optional[datetime] = None
    hidden: bool = False
    favorite: bool = False
    sorting_name: Optional[str] = None


class PlayniteSnapshot(SQLModel):
    device_name: str
    agent_url: Optional[str] = None
    games: list[PlayniteGameSnapshot]


class ImportResult(SQLModel):
    provider: str
    device_id: int
    games_received: int
    games_created: int
    entitlements_created: int
    installations_upserted: int
    launch_targets_upserted: int
