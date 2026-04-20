from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import require_roles
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reset-db")
def reset_database_for_testing(
    _: dict = Depends(require_roles("Admin")),
):
    if settings.APP_ENV.strip().lower() in {"prod", "production"}:
        raise HTTPException(status_code=403, detail="Database reset is disabled in production.")

    project_root = Path(__file__).resolve().parents[5]
    reset_script = project_root / "database" / "reset_db.py"
    schema_file = project_root / "database" / "schema.sql"
    seed_file = project_root / "database" / "seed_data.sql"
    env_file = project_root / "backend" / ".env"

    for path in [reset_script, schema_file, seed_file]:
        if not path.exists():
            raise HTTPException(status_code=500, detail=f"Required file missing: {path}")

    command = [
        sys.executable,
        str(reset_script),
        "--schema",
        str(schema_file),
        "--seed",
        str(seed_file),
        "--env-file",
        str(env_file),
    ]

    result = subprocess.run(
        command,
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        failure = (result.stderr or result.stdout or "Database reset failed").strip()
        raise HTTPException(status_code=500, detail=failure)

    return {
        "success": True,
        "message": "Database reset completed for testing.",
    }
