from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

Base = declarative_base()

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


def get_session() -> AsyncSession:
    return AsyncSessionLocal()

async def init_db():
    # Create tables if not exist
    from app.models import connection  # noqa: F401 ensure models imported
    from app.models import server  # noqa: F401 ensure server table imported
    # Explicitly import dict models so their tables are registered with metadata
    from app.models.dict import DictCategory, DictItem  # noqa: F401
    print("[init_db] Creating tables if not exist...")
    try:
        print("[init_db] Registered tables:", list(Base.metadata.tables.keys()))
    except Exception as _e:
        print("[init_db] Unable to list metadata tables:", _e)
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            print("[init_db] create_all done.")
        except Exception as e:
            print(f"[init_db] create_all error: {e}")

    # Seed dictionary tables
    from sqlalchemy import select
    from sqlalchemy import inspect
    from sqlalchemy.exc import ProgrammingError

    # Double-check tables exist (defensive), create if missing
    async with engine.begin() as conn:
        def _check_and_create(sync_conn):
            insp = inspect(sync_conn)
            missing = []
            for t in ("t_dmlx", "t_dmmx"):
                if not insp.has_table(t):
                    missing.append(t)
            if missing:
                print(f"[init_db] Missing tables detected: {missing}, running create_all again...")
                Base.metadata.create_all(sync_conn)
        await conn.run_sync(_check_and_create)

    async with AsyncSessionLocal() as session:
        print("[init_db] Seeding dictionary tables...")
        # Seed categories
        categories = {
            "01": "数据源类型",
            "02": "数据库环境",
            "03": "数据源状态",
        }
        for dm, mc in categories.items():
            existing = await session.execute(select(DictCategory).where(DictCategory.dm == dm))
            if not existing.scalars().first():
                session.add(DictCategory(dm=dm, mc=mc, status="1"))

        # Seed items
        items = {
            "01": [
                ("0", "mysql"),
                ("1", "oracle"),
                ("2", "sqlserver"),
                ("3", "postgresql"),
                ("4", "mongodb"),
                ("5", "redis"),
                ("6", "elasticsearch"),
                ("7", "clickhouse"),
                ("8", "doris"),
            ],
            "02": [
                ("1", "生产环境"),
                ("2", "测试环境"),
                ("3", "开发环境"),
                ("4", "预生产环境"),
            ],
            "03": [
                ("0", "失效"),
                ("1", "有效"),
            ],
        }

        for dm, rows in items.items():
            for dmm, dmmc in rows:
                try:
                    existing = await session.execute(
                        select(DictItem).where(DictItem.dm == dm, DictItem.dmm == dmm)
                    )
                except ProgrammingError as e:
                    # Table might not exist yet; ensure create_all then retry once
                    print(f"[init_db] Select failed, ensuring tables exist: {e}")
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)
                    existing = await session.execute(
                        select(DictItem).where(DictItem.dm == dm, DictItem.dmm == dmm)
                    )
                if not existing.scalars().first():
                    session.add(DictItem(dm=dm, dmm=dmm, dmmc=dmmc, status="1"))

        await session.commit()
        print("[init_db] Seeding done.")
