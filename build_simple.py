"""
Сборка упрощенной версии desktop приложения
Без backend сервера, все встроено напрямую
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    entry_point = repo_root / "desktop" / "simple_main.py"

    if not entry_point.exists():
        print(f"[build] Entry point not found: {entry_point}", file=sys.stderr)
        return 1

    hidden_imports = [
        # PyQt6 modules
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui", 
        "PyQt6.QtWidgets",
        # Backend services (только нужные)
        "backend.services.parsingservice",
        "backend.services.openai_service",
        # Selenium core
        "selenium.webdriver.chrome.service",
        "selenium.webdriver.chrome.options",
        "selenium.webdriver.common.by",
        # OpenAI
        "openai",
        # Requests
        "requests",
    ]

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "competitionmonitor-simple",
        "--onefile",
        "--noconsole",
        "--clean",
        # Add backend directory to paths
        "--add-data",
        f"{repo_root / 'backend'};backend",
        "--add-data", 
        f"{repo_root / 'desktop' / 'styles.py'};.",
        # Collect only essential modules
        "--collect-submodules",
        "selenium.webdriver.chrome",
        "--collect-submodules", 
        "selenium.webdriver.common",
    ]

    for hidden in hidden_imports:
        cmd.extend(["--hidden-import", hidden])

    cmd.append(str(entry_point))

    print("[build] Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=repo_root)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())