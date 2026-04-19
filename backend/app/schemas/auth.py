from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    user_id: int
    username: str
    full_name: str
    role: str
    email: str | None = None
    profile_image_url: str | None = None
    assigned_warehouse_id: int | None = None
    assigned_warehouse_name: str | None = None


class ProfileUpdateRequest(BaseModel):
    username: str
    full_name: str
    email: str | None = None
    profile_image_url: str | None = None
    assigned_warehouse_id: int | None = None


class AvatarUploadResponse(BaseModel):
    success: bool
    profile_image_url: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
