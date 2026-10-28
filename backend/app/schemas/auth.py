# contrato do cadastro e do login (NS-035); a senha nunca volta na resposta
from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, Field, StringConstraints

# o EmailStr so normaliza o dominio; o login nao pode depender da caixa
Email = Annotated[EmailStr, AfterValidator(str.lower)]


class NovoUsuario(BaseModel):
    """dados minimos do cadastro."""

    # so o nome e aparado ("   " vira vazio); a senha vale como foi digitada,
    # senao o login, que nao apara, nunca confere
    nome: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
    ]
    email: Email
    # teto para ninguem mandar megabytes ao argon2
    senha: str = Field(min_length=8, max_length=128)


class Login(BaseModel):
    """credenciais do login."""

    email: Email
    senha: str = Field(min_length=1, max_length=128)


class Usuario(BaseModel):
    """o que o front ve do usuario."""

    id: str
    nome: str
    email: str


class Acesso(BaseModel):
    """token para o header Authorization: Bearer, com o usuario logado."""

    token: str
    usuario: Usuario
