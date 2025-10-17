from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.websockets import WebSocketState
import asyncio
import re
import asyncssh
import base64
import json
from typing import Optional
import shlex
import stat
from io import BytesIO

router = APIRouter(prefix="/api/ssh", tags=["ssh"])

async def _ssh_handler(ws: WebSocket, host: str, port: int, username: str, password: str, auth: str = 'password', key_b64: Optional[str] = None, key_pass: Optional[str] = None, init_cols: int = 120, init_rows: int = 32):
    conn = None
    proc = None
    try:
        await ws.accept()
        connect_kwargs = dict(
            host=host,
            port=port,
            username=username,
            known_hosts=None,
            preferred_auth=['publickey', 'keyboard-interactive', 'password'],
        )
        if (auth or '').lower() == 'key':
            client_keys = None
            if key_b64:
                try:
                    key_data = base64.b64decode(key_b64)
                    client_keys = [asyncssh.import_private_key(key_data, passphrase=key_pass or None)]
                except Exception as e:
                    await ws.send_text(f"\r\n[ERROR] KeyLoadError: {e}\r\n")
                    await ws.close()
                    return
            connect_kwargs.update(dict(client_keys=client_keys, password=None))
        else:
            connect_kwargs.update(dict(password=password))

        # 避免连接/登录长时间挂起
        connect_kwargs.update(dict(connect_timeout=10, login_timeout=10))
        conn = await asyncssh.connect(**connect_kwargs)
        # 使用 create_process 打开交互式 shell，并分离 stdin/stdout/stderr，便于转发
        # 优先显式启动登录 shell，部分环境默认不回显提示符
        proc = None
        try:
            proc = await conn.create_process(command='/bin/bash -l', term_type='xterm-256color', term_size=(init_cols or 120, init_rows or 32))
        except Exception:
            try:
                proc = await conn.create_process(command='/bin/sh -l', term_type='xterm-256color', term_size=(init_cols or 120, init_rows or 32))
            except Exception:
                # 兜底：不指定命令，使用远端默认 shell
                proc = await conn.create_process(term_type='xterm-256color', term_size=(init_cols or 120, init_rows or 32))
        # 不再在连接后主动发送回车，避免产生额外的空行/重复提示符

        async def from_client():
            while True:
                try:
                    msg = await ws.receive_text()
                except asyncio.CancelledError:
                    break
                except WebSocketDisconnect:
                    break
                except Exception:
                    break
                if msg is None:
                    break
                # 支持前端 resize 指令：{"type":"resize","cols":120,"rows":30}
                if msg.startswith("__RESIZE__:"):
                    try:
                        payload = msg.split(":", 1)[1]
                        cols, rows = map(int, payload.split("x"))
                        if proc:
                            await proc.resize_pty(cols, rows)
                    except Exception:
                        pass
                else:
                    # 丢弃前端心跳标记，避免出现在远端终端里（如 __PING__）
                    if msg == "__PING__":
                        continue
                    try:
                        if proc and not proc.stdin.is_closing():
                            proc.stdin.write(msg)
                    except Exception:
                        break

        async def pump_stream(reader):
            while True:
                try:
                    data = await reader.read(4096)
                except asyncio.CancelledError:
                    # 任务被上层取消时安静退出
                    return
                except Exception:
                    break
                if not data:
                    break
                if ws.application_state == WebSocketState.DISCONNECTED:
                    break
                try:
                    await ws.send_text(data)
                except asyncio.CancelledError:
                    return
                except (WebSocketDisconnect, RuntimeError, Exception):
                    break

        # 认证已通过 connect 时的 auth_methods/password/client_keys 处理完成，无需额外设置

        t1 = asyncio.create_task(from_client())
        t_out = asyncio.create_task(pump_stream(proc.stdout))
        t_err = asyncio.create_task(pump_stream(proc.stderr))
        # 仅当“客户端方向结束”或“stdout 与 stderr 都结束”时再继续
        t_io = asyncio.gather(t_out, t_err, return_exceptions=True)
        done, pending = await asyncio.wait({t1, t_io}, return_when=asyncio.FIRST_COMPLETED)
        # 任一结束后，取消另一个，避免在关闭后继续发送
        for p in pending:
            try:
                p.cancel()
            except Exception:
                pass
        # 吞掉取消异常，确保干净退出
        for d in done:
            try:
                _ = d.result()
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
        # 进一步清理底层子任务，确保不遗留未检索异常
        try:
            await asyncio.gather(t_out, t_err, return_exceptions=True)
        except Exception:
            pass

        # 会话走到这里基本意味着前后任一方向已结束，尽量向前端发送退出消息
        try:
            if ws.application_state != WebSocketState.DISCONNECTED:
                exit_code = None
                try:
                    # asyncssh Process 常见为 exit_status 属性
                    exit_code = getattr(proc, 'exit_status', None)
                except Exception:
                    exit_code = None
                try:
                    await ws.send_text(json.dumps({"type": "exit", "code": exit_code}))
                finally:
                    try:
                        await ws.close(code=1000)
                    except Exception:
                        pass
        except Exception:
            pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        # 尝试提供更详细的错误提示
        detail = str(e)
        if ws.application_state != WebSocketState.DISCONNECTED:
            try:
                await ws.send_text(f"[ERROR] {type(e).__name__}: {detail}")
            except Exception:
                pass
    finally:
        try:
            if proc:
                proc.close()
                try:
                    proc.stdin.close()
                except Exception:
                    pass
                try:
                    proc.kill()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        try:
            if ws.application_state != WebSocketState.DISCONNECTED:
                await ws.close()
        except Exception:
            pass

