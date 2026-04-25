"""Backward-compatible shim for the seed CLI.

The canonical implementation lives in ``src/pybot/cli/seed.py`` and is
registered as the ``pybot-seed`` console script in ``pyproject.toml``.

This file is kept in the repository root so that existing local commands such
as ``python fill_point_db.py --help`` and references inside CI smoke-checks
continue to work without modification.

Prefer ``pybot-seed`` or ``python -m pybot.cli.seed`` for new invocations.
"""

from pybot.cli.seed import main

if __name__ == "__main__":
    main()
