from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserDto(BaseModel):
    id: str
    email: str
    name: str


class AuthResponse(BaseModel):
    user: UserDto
    token: str


class SessionResponse(BaseModel):
    user: UserDto