@router.websocket('/ws')
async def ssh_ws(ws: WebSocket):
    # query: host, port, user, pass
    q = ws.query_params
    host = q.get('host')
    port = int(q.get('port') or 22)
    username = q.get('user')
    password = q.get('pass')
    auth = q.get('auth') or 'password'
    key_b64 = q.get('key_b64')
    key_pass = q.get('key_pass')
    # 初始终端尺寸（可选）
    try:
        init_cols = int(q.get('cols') or 120)
    except Exception:
        init_cols = 120
    try:
        init_rows = int(q.get('rows') or 32)
    except Exception:
        init_rows = 32
    if not host or not username:
        await ws.accept()
        await ws.send_text('[ERROR] missing host/user')
        await ws.close()
        return
    await _ssh_handler(ws, host, port, username, password or '', auth=auth, key_b64=key_b64, key_pass=key_pass, init_cols=init_cols, init_rows=init_rows)

# ========== SFTP 辅助：建立一次性连接并返回 conn 与 sftp ==========
async def _connect_sftp(host: str, port: int, username: str, password: str = '', auth: str = 'password', key_b64: Optional[str] = None, key_pass: Optional[str] = None):
    connect_kwargs = dict(
        host=host,
        port=port,
        username=username,
        known_hosts=None,
        preferred_auth=['publickey', 'keyboard-interactive', 'password'],
    )
    if (auth or '').lower() == 'key':
        client_keys = None
        if key_b64:
            key_data = base64.b64decode(key_b64)
            client_keys = [asyncssh.import_private_key(key_data, passphrase=key_pass or None)]
        connect_kwargs.update(dict(client_keys=client_keys, password=None))
    else:
        connect_kwargs.update(dict(password=password))
    # 连接/登录超时，避免前端长时间无响应
    connect_kwargs.update(dict(connect_timeout=10, login_timeout=10))
    conn = await asyncssh.connect(**connect_kwargs)
    # 兼容当前环境的 asyncssh 版本（不支持 encoding/errors 参数）
    sftp = await conn.start_sftp_client()
    return conn, sftp

def _is_dir_from_attrs(attrs) -> bool:
    try:
        mode = getattr(attrs, 'permissions', None)
        if mode is None:
            return False
        return stat.S_ISDIR(mode)
    except Exception:
        return False

def _join_path(parent: str, name: str) -> str:
    if not parent:
        parent = '.'
    if parent.endswith('/'):
        return parent + name
    return parent + '/' + name

async def _mkdir_p(sftp, path: str):
    # 基于 / 分割逐级创建，忽略已存在错误
    if not path or path in ('.', '~'):
        return
    parts = [p for p in path.split('/') if p]
    cur = ''
    for p in parts:
        cur = _join_path(cur or '/', p) if cur else ('/' + p if path.startswith('/') else p)
        try:
            await sftp.mkdir(cur)
        except asyncssh.SFTPError:
            # 已存在则忽略
            try:
                await sftp.stat(cur)
            except Exception:
                raise

@router.post('/sftp/list')
async def sftp_list(
    host: str = Form(...),
    port: int = Form(22),
    user: str = Form(...),
    auth: str = Form('password'),
    path: str = Form('~'),
    password: Optional[str] = Form(''),
    key_b64: Optional[str] = Form(None),
    key_pass: Optional[str] = Form(None),
):
    conn = None
    try:
        conn, sftp = await _connect_sftp(host, port, user, password or '', auth, key_b64, key_pass)
        # 处理 ~ 路径
        p = path or '.'
        p = str(p).strip()
        # 规范化路径：支持 ~ 与 ~/xxx
        try:
            home = await sftp.getcwd()
        except Exception:
            home = None
        if p == '~' and home:
            p = home
        elif p.startswith('~/') and home:
            p = home.rstrip('/') + '/' + p[2:]
        # 将多个斜杠规范为单个
        p = re.sub(r'/+', '/', p)
        # 列出目录
        items = []
        try:
            names = await sftp.readdir(p)
        except FileNotFoundError:
            # 明确路径不存在
            raise HTTPException(status_code=404, detail=f'remote path not found: {p}')
        except asyncssh.SFTPError as e:
            # 对包含解码相关错误的情况，尝试使用 shell 方式兜底列目录
            msg = str(e)
            if 'unable to decode' in msg.lower() or 'decode' in msg.lower():
                try:
                    cmd = f"LC_ALL=C ls -lAp --time-style=+%s {shlex.quote(p)}"
                    res = await conn.run(cmd, check=False, encoding=None)
                    if res.exit_status == 0 and res.stdout:
                        items = []
                        for raw in res.stdout.splitlines():
                            try:
                                line = raw.strip()
                                if not line or line.startswith(b'total'):
                                    continue
                                # 拆分出 8 段（权限/链接/用户/组/大小/时间/名称），名称可能包含空格
                                parts = line.split(None, 7)
                                if len(parts) < 8:
                                    continue
                                perm, _links, _owner, _group, size_b, mtime_b, _tz_or_more, name_b = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7]
                                # 有的系统 time-style 会把时间分成两列，尝试兼容
                                try:
                                    mtime = int(mtime_b.decode('ascii', 'ignore'))
                                except Exception:
                                    # 若被分列，则向后合并一列再解析
                                    try:
                                        mtime = int((mtime_b + b" " + parts[6]).decode('ascii', 'ignore'))
                                    except Exception:
                                        mtime = None
                                try:
                                    size = int(size_b.decode('ascii', 'ignore'))
                                except Exception:
                                    size = None
                                name = name_b.decode('utf-8', 'surrogateescape')
                                kind = 'directory' if (perm.startswith(b'd') or name.endswith('/')) else 'file'
                                # 去掉目录名末尾的 /
                                if kind == 'directory' and name.endswith('/'):
                                    name = name[:-1]
                                items.append({
                                    'name': name,
                                    'path': _join_path(p, name),
                                    'kind': kind,
                                    'size': size,
                                    'mtime': mtime,
                                })
                            except Exception:
                                # 跳过无法解析的行
                                continue
                        # 目录优先排序
                        items.sort(key=lambda x: (0 if x['kind']=='directory' else 1, x['name']))
                        return JSONResponse(items)
                    # 如果 -lAp 不可用或输出为空，尝试仅名称列表（兼容 BusyBox 等）
                    cmd2 = f"LC_ALL=C ls -1Ap {shlex.quote(p)}"
                    res2 = await conn.run(cmd2, check=False, encoding=None)
                    if res2.exit_status == 0 and res2.stdout is not None:
                        items = []
                        for raw in res2.stdout.splitlines():
                            try:
                                name = raw.decode('utf-8', 'surrogateescape').strip()
                                if not name:
                                    continue
                                kind = 'directory' if name.endswith('/') else 'file'
                                if kind == 'directory' and name.endswith('/'):
                                    name = name[:-1]
                                items.append({
                                    'name': name,
                                    'path': _join_path(p, name),
                                    'kind': kind,
                                    'size': None,
                                    'mtime': None,
                                })
                            except Exception:
                                continue
                        items.sort(key=lambda x: (0 if x['kind']=='directory' else 1, x['name']))
                        return JSONResponse(items)
                except Exception:
                    pass
            # 其它错误：权限不足/不是目录/受限等，透传
            raise HTTPException(status_code=403, detail=f'sftp list failed: {p}: {msg}')
        for it in names:
            attrs = getattr(it, 'attrs', None)
            kind = 'directory' if _is_dir_from_attrs(attrs) else 'file'
            # 提取尺寸与修改时间（如可用），用于前端展示与排序
            size = None
            mtime = None
            try:
                size = getattr(attrs, 'size', None)
            except Exception:
                size = None
            try:
                # asyncssh SFTP attrs 常见字段 mtime（int 秒）
                mtime = getattr(attrs, 'mtime', None)
            except Exception:
                mtime = None
            items.append({
                'name': it.filename,
                'path': _join_path(p, it.filename) if p != '.' else it.filename,
                'kind': kind,
                'size': size,
                'mtime': mtime,
            })
        # 目录优先排序
        items.sort(key=lambda x: (0 if x['kind']=='directory' else 1, x['name']))
        return JSONResponse(items)
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

