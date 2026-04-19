from pydantic import BaseModel, Field


class AccountItem(BaseModel):
    user_id: int
    username: str
    full_name: str
    role: str
    email: str | None
    is_active: int
    profile_image_url: str | None = None
    assigned_warehouse_id: int | None = None
    assigned_warehouse_name: str | None = None


class AccountListResponse(BaseModel):
    items: list[AccountItem]


class AccountCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=120)
    full_name: str = Field(min_length=1, max_length=100)
    role: str = Field(pattern="^(Admin|Manager|Clerk)$")
    email: str | None = None
    profile_image_url: str | None = Field(default=None, max_length=255)
    assigned_warehouse_id: int | None = None
    is_active: int = Field(default=1, ge=0, le=1)


class AccountUpdateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=100)
    role: str = Field(pattern="^(Admin|Manager|Clerk)$")
    email: str | None = None
    profile_image_url: str | None = Field(default=None, max_length=255)
    assigned_warehouse_id: int | None = None
    is_active: int = Field(default=1, ge=0, le=1)
    password: str | None = Field(default=None, min_length=4, max_length=120)


class AccountMutationResponse(BaseModel):
    success: bool
    message: str
    user_id: int | None = None
