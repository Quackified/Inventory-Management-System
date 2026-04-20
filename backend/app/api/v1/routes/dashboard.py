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
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard summary: {exc}")
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
            warehouse_filter = "WHERE COALESCE(t.warehouse_id, p.warehouse_id) = %s"
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
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load recent transactions: {exc}")
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
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load warehouse summary: {exc}")
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

        query = """
            SELECT t.transaction_date, t.type, t.quantity
            FROM transactions t
            JOIN products p ON p.product_id = t.product_id
            WHERE 1 = 1
        """
        params: list[object] = []
        if warehouse_scope is not None:
            query += " AND COALESCE(t.warehouse_id, p.warehouse_id) = %s"
            params.append(warehouse_scope)

        query += " ORDER BY t.transaction_date DESC LIMIT 5000"
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()

        # Aggregate by transaction day and keep only the most recent N distinct days.
        day_buckets: dict[str, dict[str, int | str]] = {}
        ordered_days: list[str] = []
        for row in rows:
            tx_dt = row.get("transaction_date")
            if tx_dt is None:
                continue

            day_key = tx_dt.strftime("%Y-%m-%d")
            if day_key not in day_buckets:
                day_buckets[day_key] = {
                    "day_name": tx_dt.strftime("%a"),
                    "day_of_month": tx_dt.day,
                    "stock_in": 0,
                    "stock_out": 0,
                }
                ordered_days.append(day_key)

            tx_type = str(row.get("type") or "")
            qty = int(row.get("quantity") or 0)
            if tx_type == "Stock-In":
                day_buckets[day_key]["stock_in"] = int(day_buckets[day_key]["stock_in"]) + qty
            elif tx_type == "Stock-Out":
                day_buckets[day_key]["stock_out"] = int(day_buckets[day_key]["stock_out"]) + qty

            if len(ordered_days) >= days:
                # Keep collecting rows for already discovered day keys only.
                # Stop once rows move beyond the oldest captured key.
                oldest_kept_day = ordered_days[-1]
                if day_key < oldest_kept_day:
                    break

        selected_days = sorted(ordered_days[:days])
        chart: list[DashboardChartItem] = []
        for day_key in selected_days:
            bucket = day_buckets[day_key]
            label = str(bucket["day_name"]) if period == "weekly" else str(bucket["day_of_month"])
            chart.append(
                DashboardChartItem(
                    label=label,
                    stock_in=int(bucket["stock_in"]),
                    stock_out=int(bucket["stock_out"]),
                )
            )

        return chart
    except Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load chart data: {exc}")
    finally:
        conn.close()
