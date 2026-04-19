from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_products: int
    total_stock: int
    total_inventory_value: float
    low_stock_count: int
    expired_count: int


class DashboardRecentTransactionItem(BaseModel):
    transaction_id: int
    product_name: str
    type: str
    quantity: int
    transaction_date: str


class DashboardWarehouseSummaryItem(BaseModel):
    name: str
    product_count: int
    total_stock: int
    total_value: float
    expired_count: int
    low_stock_count: int


class DashboardChartItem(BaseModel):
    label: str
    stock_in: int
    stock_out: int