@router.post('/sftp/upload')
async def sftp_upload(
    file: UploadFile = File(...),
    host: str = Form(...),
    port: int = Form(22),
    user: str = Form(...),
    auth: str = Form('password'),
    path: str = Form('~'),
    password: Optional[str] = Form(''),
    key_b64: Optional[str] = Form(None),
    key_pass: Optional[str] = Form(None),
):
    conn = None
    try:
        conn, sftp = await _connect_sftp(host, port, user, password or '', auth, key_b64, key_pass)
        # 目标目录，规范化 ~ 与 ~/xxx
        target_dir = path or '.'
        target_dir = str(target_dir).strip()
        try:
            home = await sftp.getcwd()
        except Exception:
            home = None
        if target_dir == '~' and home:
            target_dir = home
        elif target_dir.startswith('~/') and home:
            target_dir = home.rstrip('/') + '/' + target_dir[2:]
        # 折叠多余斜杠
        target_dir = re.sub(r'/+', '/', target_dir)
        # 确保目标目录存在
        try:
            await sftp.stat(target_dir)
        except Exception:
            await _mkdir_p(sftp, target_dir)
        remote_path = _join_path(target_dir, file.filename)
        # 二进制写入
        try:
            async with sftp.open(remote_path, 'wb') as f:
                while True:
                    chunk = await file.read(1024*256)
                    if not chunk:
                        break
                    await f.write(chunk)
        except asyncssh.SFTPError as e:
            raise HTTPException(status_code=500, detail=f'sftp write error: {e}')
        return {'ok': True, 'path': remote_path}
    finally:
        try:
            await file.close()
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass

@router.post('/sftp/download')
async def sftp_download(
    host: str = Form(...),
    port: int = Form(22),
    user: str = Form(...),
    auth: str = Form('password'),
    path: str = Form(...),
    password: Optional[str] = Form(''),
    key_b64: Optional[str] = Form(None),
    key_pass: Optional[str] = Form(None),
):
    conn = None
    try:
        conn, sftp = await _connect_sftp(host, port, user, password or '', auth, key_b64, key_pass)
        # 规范化下载路径：支持 ~ 与 ~/xxx
        dl_path = str(path or '').strip()
        try:
            home = await sftp.getcwd()
        except Exception:
            home = None
        if dl_path == '~' and home:
            dl_path = home
        elif dl_path.startswith('~/') and home:
            dl_path = home.rstrip('/') + '/' + dl_path[2:]
        dl_path = re.sub(r'/+', '/', dl_path)
        async def file_iter():
            async with sftp.open(dl_path, 'r') as f:
                while True:
                    data = await f.read(1024*256)
                    if not data:
                        break
                    yield data
        filename = dl_path.split('/')[-1] or 'download.bin'
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        return StreamingResponse(file_iter(), media_type='application/octet-stream', headers=headers)
    except asyncssh.SFTPError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (asyncio.TimeoutError, asyncssh.Error) as e:
        raise HTTPException(status_code=504, detail=f'sftp download timeout/ssh error: {e}')
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
