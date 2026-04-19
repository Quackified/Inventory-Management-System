from pydantic import BaseModel


class TransactionListItem(BaseModel):
    transaction_id: int
    product: str
    type: str
    quantity: int
    unit_cost: float | None
    total_cost: float | None
    transaction_date: str
    remarks: str | None
    user: str
    warehouse: str
    category: str
    batch: str


class TransactionListResponse(BaseModel):
    items: list[TransactionListItem]
    page: int
    page_size: int
    total: int


class TransactionWriteRequest(BaseModel):
    product_id: int
    type: str
    quantity: int
    remarks: str | None = None
    warehouse_id: int | None = None
    unit_price: float | None = None


class TransactionMutationResponse(BaseModel):
    success: bool
    message: str
    transaction_id: int | None = None
