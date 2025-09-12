from typing import List, Optional
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.api.deps import get_db
from app.models.connection import Connection
from app.schemas.connection import ConnectionCreate, ConnectionOut, ConnectionUpdate

router = APIRouter()


@router.get("/", response_model=List[ConnectionOut])
async def list_connections(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Connection))
    rows = result.scalars().all()
    return rows


@router.post("/", response_model=ConnectionOut, status_code=status.HTTP_201_CREATED)
async def create_connection(payload: ConnectionCreate, db: AsyncSession = Depends(get_db)):
    conn = Connection(
        ip=payload.ip,
        port=payload.port,
        user=payload.user,
        password=payload.password,
        db_type=payload.db_type,
        db_env=payload.db_env,
        description=payload.description,
        status=payload.status,
        creator=payload.creator,
    )
    db.add(conn)
    await db.commit()
    await db.refresh(conn)
    return conn


@router.get("/{conn_id}", response_model=ConnectionOut)
async def get_connection(conn_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.get(Connection, conn_id)
    if not res:
        raise HTTPException(status_code=404, detail="Connection not found")
    return res


@router.put("/{conn_id}", response_model=ConnectionOut)
async def update_connection(conn_id: int, payload: ConnectionUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.get(Connection, conn_id)
    if not res:
        raise HTTPException(status_code=404, detail="Connection not found")

    data = payload.model_dump(exclude_unset=True)
    await db.execute(update(Connection).where(Connection.id == conn_id).values(**data))
    await db.commit()
    await db.refresh(res)
    return res


@router.delete("/{conn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(conn_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.get(Connection, conn_id)
    if not res:
        raise HTTPException(status_code=404, detail="Connection not found")
    await db.execute(delete(Connection).where(Connection.id == conn_id))
    await db.commit()
    return None


@router.post("/{conn_id}/test")
async def test_connection(conn_id: int, db: AsyncSession = Depends(get_db)):
    entity = await db.get(Connection, conn_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Connection not found")

    try:
        ok = await _test_mysql(
            host=entity.ip,
            port=int(entity.port),
            user=entity.user or "",
            password=entity.password,
            database=None,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {e}")

    return {"success": ok}


async def _test_mysql(host: str, port: int, user: str, password: str, database: Optional[str]):
    import pymysql

    def _connect():
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database or None,
            connect_timeout=5,
            cursorclass=pymysql.cursors.Cursor,
        )
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        conn.close()
        return True

    return await asyncio.to_thread(_connect)
