from pydantic import BaseModel, Field


class WarehouseItem(BaseModel):
    warehouse_id: int
    name: str
    location: str | None
    is_active: int


class WarehouseListResponse(BaseModel):
    items: list[WarehouseItem]


class WarehouseWriteRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    location: str | None = None
    is_active: int = Field(default=1, ge=0, le=1)


class WarehouseMutationResponse(BaseModel):
    success: bool
    message: str
    warehouse_id: int | None = None
