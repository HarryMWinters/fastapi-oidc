from pydantic import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    openid_connect_url: str = Field(..., env="AUTH_OPENID_CONNECT_URL")
    issuer: str = Field(..., env="AUTH_ISSUER")
    client_id: str = Field(..., env="AUTH_CLIENT_ID")


config = Config()
