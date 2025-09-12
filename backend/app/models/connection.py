from sqlalchemy import Integer, String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Connection(Base):
    __tablename__ = "t_db_source"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ip: Mapped[str] = mapped_column(String(100), nullable=False, comment="数据库IP")
    port: Mapped[str] = mapped_column(String(20), nullable=False, comment="数据库端口")
    user: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="用户名")
    password: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="密码")
    db_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="数据库类型,t_dmlx(dm=01)")
    db_env: Mapped[str | None] = mapped_column(String(1), nullable=True, comment="数据库环境,t_dmlx(dm=02)")
    description: Mapped[str | None] = mapped_column(String(40), nullable=True, comment="数据源描述")
    status: Mapped[str | None] = mapped_column(String(1), nullable=True, comment="数据源状态,t_dmlx(dm=03)")
    create_time: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )
    creator: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="创建人")
    update_time: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        comment="最近更新时间",
    )
    updator: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="更新人")
