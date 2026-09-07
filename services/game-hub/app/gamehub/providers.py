from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ProviderDefinition:
    key: str
    name: str
    scan: str
    launch: str
    status: str
    notes: str


PROVIDERS = {
    "manual": ProviderDefinition(
        key="manual",
        name="Manual / Physical",
        scan="manual",
        launch="manual",
        status="foundation",
        notes="Fallback for physical games and sources without an automated connector.",
    ),
    "playnite": ProviderDefinition(
        key="playnite",
        name="Playnite Bridge",
        scan="planned",
        launch="planned",
        status="next",
        notes="Preferred first broad-coverage Windows bridge for storefront libraries and local installations.",
    ),
    "steam": ProviderDefinition("steam", "Steam", "planned", "agent", "planned", "Direct scan plus device-agent launch."),
    "epic": ProviderDefinition("epic", "Epic Games", "planned", "agent", "planned", "Provider scan plus Playnite/device-agent launch."),
    "gog": ProviderDefinition("gog", "GOG", "planned", "agent", "planned", "Provider scan plus Playnite/device-agent launch."),
    "xbox": ProviderDefinition("xbox", "Xbox / Microsoft", "planned", "mixed", "planned", "Library scanning plus PC/remote-session launch routes where supported."),
    "playstation": ProviderDefinition("playstation", "PlayStation", "planned", "remote_session", "planned", "Library scanning and supported remote-session routes."),
    "nintendo": ProviderDefinition("nintendo", "Nintendo", "planned", "manual", "planned", "Library tracking; direct remote launch remains manual unless a supported path exists."),
    "ea": ProviderDefinition("ea", "EA", "planned", "agent", "planned", "Initial coverage expected through Playnite bridge."),
    "ubisoft": ProviderDefinition("ubisoft", "Ubisoft Connect", "planned", "agent", "planned", "Initial coverage expected through Playnite bridge."),
    "battlenet": ProviderDefinition("battlenet", "Battle.net", "planned", "agent", "planned", "Initial coverage expected through Playnite bridge."),
    "amazon": ProviderDefinition("amazon", "Amazon Games", "planned", "agent", "planned", "Initial coverage expected through Playnite bridge."),
    "itch": ProviderDefinition("itch", "itch.io", "planned", "agent", "planned", "Initial coverage expected through Playnite bridge."),
    "romm": ProviderDefinition("romm", "RomM", "planned", "mixed", "planned", "Retro/ROM provider, not the master catalog."),
}


def list_providers() -> list[dict]:
    return [asdict(provider) for provider in PROVIDERS.values()]
