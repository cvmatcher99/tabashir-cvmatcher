"""
PyInstaller entry point – sets working directory to the executable's folder
so uploads/, logs/, and static/ resolve correctly at runtime.
"""
import os
import sys
from pathlib import Path


def resource_path(relative: str) -> str:
    """Return absolute path – works for both dev and PyInstaller bundles."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    return str(base / relative)


# Change cwd to executable directory so relative paths work
if getattr(sys, "frozen", False):
    os.chdir(Path(sys.executable).parent)

# Create runtime directories
for d in ("uploads", "logs"):
    Path(d).mkdir(exist_ok=True)

# Bootstrap .env if not present
env_file = Path(".env")
if not env_file.exists():
    example = Path(resource_path(".env.example"))
    if example.exists():
        env_file.write_text(example.read_text())
        print("[cv_matcher] Created .env from .env.example – please edit before use.")

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"[cv_matcher] Starting on http://localhost:{port}")
    print(f"[cv_matcher] API docs: http://localhost:{port}/docs")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )
