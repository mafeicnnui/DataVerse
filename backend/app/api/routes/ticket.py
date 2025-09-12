from typing import List, Optional
import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.api.deps import get_db
from app.models.connection import Connection

router = APIRouter()


# Helpers
async def _get_conn_entity(conn_id: int, db: AsyncSession) -> Connection:
    entity = await db.get(Connection, conn_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Connection not found")
    return entity


async def _list_mysql_databases(entity: Connection) -> List[str]:
    import pymysql

    def _work():
        conn = pymysql.connect(
            host=entity.ip,
            port=int(entity.port),
            user=entity.user or "",
            password=entity.password or "",
            connect_timeout=5,
            cursorclass=pymysql.cursors.Cursor,
        )
        try:
            with conn.cursor() as cur:
                cur.execute("SHOW DATABASES")
                rows = cur.fetchall()
                return [r[0] for r in rows if isinstance(r, (list, tuple)) and r]
        finally:
            conn.close()

    return await asyncio.to_thread(_work)


async def _list_mysql_columns(entity: Connection, database: str, table: str) -> List[str]:
    import pymysql

    def _work():
        conn = pymysql.connect(
            host=entity.ip,
            port=int(entity.port),
            user=entity.user or "",
            password=entity.password or "",
            database=database,
            connect_timeout=5,
            cursorclass=pymysql.cursors.Cursor,
        )
        try:
            with conn.cursor() as cur:
                # 使用 information_schema 以兼容视图与表
                sql = (
                    "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s ORDER BY ORDINAL_POSITION"
                )
                cur.execute(sql, (database, table))
                rows = cur.fetchall()
                return [r[0] for r in rows if isinstance(r, (list, tuple)) and r]
        finally:
            conn.close()

    return await asyncio.to_thread(_work)


async def _list_mysql_tables(entity: Connection, database: str) -> List[str]:
    import pymysql

    def _work():
        conn = pymysql.connect(
            host=entity.ip,
            port=int(entity.port),
            user=entity.user or "",
            password=entity.password or "",
            database=database,
            connect_timeout=5,
            cursorclass=pymysql.cursors.Cursor,
        )
        try:
            with conn.cursor() as cur:
                cur.execute("SHOW TABLES")
                rows = cur.fetchall()
                # MySQL SHOW TABLES returns single-column rows
                return [r[0] for r in rows if isinstance(r, (list, tuple)) and r]
        finally:
            conn.close()

    return await asyncio.to_thread(_work)


# 1) /api/ticket/databases?connId=1 (含别名)
@router.get("/api/ticket/databases", response_model=List[str])
async def list_databases(
    conn_id_primary: Optional[int] = Query(default=None, alias="connId"),
    connection_id: Optional[int] = Query(default=None, alias="connectionId"),
    conn_id_snake: Optional[int] = Query(default=None, alias="conn_id"),
    id_aliased: Optional[int] = Query(default=None, alias="id"),
    db: AsyncSession = Depends(get_db),
):
    conn_id = conn_id_primary or connection_id or conn_id_snake or id_aliased
    if not conn_id:
        raise HTTPException(status_code=400, detail="connId is required")

    entity = await _get_conn_entity(conn_id, db)

    try:
        return await _list_mysql_databases(entity)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list databases: {e}")


# 2) /api/connections/{conn_id}/databases 便于前端回退
@router.get("/api/connections/{conn_id}/databases", response_model=List[str])
async def list_databases_by_path(conn_id: int, db: AsyncSession = Depends(get_db)):
    entity = await _get_conn_entity(conn_id, db)
    try:
        return await _list_mysql_databases(entity)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list databases: {e}")


# 3) /api/ticket/tables?connId=1&db=xxx (含别名 database/schema)
@router.get("/api/ticket/tables", response_model=List[str])
async def list_tables(
    conn_id_primary: Optional[int] = Query(default=None, alias="connId"),
    connection_id: Optional[int] = Query(default=None, alias="connectionId"),
    conn_id_snake: Optional[int] = Query(default=None, alias="conn_id"),
    id_aliased: Optional[int] = Query(default=None, alias="id"),
    db_name: Optional[str] = Query(default=None, alias="db"),
    database_name: Optional[str] = Query(default=None, alias="database"),
    schema_name: Optional[str] = Query(default=None, alias="schema"),
    db: AsyncSession = Depends(get_db),
):
    conn_id = conn_id_primary or connection_id or conn_id_snake or id_aliased
    if not conn_id:
        raise HTTPException(status_code=400, detail="connId is required")
    database = db_name or database_name or schema_name
    if not database:
        raise HTTPException(status_code=400, detail="database is required")

    entity = await _get_conn_entity(conn_id, db)

    try:
        return await _list_mysql_tables(entity, database)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list tables: {e}")


# 4) /api/connections/{conn_id}/tables?db=xxx 便于前端回退
@router.get("/api/connections/{conn_id}/tables", response_model=List[str])
async def list_tables_by_path(
    conn_id: int,
    db_name: Optional[str] = Query(default=None, alias="db"),
    database_name: Optional[str] = Query(default=None, alias="database"),
    schema_name: Optional[str] = Query(default=None, alias="schema"),
    db: AsyncSession = Depends(get_db),
):
    database = db_name or database_name or schema_name
    if not database:
        raise HTTPException(status_code=400, detail="database is required")

    entity = await _get_conn_entity(conn_id, db)

    try:
        return await _list_mysql_tables(entity, database)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list tables: {e}")


# 5) /api/ticket/columns?connId=1&db=xxx&table=yyy
@router.get("/api/ticket/columns", response_model=List[str])
async def list_columns(
    conn_id_primary: Optional[int] = Query(default=None, alias="connId"),
    connection_id: Optional[int] = Query(default=None, alias="connectionId"),
    conn_id_snake: Optional[int] = Query(default=None, alias="conn_id"),
    id_aliased: Optional[int] = Query(default=None, alias="id"),
    db_name: Optional[str] = Query(default=None, alias="db"),
    database_name: Optional[str] = Query(default=None, alias="database"),
    schema_name: Optional[str] = Query(default=None, alias="schema"),
    table_name: Optional[str] = Query(default=None, alias="table"),
    table2_name: Optional[str] = Query(default=None, alias="tableName"),
    t_name: Optional[str] = Query(default=None, alias="tbl"),
    db: AsyncSession = Depends(get_db),
):
    conn_id = conn_id_primary or connection_id or conn_id_snake or id_aliased
    if not conn_id:
        raise HTTPException(status_code=400, detail="connId is required")
    database = db_name or database_name or schema_name
    if not database:
        raise HTTPException(status_code=400, detail="database is required")
    table = table_name or table2_name or t_name
    if not table:
        raise HTTPException(status_code=400, detail="table is required")

    entity = await _get_conn_entity(conn_id, db)

    try:
        return await _list_mysql_columns(entity, database, table)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list columns: {e}")


# ===================== 执行与执行计划 =====================
class ExecuteRequest(BaseModel):
    connId: Optional[int] = None
    connectionId: Optional[int] = None
    conn_id: Optional[int] = None
    id: Optional[int] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    db: Optional[str] = None
    sql: str
    # 后端分页参数（可选）
    page: Optional[int] = None
    pageSize: Optional[int] = None
    # 是否尊重 SQL 内置的 LIMIT/OFFSET（直通模式）。为 True 时不做后端分页、计数与外提 ORDER BY。
    respectInnerLimit: Optional[bool] = False


def _get_first_nonempty_sql(sql: str) -> str:
    # 取第一条非空语句
    parts = [p.strip() for p in (sql or '').split(';')]
    for p in parts:
        if p:
            return p
    return (sql or '').strip()


@router.post("/api/ticket/execute")
async def execute_sql(payload: ExecuteRequest, db: AsyncSession = Depends(get_db)):
    import pymysql
    from pymysql.cursors import DictCursor
    import re

    conn_id = payload.connId or payload.connectionId or payload.conn_id or payload.id
    if not conn_id:
        raise HTTPException(status_code=400, detail="connId is required")
    if not payload.sql or not str(payload.sql).strip():
        raise HTTPException(status_code=400, detail="sql is required")

    entity = await _get_conn_entity(conn_id, db)

    def _work():
        conn = pymysql.connect(
            host=entity.ip,
            port=int(entity.port),
            user=entity.user or "",
            password=entity.password or "",
            database=payload.database or payload.schema or payload.db or None,
            connect_timeout=10,
            cursorclass=DictCursor,
            autocommit=True,
        )
        try:
            with conn.cursor() as cur:
                raw = _get_first_nonempty_sql(payload.sql)
                # 去掉开头的注释与空行，避免 '-- xxx' 开头导致无法识别为 SELECT
                def _strip_leading_comments(s: str) -> str:
                    try:
                        s2 = s.lstrip()
                        # 连续去除前缀的块注释与行注释
                        changed = True
                        while changed:
                            changed = False
                            # 块注释
                            if re.match(r"(?is)^/\*", s2):
                                m = re.match(r"(?is)^/\*.*?\*/", s2)
                                if m:
                                    s2 = s2[m.end():].lstrip()
                                    changed = True
                                    continue
                            # 行注释
                            if re.match(r"(?im)^--.*$", s2):
                                s2 = re.sub(r"(?im)^--.*$\n?", "", s2, count=1).lstrip()
                                changed = True
                                continue
                        return s2
                    except Exception:
                        return s

                raw_clean = _strip_leading_comments(raw)
                upper = raw_clean.strip().upper()
                # 仅对 SELECT 语句做分页与总数
                if upper.startswith("SELECT"):
                    # 直通模式：尊重 SQL 内置 LIMIT/OFFSET，不做后端分页/计数/ORDER BY 外提
                    if payload.respectInnerLimit:
                        try:
                            # 去掉尾部分号，防止部分驱动因分号报错
                            direct_sql = re.sub(r"(?is)\s*;\s*$", "", raw_clean)
                        except Exception:
                            direct_sql = raw_clean
                        cur.execute(direct_sql)
                        columns = [c[0] for c in cur.description] if cur.description else []
                        rows = cur.fetchall()
                        total = len(rows) if isinstance(rows, list) else (len(rows) if rows else 0)
                        return {"columns": columns, "rows": rows, "totalRows": total}

                    # 去掉尾部 LIMIT/OFFSET 与多余分号/注释，避免影响总数（尽量覆盖常见写法）
                    tmp = re.sub(r"(?is)\s*;\s*$", "", raw_clean)  # 去掉末尾分号
                    tmp = re.sub(r"(?im)\s*--.*$", "", tmp)   # 去掉行尾注释
                    tmp = re.sub(r"(?is)/\*.*?\*/", "", tmp) # 去掉块注释
                    # 先移除末尾 LIMIT/OFFSET
                    tmp2 = re.sub(r"(?is)\s+limit\s+\d+(\s*,\s*\d+|\s+offset\s+\d+)?\s*$", "", tmp)
                    # 提取并外提末尾 ORDER BY（若存在），计数用去掉 ORDER BY 的子查询，分页在外层加 ORDER BY
                    order_by_clause = ""
                    order_iter = list(re.finditer(r"(?is)\border\s+by\b", tmp2))
                    if order_iter:
                        last_ob = order_iter[-1]
                        tail = tmp2[last_ob.start():].strip()
                        # 确认 tail 仅为 ORDER BY 子句（不含其他关键字），简单兜底：直接作为外层 ORDER BY 使用
                        order_by_clause = tail  # 形如 'ORDER BY id, name DESC'
                        raw_base = tmp2[:last_ob.start()].rstrip()
                    else:
                        raw_base = tmp2

                    page = int(payload.page or 1)
                    page_size = int(payload.pageSize or 50)
                    if page <= 0:
                        page = 1
                    if page_size <= 0:
                        page_size = 50
                    offset = (page - 1) * page_size

                    # 计算总数
                    count_sql = f"SELECT COUNT(*) AS total FROM ({raw_base}) AS _t"
                    cur.execute(count_sql)
                    total_row = cur.fetchone()
                    total = int(total_row[0] if isinstance(total_row, (list, tuple)) else total_row.get('total', 0))

                    # 分页查询（MySQL 支持 LIMIT size OFFSET offset 或 LIMIT offset, size）
                    outer_order = f" {order_by_clause} " if order_by_clause else " "
                    page_sql = f"SELECT * FROM ({raw_base}) AS _t{outer_order}LIMIT %s OFFSET %s"
                    try:
                        cur.execute(page_sql, (page_size, offset))
                    except Exception:
                        # 回退写法：LIMIT offset, size
                        page_sql = f"SELECT * FROM ({raw_base}) AS _t{outer_order}LIMIT %s, %s"
                        cur.execute(page_sql, (offset, page_size))
                    columns = [c[0] for c in cur.description] if cur.description else []
                    rows = cur.fetchall()
                    return {"columns": columns, "rows": rows, "totalRows": total, "pageEcho": page, "pageSizeEcho": page_size}
                else:
                    # 非 SELECT，按原样执行
                    cur.execute(raw)
                    if cur.description:
                        columns = [c[0] for c in cur.description]
                        rows = cur.fetchall()
                        return {"columns": columns, "rows": rows}
                    return {"message": f"OK, affected {cur.rowcount} rows"}
        finally:
            conn.close()

    try:
        return await asyncio.to_thread(_work)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Execute failed: {e}")


@router.post("/api/ticket/plan")
async def view_plan(payload: ExecuteRequest, db: AsyncSession = Depends(get_db)):
    import pymysql
    from pymysql.cursors import DictCursor

    conn_id = payload.connId or payload.connectionId or payload.conn_id or payload.id
    if not conn_id:
        raise HTTPException(status_code=400, detail="connId is required")
    if not payload.sql or not str(payload.sql).strip():
        raise HTTPException(status_code=400, detail="sql is required")

    entity = await _get_conn_entity(conn_id, db)

    def _work():
        conn = pymysql.connect(
            host=entity.ip,
            port=int(entity.port),
            user=entity.user or "",
            password=entity.password or "",
            database=payload.database or payload.schema or payload.db or None,
            connect_timeout=10,
            cursorclass=DictCursor,
            autocommit=True,
        )
        try:
            with conn.cursor() as cur:
                raw = _get_first_nonempty_sql(payload.sql)
                sql_plan = raw if raw.strip().upper().startswith("EXPLAIN") else f"EXPLAIN {raw}"
                cur.execute(sql_plan)
                if cur.description:
                    columns = [c[0] for c in cur.description]
                    rows = cur.fetchall()
                    return {"columns": columns, "rows": rows}
                return {"message": "No plan output"}
        finally:
            conn.close()

    try:
        return await asyncio.to_thread(_work)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Plan failed: {e}")
