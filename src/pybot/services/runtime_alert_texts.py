from __future__ import annotations


def runtime_startup_notification(*, bot_mode: str, health_api_enabled: bool) -> str:
    health_status = "enabled" if health_api_enabled else "disabled"
    return f"PyBot ITAcadem runtime alert\n\nEvent: bot startup\nMode: {bot_mode}\nHealth API: {health_status}"


def runtime_shutdown_notification(*, bot_mode: str) -> str:
    return f"PyBot ITAcadem runtime alert\n\nEvent: bot shutdown\nMode: {bot_mode}"
