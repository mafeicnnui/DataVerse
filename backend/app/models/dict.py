from sqlalchemy import String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DictCategory(Base):
    __tablename__ = "t_dmlx"

    dm: Mapped[str] = mapped_column(String(10), primary_key=True, comment="大类代码")
    mc: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="大类名称")
    status: Mapped[str | None] = mapped_column(String(1), nullable=True, comment="大类状态,0:失效，1：有效")
    create_time: Mapped[DateTime | None] = mapped_column(
        DateTime, nullable=True, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"
    )
    update_time: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        comment="更新时间",
    )


class DictItem(Base):
    __tablename__ = "t_dmmx"

    dm: Mapped[str] = mapped_column(String(10), primary_key=True, comment="代码大类")
    dmm: Mapped[str] = mapped_column(String(20), primary_key=True, comment="代码小类")
    dmmc: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="小类名称")
    status: Mapped[str | None] = mapped_column(String(1), nullable=True, comment="小类状态,0:失效，1：有效")
    create_time: Mapped[DateTime | None] = mapped_column(
        DateTime, nullable=True, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"
    )
    update_time: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        comment="更新时间",
    )
