from typing import List
import socket

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.api.deps import get_db
from app.models.server import Server
from app.schemas.server import ServerCreate, ServerOut, ServerUpdate

router = APIRouter()


@router.get("/", response_model=List[ServerOut])
async def list_servers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server))
    rows = result.scalars().all()
    return rows


@router.post("/", response_model=ServerOut, status_code=status.HTTP_201_CREATED)
async def create_server(payload: ServerCreate, db: AsyncSession = Depends(get_db)):
    entity = Server(
        server_desc=payload.server_desc,
        server_ip=payload.server_ip,
        server_port=payload.server_port,
        server_user=payload.server_user,
        server_pass=payload.server_pass,
        auth_memthod=payload.auth_memthod,
        server_os=payload.server_os,
        status=payload.status,
        creator=payload.creator,
        updator=payload.updator,
    )
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


@router.get("/{server_id}", response_model=ServerOut)
async def get_server(server_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.get(Server, server_id)
    if not res:
        raise HTTPException(status_code=404, detail="Server not found")
    return res


@router.put("/{server_id}", response_model=ServerOut)
async def update_server(server_id: int, payload: ServerUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.get(Server, server_id)
    if not res:
        raise HTTPException(status_code=404, detail="Server not found")

    data = payload.model_dump(exclude_unset=True)
    await db.execute(update(Server).where(Server.id == server_id).values(**data))
    await db.commit()
    await db.refresh(res)
    return res


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(server_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.get(Server, server_id)
    if not res:
        raise HTTPException(status_code=404, detail="Server not found")
    await db.execute(delete(Server).where(Server.id == server_id))
    await db.commit()
    return None


@router.post("/{server_id}/test")
async def test_server(server_id: int, db: AsyncSession = Depends(get_db)):
    entity = await db.get(Server, server_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Server not found")

    try:
        host = entity.server_ip
        port = int(entity.server_port)
        ok = _test_tcp(host, port, timeout=5)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {e}")

    return {"success": ok}


def _test_tcp(host: str, port: int, timeout: float = 5.0) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True
    finally:
        try:
            sock.close()
        except Exception:
            pass
