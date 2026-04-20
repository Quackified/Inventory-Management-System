from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.accounts import router as accounts_router
from app.api.v1.routes.categories import router as categories_router
from app.api.v1.routes.exports import router as exports_router
from app.api.v1.routes.dashboard import router as dashboard_router
from app.api.v1.routes.products import router as products_router
from app.api.v1.routes.warehouses import router as warehouses_router
from app.api.v1.routes.transactions import router as transactions_router
from app.core.config import settings
from app.core.storage import UPLOADS_DIR
from app.db.connection import (
    check_db_connection,
    ensure_batch_tracking_support,
    ensure_transaction_cost_column,
    ensure_transaction_warehouse_support,
    ensure_user_profile_columns,
)

app = FastAPI(title=settings.APP_NAME)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

allowed_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(accounts_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(exports_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(warehouses_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


@app.on_event("startup")
def startup_migrations():
    ensure_user_profile_columns()
    ensure_transaction_cost_column()
    ensure_transaction_warehouse_support()
    ensure_batch_tracking_support()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "db_connected": check_db_connection(),
        "environment": settings.APP_ENV,
    }
