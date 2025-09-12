from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.dict import DictItem

router = APIRouter(prefix="/api/dicts", tags=["dicts"])


@router.get("/{dm}")
async def get_dict_items(dm: str, db: AsyncSession = Depends(get_db)):
    stmt = select(DictItem).where(DictItem.dm == dm, DictItem.status == "1").order_by(DictItem.dmm)
    res = await db.execute(stmt)
    items = [
        {"dm": r.dm, "dmm": r.dmm, "dmmc": r.dmmc, "status": r.status}
        for r in res.scalars().all()
    ]
    return items
