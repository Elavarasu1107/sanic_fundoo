from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore', case_sensitive=False)

    neo_uri: str
    base_url: str
    port: int
    admin_key: str
    email_host_user: EmailStr
    email_host_password: str
    smtp: str
    smtp_port: int
    jwt_exp: int
    jwt_algo: str


settings = Settings()
