from fastapi import APIRouter, Depends, HTTPException, Query
from mysql.connector import Error

from app.api.deps import get_current_user, get_warehouse_scope, require_roles
from app.db.connection import get_connection
from app.schemas.dashboard import (
    DashboardChartItem,
    DashboardRecentTransactionItem,
    DashboardSummaryResponse,
    DashboardWarehouseSummaryItem,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    current_user: dict = Depends(require_roles("Admin", "Manager", "Clerk")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor(dictionary=True)
        warehouse_scope = get_warehouse_scope(current_user)
        warehouse_filter = ""
        warehouse_params: list[object] = []
        if warehouse_scope is not None:
            warehouse_filter = " AND warehouse_id = %s"
            warehouse_params.append(warehouse_scope)

        cur.execute(
            f"SELECT COUNT(*) AS total FROM products WHERE is_deleted = 0{warehouse_filter}",
            tuple(warehouse_params),
        )
        total_products = int(cur.fetchone()["total"])

        cur.execute(
            f"SELECT COALESCE(SUM(current_stock), 0) AS total_stock FROM products WHERE is_deleted = 0{warehouse_filter}",
            tuple(warehouse_params),
        )
        total_stock = int(cur.fetchone()["total_stock"])

        cur.execute(
            f"SELECT COALESCE(SUM(current_stock * unit_price), 0) AS total_value "
            f"FROM products WHERE is_deleted = 0{warehouse_filter}",
            tuple(warehouse_params),
        )
        total_inventory_value = float(cur.fetchone()["total_value"])

        cur.execute(
            f"SELECT COUNT(*) AS cnt FROM products WHERE current_stock < low_stock_threshold AND is_deleted = 0{warehouse_filter}",
            tuple(warehouse_params),
        )
        low_stock_count = int(cur.fetchone()["cnt"])

        cur.execute(
            f"SELECT COUNT(*) AS cnt FROM products WHERE expiry_status = 'Expired' AND is_deleted = 0{warehouse_filter}",
            tuple(warehouse_params),
        )
        expired_count = int(cur.fetchone()["cnt"])

        cur.close()
        return DashboardSummaryResponse(
            total_products=total_products,
            total_stock=total_stock,
            total_inventory_value=total_inventory_value,
            low_stock_count=low_stock_count,
            expired_count=expired_count,
        )
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load dashboard summary")
    finally:
        conn.close()


@router.get("/recent-transactions", response_model=list[DashboardRecentTransactionItem])
def get_recent_transactions(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: dict = Depends(require_roles("Admin", "Manager", "Clerk")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        warehouse_scope = get_warehouse_scope(current_user)
        warehouse_filter = ""
        warehouse_params: list[object] = []
        if warehouse_scope is not None:
            warehouse_filter = "WHERE t.warehouse_id = %s"
            warehouse_params.append(warehouse_scope)
        cur.execute(
            """
            SELECT t.transaction_id, p.name, t.type, t.quantity,
                   DATE_FORMAT(t.transaction_date, '%Y-%m-%d %H:%i')
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            {warehouse_filter}
            ORDER BY t.transaction_date DESC
            LIMIT %s
            """.format(warehouse_filter=warehouse_filter),
            tuple(warehouse_params + [limit]),
        )
        rows = cur.fetchall()
        cur.close()

        return [
            DashboardRecentTransactionItem(
                transaction_id=row[0],
                product_name=row[1],
                type=row[2],
                quantity=row[3],
                transaction_date=row[4],
            )
            for row in rows
        ]
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load recent transactions")
    finally:
        conn.close()


@router.get("/warehouse-summary", response_model=list[DashboardWarehouseSummaryItem])
def get_warehouse_summary(
    current_user: dict = Depends(require_roles("Admin", "Manager", "Clerk")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor(dictionary=True)
        warehouse_scope = get_warehouse_scope(current_user)
        warehouse_filter = ""
        warehouse_params: list[object] = []
        if warehouse_scope is not None:
            warehouse_filter = " AND w.warehouse_id = %s"
            warehouse_params.append(warehouse_scope)
        cur.execute(
            f"""
            SELECT w.name,
                   COUNT(p.product_id) AS product_count,
                   COALESCE(SUM(p.current_stock), 0) AS total_stock,
                   COALESCE(SUM(p.current_stock * p.unit_price), 0) AS total_value,
                   SUM(CASE WHEN p.expiry_status = 'Expired' THEN 1 ELSE 0 END) AS expired_count,
                   SUM(CASE WHEN p.current_stock < p.low_stock_threshold THEN 1 ELSE 0 END) AS low_stock_count
            FROM warehouses w
            LEFT JOIN products p ON w.warehouse_id = p.warehouse_id AND p.is_deleted = 0
            WHERE w.is_active = 1{warehouse_filter}
            GROUP BY w.warehouse_id, w.name
            ORDER BY w.name
            """,
            tuple(warehouse_params),
        )
        rows = cur.fetchall()
        cur.close()
        return [
            DashboardWarehouseSummaryItem(
                name=row["name"],
                product_count=int(row["product_count"] or 0),
                total_stock=int(row["total_stock"] or 0),
                total_value=float(row["total_value"] or 0),
                expired_count=int(row["expired_count"] or 0),
                low_stock_count=int(row["low_stock_count"] or 0),
            )
            for row in rows
        ]
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load warehouse summary")
    finally:
        conn.close()


@router.get("/chart-data", response_model=list[DashboardChartItem])
def get_chart_data(
    period: str = Query(default="weekly", pattern="^(weekly|monthly)$"),
    current_user: dict = Depends(require_roles("Admin", "Manager", "Clerk")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        days = 7 if period == "weekly" else 30
        cur = conn.cursor(dictionary=True)
        warehouse_scope = get_warehouse_scope(current_user)
        warehouse_filter = ""
        warehouse_params: list[object] = []
        if warehouse_scope is not None:
            warehouse_filter = "AND warehouse_id = %s"
            warehouse_params.append(warehouse_scope)
        cur.execute(
            """
            SELECT DATE(transaction_date) AS day,
                   DAYNAME(DATE(transaction_date)) AS day_name,
                   SUM(CASE WHEN type = 'Stock-In' THEN quantity ELSE 0 END) AS stock_in,
                   SUM(CASE WHEN type = 'Stock-Out' THEN quantity ELSE 0 END) AS stock_out
            FROM transactions
            WHERE transaction_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            {warehouse_filter}
            GROUP BY DATE(transaction_date), DAYNAME(DATE(transaction_date))
            ORDER BY day
            """.format(warehouse_filter=f" {warehouse_filter}" if warehouse_filter else ""),
            tuple([days] + warehouse_params),
        )
        rows = cur.fetchall()
        cur.close()

        chart = []
        for row in rows:
            label = row["day_name"][:3] if period == "weekly" else str(row["day"].day)
            chart.append(
                DashboardChartItem(
                    label=label,
                    stock_in=int(row["stock_in"] or 0),
                    stock_out=int(row["stock_out"] or 0),
                )
            )
        return chart
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load chart data")
    finally:
        conn.close()
