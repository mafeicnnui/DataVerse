from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ServerBase(BaseModel):
    server_desc: Optional[str] = None
    server_ip: str
    server_port: str
    server_user: str
    server_pass: str
    auth_memthod: Optional[str] = None  # 认证方式,t_dmlx(dm=05)
    server_os: str  # t_dmlx(dm=04)
    status: str     # t_dmlx(dm=05)
    creator: Optional[str] = None
    updator: Optional[str] = None


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    server_desc: Optional[str] = None
    server_ip: Optional[str] = None
    server_port: Optional[str] = None
    server_user: Optional[str] = None
    server_pass: Optional[str] = None
    auth_memthod: Optional[str] = None
    server_os: Optional[str] = None
    status: Optional[str] = None
    updator: Optional[str] = None


class ServerOut(ServerBase):
    id: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True
