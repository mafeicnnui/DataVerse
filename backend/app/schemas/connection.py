from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ConnectionBase(BaseModel):
    ip: str
    port: str
    user: Optional[str] = None
    password: Optional[str] = None
    db_type: Optional[str] = None
    db_env: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    create_time: Optional[datetime] = None
    creator: Optional[str] = None
    update_time: Optional[datetime] = None
    updator: Optional[str] = None


class ConnectionCreate(BaseModel):
    ip: str
    port: str
    user: str
    password: str
    db_type: Optional[str] = "mysql"
    db_env: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    creator: Optional[str] = None


class ConnectionUpdate(BaseModel):
    ip: Optional[str] = None
    port: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    db_type: Optional[str] = None
    db_env: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    create_time: Optional[datetime] = None
    creator: Optional[str] = None
    update_time: Optional[datetime] = None
    updator: Optional[str] = None


class ConnectionOut(ConnectionBase):
    id: int

    class Config:
        from_attributes = True
