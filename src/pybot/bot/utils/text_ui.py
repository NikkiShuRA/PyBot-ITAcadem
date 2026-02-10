async def progress_bar(current: int, max_: int, width: int = 10) -> str:
    if max_ <= 0:
        return "░" * width + " ???"
    if current >= max_:
        return "█" * width + " MAX"
    filled = int(current / max_ * width)
    filled = max(0, min(width, filled))
    pct = int(current / max_ * 100)
    return "█" * filled + "░" * (width - filled) + f" {pct}%"
