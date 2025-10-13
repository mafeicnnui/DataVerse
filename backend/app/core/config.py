from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
from typing import List, Union
import os


class Settings(BaseSettings):
    APP_NAME: str = "db_expert Backend"
    API_PREFIX: str = "/api"

    # Default to provided MySQL (URL-encoded '@' in password). Override via env `DATABASE_URL` if needed.
    # Example: mysql+aiomysql://puppet:Puppet%40123@10.2.39.59:3306/db_expert?charset=utf8mb4
    DATABASE_URL: str = (
        os.getenv("DATABASE_URL")
        or "mysql+aiomysql://puppet:Puppet%40123@10.2.39.59:3306/db_expert?charset=utf8mb4"
    )

    # CORS
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://10.16.45.135:5173"
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://10.16.45.135:3000",
    ]
    # 允许通过 IP 访问的前端来源（正则）。例如：http://10.16.45.135:5173
    # 可通过环境变量 CORS_ORIGIN_REGEX 覆盖
    CORS_ORIGIN_REGEX: str | None = os.getenv("CORS_ORIGIN_REGEX") or r"^https?://[0-9\.]+(?::[0-9]+)?$"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


settings = Settings()
