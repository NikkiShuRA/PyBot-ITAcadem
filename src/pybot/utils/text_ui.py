import textwrap


def progress_bar(current: int, max_: int, width: int = 10) -> str:
    filled = 0
    pct = "???"
    if max_ == 0:
        filled = width
        pct = "MAX"
    elif max_ > 0:
        filled = int(current / max_ * width)
        filled = max(0, min(width, filled))
        pct = f"{int(current / max_ * 100)}%"
    # Не знаю почему, но только так правильно отображается в выводе профиля
    bar = textwrap.dedent(
        f"""\
            {"█" * filled + "░" * (width - filled)} {pct}
                        {current} / {"♾️" if max_ <= 0 else max_}\
        """
    )
    return bar
