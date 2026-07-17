import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_formal_clis_have_help() -> None:
    modules = (
        "conflict_detection.cli.preprocess_cli",
        "conflict_detection.cli.prepare_run_cli",
        "conflict_detection.cli.run_scheduler_cli",
        "conflict_detection.cli.rebuild_final_cli",
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT)))
    for module in modules:
        completed = subprocess.run(
            [sys.executable, "-m", module, "--help"],
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
        assert completed.returncode == 0, completed.stderr
