# DataVerse 接口文档（API）

本项目的前后端约定接口汇总。以下说明以默认代理路径为基准（开发时前端经由 Vite 代理至后端）。如部署路径不同，请自行替换前缀。

- 所有示例均为简化示例，真实响应可能包含额外字段。
- 未特别说明时，方法为 GET；需要提交 SQL 时通常为 POST。

---

## 连接与库表相关

### 1) 获取连接列表
- URL: `/connections`
- Method: GET
- Query: 无
- Response 示例：
```json
[
  { "id": 1, "name": "dev-mysql-master" },
  { "id": 2, "name": "dev-mysql-slave" }
]
```

### 2) 获取某连接下的数据库列表（两种路径）
- URL-A: `/ticket/databases`（优先尝试）
  - Query: `connId=<number>` 或别名 `id=<number>`、`connectionId=<number>`
- URL-B: `/connections/{connId}/databases`（兜底）
- Response 示例：
```json
["hopsonone_members", "analytics", "test"]
```

### 3) 获取某库下的表列表
- URL: `/ticket/tables`
- Method: GET
- Query（支持多别名，任一可用）:
  - 连接：`connId` 或 `id`、`connectionId`
  - 库名：`db` 或 `database`、`schema`
- Response 示例：
```json
["members", "members_address", "members_behavior"]
```

### 4) 获取某表的列列表（优先使用 /api 路径）
- URL-优先: `/api/ticket/columns`
- URL-回退: `/ticket/columns`
- URL-REST兜底: `/connections/{connId}/databases/{db}/tables/{table}/columns`
- Method: GET
- Query（带全量别名，最大兼容）：
  - 连接：`connId`、`connectionId`、`conn_id`、`id`
  - 库名：`db`、`database`、`schema`
  - 表名：`table`、`tableName`、`tbl`
  - 其它：`format=json`（可选，若后端支持）
- Response（推荐）示例：
```json
["id", "m_id", "m_mobile", "create_time"]
```
- Response（对象数组）示例：
```json
[
  {"COLUMN_NAME": "id", "DATA_TYPE": "bigint", "COMMENT": "主键"},
  {"COLUMN_NAME": "m_mobile", "DATA_TYPE": "varchar", "COMMENT": "手机号"}
]
```

---

## SQL 执行与计划

### 5) 执行 SQL
- URL: `/ticket/execute` 或 `/api/ticket/execute`（视后端路由）
- Method: POST
- Body：
```json
{
  "connId": 1,
  "database": "hopsonone_members",  // 或省略，视后端
  "sql": "SELECT m.m_mobile FROM hopsonone_members.members m LIMIT 100;",
  "page": 1,
  "pageSize": 50
}
```
- Response 形态一（推荐）：
```json
{
  "data": [
    {"m_mobile": "13800000000"},
    {"m_mobile": "13900000000"}
  ],
  "columns": ["m_mobile"],
  "total": 444749,
  "page": 1,
  "pageSize": 50
}
```
- Response 形态二：
```json
{
  "rows": [
    {"m_id": 1, "m_mobile": "13800000000", "password": "..."}
  ],
  "columns": ["m_id", "m_mobile"],
  "totalRows": 444749
}
```
- Response 形态三（字符串）：
```json
"执行完成"
```

> 前端会优先按 `{data,columns}` 或 `{rows,columns}` 规范投影与渲染，严格按 `columns` 的顺序与字段集展示。

### 6) 查看执行计划（如后端提供）
- URL: `/ticket/plan`
- Method: POST
- Body：
```json
{ "connId": 1, "database": "hopsonone_members", "sql": "EXPLAIN SELECT ..." }
```
- Response：依后端实现。

---

## 参数别名与兼容性约定
- `connId` 可用别名：`id`、`connectionId`、`conn_id`
- `db` 可用别名：`database`、`schema`
- `table` 可用别名：`tableName`、`tbl`
- 若后端返回 Content-Type 非 `application/json`，前端会尝试以文本解析 JSON；若仍失败，将回退到 REST 路径。

---

## 错误与排查建议
- 404/页面 HTML：通常为路径不对或后端未提供该接口。
- 200 但无响应体：检查参数名是否匹配（尤其是 `connId/db/table`）或是否需要 `format=json`。
- 结果列不对：确认返回体是否携带 `columns`；若无 `columns`，前端会按 `rows[0]` 的键集推断。

---

## 连接管理（connections）

前缀（参考）：`/api/connections` 或由 `backend/app/api/routes/connections.py` 挂载位置决定。

1) 列表
- GET `/api/connections/`
- Resp: `ConnectionOut[]`

2) 新增
- POST `/api/connections/`
- Body: `ConnectionCreate`
- Resp: `ConnectionOut`

3) 查询
- GET `/api/connections/{conn_id}`
- Resp: `ConnectionOut`

4) 更新
- PUT `/api/connections/{conn_id}`
- Body: `ConnectionUpdate`
- Resp: `ConnectionOut`

5) 删除
- DELETE `/api/connections/{conn_id}`
- Resp: 204 No Content

6) 连通性测试
- POST `/api/connections/{conn_id}/test`
- Resp: `{ "success": true }` 或 4xx 错误

