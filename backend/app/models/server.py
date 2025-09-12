from sqlalchemy import Column, Integer, String, DateTime, text
from app.db.base import Base


class Server(Base):
    __tablename__ = "t_server"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="标识")
    server_desc = Column(String(100), nullable=True, comment="服务器描述")
    server_ip = Column(String(100), nullable=False, comment="服务器地址")
    server_port = Column(String(10), nullable=False, comment="服务器端口")
    server_user = Column(String(20), nullable=False, comment="用户名")
    server_pass = Column(String(200), nullable=False, comment="密码")
    auth_memthod = Column(String(20), nullable=True, comment="认证方式,t_dmlx(dm=06)")
    server_os = Column(String(100), nullable=False, comment="系统,t_dmlx(dm=04)")
    status = Column(String(20), nullable=False, comment="状态,t_dmlx(dm=05)")
    create_time = Column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )
    creator = Column(String(20), nullable=True, comment="创建人")
    update_time = Column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        comment="最近更新时间",
    )
    updator = Column(String(20), nullable=True, comment="更新人")
