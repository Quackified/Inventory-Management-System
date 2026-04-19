# Inventory Management System

Web-based inventory management app with:
- FastAPI backend (`backend/`)
- React frontend (`frontend/`)
- MySQL schema + seed scripts (`database/`)

## Quick Start (Windows)

### 1) Full setup + run

```powershell
./setup_and_run.ps1
```

This will:
- create/update `.venv`
- install backend and frontend dependencies
- start backend (`uvicorn`) and frontend (`npm run dev`)

### 2) Setup + run + reset DB (schema + seed)

```powershell
./setup_and_run.ps1 -ResetDb
```

Use this when you want a clean database for demos.

### 3) Start app only (no dependency setup)

```powershell
./start_webapp.ps1
```

## Script Summary

- `setup_and_run.ps1`: main setup + run flow (supports `-Force`, `-ResetDb`)
- `setup_and_run.bat`: Windows wrapper for the PowerShell setup script
- `start_webapp.ps1`: start backend + frontend assuming deps are already installed
- `start_webapp.bat`: Windows wrapper for the PowerShell start script

## Database

- Schema: `database/schema.sql`
- Seed: `database/seed_data.sql`
- Reset helper: `database/reset_db.py`

`-ResetDb` applies schema first, then seed, to keep schema/seed parity.
It recreates the target database before applying files, so existing data is removed.

## Default Seed Accounts

All seeded users use password:

```text
password
```

Accounts:
- `admin` (Admin)
- `manager` (Manager)
- `clerk` (Clerk)
- `warehouse_a` (Clerk)
- `warehouse_b` (Clerk)

## Environment

Backend env file:
- `backend/.env`

Minimum important values:
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`

## Production Notes

Before public deployment:
- set a strong `JWT_SECRET_KEY`
- update `CORS_ORIGINS` to your real frontend domain
- replace default seed credentials
- disable development `--reload` process style for backend
