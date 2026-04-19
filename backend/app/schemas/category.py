from pydantic import BaseModel, Field


class CategoryItem(BaseModel):
    category_id: int
    name: str
    description: str | None


class CategoryListResponse(BaseModel):
    items: list[CategoryItem]


class CategoryWriteRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None


class CategoryMutationResponse(BaseModel):
    success: bool
    message: str
    category_id: int | None = None
