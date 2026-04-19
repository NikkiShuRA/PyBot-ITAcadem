import os
from pathlib import Path
import subprocess
import sys


def test_import_di_containers_without_required_env(tmp_path: Path) -> None:
    runtime_env = os.environ.copy()
    project_root = Path(__file__).resolve().parents[2]
    runtime_env["PYTHONPATH"] = os.pathsep.join(
        [
            str(project_root / "src"),
            str(project_root),
            runtime_env.get("PYTHONPATH", ""),
        ]
    )
    for key in ("BOT_TOKEN", "BOT_TOKEN_TEST", "ROLE_REQUEST_ADMIN_TG_ID", "DATABASE_URL"):
        runtime_env.pop(key, None)

    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", "from pybot.di import containers; print('ok')"],  # noqa: S607
        capture_output=True,
        check=False,
        cwd=tmp_path,
        env=runtime_env,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "ok"
    assert "ValidationError" not in result.stderr
