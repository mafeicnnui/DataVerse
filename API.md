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

## 版本与变更
- 2025-09-17
  - 初版整理，补全 `/connections`、`/ticket/databases`、`/connections/{id}/databases`、`/ticket/tables`、`/api/ticket/columns`、`/ticket/execute` 等接口说明；
  - 明确参数别名与投影规则。