> 字段结构参考 `app/schemas/connection.py`。

---

## 主机管理（servers）

前缀（参考）：`/api/servers`

1) 列表
- GET `/api/servers/`

2) 新增
- POST `/api/servers/`

3) 查询
- GET `/api/servers/{server_id}`

4) 更新
- PUT `/api/servers/{server_id}`

5) 删除
- DELETE `/api/servers/{server_id}`

6) 连通性测试（TCP）
- POST `/api/servers/{server_id}/test`
- Resp: `{ "success": true }`

> 字段结构参考 `app/schemas/server.py`。

---

## 字典（dicts）

前缀：`/api/dicts`

1) 获取某字典项
- GET `/api/dicts/{dm}`
- Resp: `[{ dm, dmm, dmmc, status }]`

---

## SSH & SFTP

前缀：`/api/ssh`

1) WebSocket 终端
- WS `/api/ssh/ws?host=1.2.3.4&port=22&user=root&pass=xxx&auth=password`
- 额外支持：公钥方式 `auth=key&key_b64=<base64>`（可选 `key_pass`）
- 客户端可发送：
  - 终端输入数据（原样转发）
  - `__RESIZE__:120x32` 调整终端大小
  - `__PING__` 心跳（后端忽略）
- 服务端会在会话结束时发送：`{"type":"exit","code":<exit_status>}`

2) SFTP 列目录
- POST `/api/ssh/sftp/list`
- Form-Data：`host, port, user, auth=password|key, path=~|/var/log, password? , key_b64? , key_pass?`
- Resp：`[{ name, path, kind: 'file'|'directory', size?, mtime? }]`
- 行为：
  - 支持 `~` 与 `~/xxx`，会解析为家目录
  - 目录优先排序
  - 对个别系统编码问题，内置 `ls` 兜底解析

3) SFTP 上传
- POST `/api/ssh/sftp/upload`
- Form-Data：`file=<binary>` 以及与 list 相同连接字段，`path` 为目标目录（默认 `~`）
- Resp：`{ ok: true, path: "/remote/path/xxx" }`

4) SFTP 下载
- POST `/api/ssh/sftp/download`
- Form-Data：同上，`path` 为远端文件完整路径
- Resp：`application/octet-stream` 附件下载

> 服务器连接由 asyncssh 管理，已设置合理的连接与登录超时，确保前端不会长时间卡住。

---

## 统一返回结构（建议）

为便于前端统一处理，推荐后端（在不破坏现有接口的前提下）增加一个包裹层：

```json
// 成功
{
  "code": 0,
  "message": "ok",
  "data": { /* 原始 payload，例如 {data,columns,total,...} */ }
}

// 失败
{
  "code": 1001,
  "message": "连接不存在或不可用",
  "data": null
}
```

当前前端已向下兼容“裸返回”的 `{data,columns}` / `{rows,columns}` / `string` 等多种形态。

---

## cURL 示例

以下示例以 `connId=1`、数据库 `hopsonone_members`、表 `members` 为例：

1) 连接列表
```bash
curl -s http://127.0.0.1:5173/connections
```

2) 数据库列表
```bash
curl -s "http://127.0.0.1:5173/ticket/databases?connId=1"
# 兜底：
curl -s http://127.0.0.1:5173/connections/1/databases
```

3) 表列表
```bash
curl -s "http://127.0.0.1:5173/ticket/tables?connId=1&db=hopsonone_members"
```

4) 列列表（优先 /api 路径）
```bash
curl -s "http://127.0.0.1:5173/api/ticket/columns?connId=1&id=1&connectionId=1&db=hopsonone_members&database=hopsonone_members&schema=hopsonone_members&table=members&tableName=members&tbl=members&format=json"
```

5) 执行 SQL
```bash
curl -s -X POST http://127.0.0.1:5173/api/ticket/execute \
  -H "Content-Type: application/json" \
  -d '{
    "connId": 1,
    "database": "hopsonone_members",
    "sql": "SELECT m.m_mobile FROM hopsonone_members.members m LIMIT 10;",
    "page": 1,
    "pageSize": 50
  }'
```

---

## 常见错误排查（扩展）

- __[路径不对/代理未生效]__：浏览器直接打开接口返回的是 HTML 而非 JSON；请检查前端代理或后端实际监听路径。
- __[参数不兼容]__：`connId`/`id`/`connectionId`、`db`/`database`/`schema`、`table`/`tableName`/`tbl` 未覆盖到后端期望参数时会导致空结果。
- __[Content-Type 非 JSON]__：部分接口返回 `text/html` 或 `text/plain`，前端会尝试文本解析；如失败，回退 REST 路径。
- __[数据太大]__：建议分页（`page/pageSize`）或限制列，避免浏览器内存压力。
- __[权限/网络问题]__：关注 CORS、鉴权中间件、以及目标数据库网络连通性。

---

## 版本与变更
- 2025-09-17
  - 初版整理，补全 `/connections`、`/ticket/databases`、`/connections/{id}/databases`、`/ticket/tables`、`/api/ticket/columns`、`/ticket/execute` 等接口说明；
  - 明确参数别名与投影规则。
