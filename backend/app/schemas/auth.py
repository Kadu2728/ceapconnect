"""Schemas Pydantic de autenticação (EPIC 02).

Toda validação de formato (CPF com dígito verificador, telefone, senha)
acontece aqui, na borda da API — a camada de services nunca deve confiar
em dado já "validado" pelo cliente.
"""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.schemas.user import UserSummary
from app.utils.validators import extract_digits, is_valid_cpf, is_valid_phone


class RegisterRequest(BaseModel):
    """Corpo de `POST /api/v1/auth/register`."""

    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    cpf: str = Field(description="CPF com ou sem máscara — normalizado no backend.")
    phone: str = Field(description="Telefone com ou sem máscara — normalizado no backend.")
    password: str = Field(min_length=8, max_length=72)
    password_confirmation: str

    @field_validator("name")
    @classmethod
    def _normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("O nome não pode ser vazio.")
        return normalized

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()

    @field_validator("cpf")
    @classmethod
    def _validate_cpf(cls, value: str) -> str:
        digits = extract_digits(value)
        if not is_valid_cpf(digits):
            raise ValueError("CPF inválido.")
        return digits

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, value: str) -> str:
        digits = extract_digits(value)
        if not is_valid_phone(digits):
            raise ValueError("Telefone inválido. Informe DDD + número (10 ou 11 dígitos).")
        return digits

    @model_validator(mode="after")
    def _validate_password_confirmation(self) -> "RegisterRequest":
        if self.password != self.password_confirmation:
            raise ValueError("As senhas não coincidem.")
        return self


class LoginRequest(BaseModel):
    """Corpo de `POST /api/v1/auth/login`."""

    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()


class RefreshRequest(BaseModel):
    """Corpo de `POST /api/v1/auth/refresh`."""

    refresh_token: str = Field(min_length=1)


class TokenPairResponse(BaseModel):
    """Dado retornado por `POST /api/v1/auth/login`."""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserSummary


class AccessTokenResponse(BaseModel):
    """Dado retornado por `POST /api/v1/auth/refresh`."""

    access_token: str
