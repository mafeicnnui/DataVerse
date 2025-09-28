## API 文档

更完整的后端接口使用说明请参见 [`API.md`](./API.md)。

# Data Verse 星域运维平台

一个包含 FastAPI 后端与 Vue 3 前端的全栈项目，用于数据库与主机统一运维：

- 连接管理（MySQL）：新增/修改/删除/列表/连通性测试
- 主机管理：WebSSH 控制台、多标签会话、最小化与右下角气泡还原、SFTP 文件传输
- SQL 控制台：与连接管理联动，支持全屏浮窗、数据库/表树、SQL 编辑/执行、结果导出

后端使用 MySQL 存储连接与主机信息（SQLAlchemy 异步引擎 + aiomysql），并提供 RESTful + WebSocket（SSH）接口；前端基于 Vite + Vue 3，实现控制台与文件传输等交互。

---

## 快速开始
- 连接管理（MySQL）
  - 新增、查询、更新、删除
  - 连通性测试（PyMySQL）![alt text](image.png)
- 主机管理（SSH）
  - WebSSH 控制台（xterm.js + FastAPI WebSocket）
  - 多标签会话、重连、最小化到气泡、从气泡一键还原
  - SFTP 文件传输（上传/下载、进度/日志、历史与排序）
- SQL 控制台
  - 全屏浮窗布局、数据库/表树、编辑器自动补全
  - 执行/停止/导出 CSV/Excel、分页与排序
  - 支持新窗口打开与 URL 直达、按标签页绑定连接、标签悬浮显示连接描述
- RESTful API + Swagger `/docs`
- CORS 已开启，默认允许 `http://localhost:5173`

---

> 文档导航：如果你只需查看后端/前端交互接口，请直接查看：[`API.md`](./API.md)

#- [快速开始](#快速开始)
- [目录结构（精简）](#项目结构)
- [API 文档](#api-文档)

## 功能特性
- 连接管理（MySQL）
  - 新增、查询、更新、删除
  - 连通性测试（PyMySQL）![alt text](image.png)
- 主机管理（SSH）
  - WebSSH 控制台（xterm.js + FastAPI WebSocket）
  - 多标签会话、重连、最小化到气泡、从气泡一键还原
  - SFTP 文件传输（上传/下载、进度/日志、历史与排序）
- SQL 控制台
  - 全屏浮窗布局、数据库/表树、编辑器自动补全
  - 执行/停止/导出 CSV/Excel、分页与排序
  - 支持新窗口打开与 URL 直达、按标签页绑定连接、标签悬浮显示连接描述
- RESTful API + Swagger `/docs`
- CORS 已开启，默认允许 `http://localhost:5173`

---

## 项目结构
（精简）
```
./
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  │  ├─ deps.py
│  │  │  └─ routes/
│  │  │     ├─ connections.py   # 连接管理 CRUD + 测试
│  │  │     ├─ servers.py       # 主机管理 CRUD + 测试
│  │  │     ├─ dicts.py         # 字典（类型/环境/状态等）
│  │  │     ├─ ticket.py        # SQL 控制台（表/列等数据）
│  │  │     └─ ssh.py           # WebSSH(WS) 与 SFTP（list/upload/download）
│  │  ├─ core/
│  │  │  └─ config.py           # 配置与环境变量
│  │  ├─ db/
│  │  │  └─ base.py
│  │  ├─ models/
│  │  │  ├─ connection.py       # ORM: t_db_source
│  │  │  └─ server.py           # ORM: t_server
│  │  ├─ schemas/
│  │  │  ├─ connection.py
│  │  │  └─ server.py
│  │  └─ main.py                # FastAPI 入口（包含 CORS、中间件与路由）
│  └─ requirements.txt
├─ frontend/
│  ├─ index.html
│  ├─ package.json
│  ├─ vite.config.js            # /api 代理到后端
│  └─ src/
│     ├─ api.js                 # axios 封装（baseURL=/api）
│     ├─ App.vue                # 主界面：侧边导航、工单/连接/主机等
│     ├─ components/
│     │  ├─ conn/               # 连接管理（表格/表单/工具条）
│     │  ├─ server/HostManager.vue    # 主机管理列表与入口
│     │  └─ console/            # 控制台相关
│     │     ├─ ConsoleManager.vue      # 控制台窗口（多标签 SSH/FTP）
│     │     ├─ ConsoleBubbles.vue      # 右下角最小化气泡
│     │     ├─ WebSSH.vue              # WebSSH 终端（xterm.js）
│     │     └─ FileTransferDialog.vue  # SFTP 文件传输
│     │
│     │  └─ ticket/            # 备注：SQL 控制台已默认启用高亮与补全，无需 `?cm=on` 参数。
│     │     ├─ SqlTabs.vue
│     │     ├─ SqlEditor.vue
│     │     └─ ResultTable.vue
│     └─ main.js
├─ scripts/                      # 开发辅助脚本（安全释放端口等）
│  ├─ start_backend.bat
│  ├─ start_frontend.bat
│  ├─ start_frontend.ps1
│  └─ image_tools/*
└─ README.md
```

> 注：首次启动会自动在 MySQL 中创建表（若不存在）。

---

## 环境要求
- Python 3.10+
- Node.js 18+
- PowerShell 或任意终端（Windows 开发环境）

---

## 后端运行（FastAPI）
1) 创建与激活虚拟环境（Windows PowerShell）：
```powershell
# 在项目根目录下
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

2) 安装依赖：
```powershell
pip install -r backend/requirements.txt
```

3) 启动服务（以 `backend/` 为工作目录）：
```powershell
# 方式一：在 backend 目录内运行
uvicorn app.main:app --reload --port 8000

# 方式二：指定 app-dir
# uvicorn app.main:app --reload --port 8000 --app-dir backend
```

### 脚本说明（安全释放端口）
为避免误杀系统/关键进程导致蓝屏，项目提供的启动脚本已实现“安全释放端口”策略：

- `scripts/start_backend.bat` 用法：
  ```bat
  scripts\start_backend.bat [PORT] [APP_DIR] [DATABASE_URL] [--force]
  ```
  - 仅在监听进程为“当前用户”的开发类进程时才会结束（白名单：`python.exe`、`uvicorn.exe`）。
  - 如检测为疑似系统/他人进程占用，将提示并退出（退出码 2），请更换端口或手工处理。
  - 可选 `--force` 将强制结束任意监听进程（不推荐，除非确认安全）。
  - 示例：
    ```bat
    scripts\start_backend.bat 8001 backend
    ```

- `scripts/start_frontend.bat` 用法：
  ```bat
  scripts\start_frontend.bat [DEV_PORT] [BACKEND_PORT] [--force] [HOST]
  ```
  - 仅在监听进程为“当前用户”的前端开发进程时才会结束（白名单：`node.exe`）。
  - 提供 `BACKEND_PORT` 时会自动更新 `frontend/vite.config.js` 的代理目标（同时生成备份 `vite.config.js.bak`）。
  - 可选 `--force` 将强制结束任意监听进程（不推荐，除非确认安全）。
  - 新增 `HOST`（默认 `0.0.0.0`）用于指定监听地址，便于通过局域网 IP 访问。
  - 示例：
    ```bat
    rem 本机默认：监听 0.0.0.0（全部网卡）
    rp

    rem 指定监听 IP（如某网卡地址）
    scripts\start_frontend.bat 5173 8001 "" 192.168.1.100

    rem 强制释放端口后再启动，并监听全部网卡
    scripts\start_frontend.bat 5173 8001 --force 0.0.0.0
    ```
  - 访问示例：`http://<你的IP>:5173/`（首次可能触发 Windows 防火墙提示，请允许访问）。

建议：后端使用 8001，前端使用 5173；仅在明确确认监听进程可安全终止时使用 `--force`。

4) 验证：
- 健康检查：http://127.0.0.1:8000/health
- API 文档（Swagger）：http://127.0.0.1:8000/docs

### 一键启动（命令行脚本）

以下脚本从“项目根目录”执行，自动创建虚拟环境、安装后端依赖并启动 Uvicorn。可按需修改 `DATABASE_URL`。

#### Windows（PowerShell）
```powershell
# 可选：自定义数据库连接字符串（否则使用默认配置）
$env:DATABASE_URL = "mysql+aiomysql://puppet:Puppet%40123@10.2.39.59:3306/db_expert?charset=utf8mb4"

# 创建并激活虚拟环境
python -m venv .venv
. .venv\Scripts\Activate.ps1

# 安装依赖
pip install -r backend/requirements.txt

# 启动后端（指定 app-dir，便于在项目根目录直接运行）
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

#### Windows（CMD）
```bat
REM 可选：自定义数据库连接字符串（否则使用默认配置）
set DATABASE_URL=mysql+aiomysql://puppet:Puppet%40123@10.2.39.59:3306/db_expert?charset=utf8mb4

REM 创建并激活虚拟环境
python -m venv .venv
call .venv\Scripts\activate.bat

REM 安装依赖
pip install -r backend\requirements.txt

REM 启动后端（指定 app-dir，便于在项目根目录直接运行）
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

#### Linux / macOS（Bash）
```bash
# 可选：自定义数据库连接字符串（否则使用默认配置）
export DATABASE_URL="mysql+aiomysql://puppet:Puppet%40123@10.2.39.59:3306/db_expert?charset=utf8mb4"

# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt

# 启动后端（指定 app-dir，便于在项目根目录直接运行）
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

### 环境变量
- `DATABASE_URL`：覆盖默认 MySQL 连接串
  - 默认值（已在 `app/core/config.py` 配置）：
    `mysql+aiomysql://puppet:Puppet%40123@10.2.39.59:3306/db_expert?charset=utf8mb4`
  - 自定义示例：
    `mysql+aiomysql://<user>:<pass>@<ip>:<port>/<database>?charset=utf8mb4`
- `CORS_ORIGINS`：逗号分隔，示例：`http://localhost:5173,http://127.0.0.1:5173`

> 默认 CORS 已包含 `http://localhost:5173` 与 `http://127.0.0.1:5173`。

---

## 前端运行（Vue 3 + Vite）
1) 安装依赖：
```powershell
# 在 frontend 目录下
npm install
```

2) 启动开发服务器：
```powershell
npm run dev
```

3) 访问：
- 前端开发地址（默认）：http://127.0.0.1:5173/
- `vite.config.js` 已配置代理，将 `/api` 代理到 `http://127.0.0.1:8001`

> 前端已集成 Console（WebSSH/SFTP）与 SQL 控制台等模块，统一通过 `src/api.js` 调用后端 `/api/*` 接口。

---

## SQL 控制台使用说明（重要更新）

- 新窗口打开：在“连接管理”中点击“SQL 控制台”将以新标签页打开完整控制台，窗口标题为：`DataVerse - SQL控制台`。
- URL 直达：支持通过地址栏参数直达控制台并指定连接
  - 示例：`http://<host>:5173/?view=sqlconsole&conn=123`
  - `conn` 为连接 ID，`view=sql` 也兼容。
- 连接下拉：控制台工具条左侧的“连接下拉框”展示所有有效连接，默认选中当前连接。
- 标签页与连接绑定（多实例并行）：
  - 每个 SQL 标签在“新建时”会固定绑定一个连接 ID（`connId`）。
  - 切换连接下拉不会改写已有标签的绑定，而是“以所选连接新建一个新的 SQL 标签页”。
  - 不同标签可面向不同连接/实例执行 SQL，互不影响。
- TAB 悬浮提示：鼠标悬停于 SQL 标签页时，会显示该标签绑定连接的“描述信息”（若无描述则显示 `user@ip:port`）。
- 顶部连接信息：控制台标题右侧的 `[user@ip:port]` 会随“当前激活的 SQL 标签”自动变化。

> 以上行为均在前端 `frontend/src/App.vue` 与 `frontend/src/components/ticket/SqlTabs.vue` 中实现：
> - `?view=sqlconsole&conn=<id>` 解析并自动打开控制台
> - 标签 `connId` 固化与切换下拉“新建标签”行为
> - 执行/执行计划请求以“当前标签的 connId”为准
> - 标签 title 悬浮显示连接描述

---

## 数据表结构（MySQL）
默认使用的 MySQL 连接：`10.2.39.59:3306`, 用户：`puppet`，密码：`Puppet@123`，库：`db_expert`。

后端 ORM 映射的表为 `t_db_source`（首次运行自动创建，若不存在；如已存在且结构不同，不会自动变更，见下方说明）：
```sql
CREATE TABLE `t_db_source` (
  `id`          INT(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `ip`          VARCHAR(100) NOT NULL COMMENT '数据库IP',
  `port`        VARCHAR(20)  NOT NULL COMMENT '数据库端口',
  `database`    VARCHAR(40)  NOT NULL COMMENT '数据库名称',
  `user`        VARCHAR(20)  DEFAULT NULL COMMENT '用户名',
  `password`    VARCHAR(200) DEFAULT NULL COMMENT '密码',
  `db_type`     VARCHAR(20)  DEFAULT NULL COMMENT '数据库类型,t_dmlx(dm=01)', 
  `db_env`      VARCHAR(1)   DEFAULT NULL COMMENT '数据库环境,t_dmlx(dm=02)',
  `description` VARCHAR(40)  DEFAULT NULL COMMENT '数据源描述',
  `status`      VARCHAR(1)   DEFAULT NULL COMMENT '数据源状态,t_dmlx(dm=03)', 
  `create_time` DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `creator`     VARCHAR(20)  DEFAULT NULL COMMENT '创建人',
  `update_time` DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近更新时间',
  `updator`     VARCHAR(20)  DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`)
) ENGINE=INNODB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
```

> 说明：应用启动时使用 SQLAlchemy `create_all` 仅“创建不存在的表”，不会自动修改已存在表的字段定义/注释/默认值。如需迁移，请使用 Alembic 或手工执行 DDL。

---

## API 概览（连接管理）
基础路径：`/api/connections`

- 列表
  - `GET /api/connections`
  - 响应：`ConnectionOut[]`

- 新增
  - `POST /api/connections`
  - 请求体：
    ```json
    {
      "ip": "127.0.0.1",
      "port": "3306",
      "database": "test",
      "user": "root",
      "password": "123456",
      "db_type": "mysql",
      "description": "dev mysql"
    }
    ```
  - 响应：`ConnectionOut`

- 查询单个
  - `GET /api/connections/{id}`

- 更新
  - `PUT /api/connections/{id}`
  - 请求体（任意可选字段）：
    ```json
    {
      "description": "prod mysql",
      "status": "1"
    }
    ```

- 删除
  - `DELETE /api/connections/{id}`

- 连通性测试（使用已保存的凭据）
  - `POST /api/connections/{id}/test`
  - 响应：
    ```json
    { "success": true }
    ```

## cURL 示例
```bash
# 列表
curl http://127.0.0.1:8000/api/connections

# 新增
curl -X POST http://127.0.0.1:8000/api/connections \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "127.0.0.1",
    "port": "3306",
    "database": "test",
    "user": "root",
    "password": "123456",
    "db_type": "mysql"
  }'

# 测试连通性（假设返回 id 为 1）
curl -X POST http://127.0.0.1:8000/api/connections/1/test
```

---

## 安全与后续改进
- 目前为演示 MVP，密码明文存放在数据库。生产场景建议：
  - 对敏感信息加密存储（KMS/密钥环）或使用凭据管家（Vault、Secrets Manager 等）
  - 基于 OAuth2/JWT 的鉴权与权限模型
  - 完整的审计日志
- 扩展支持更多数据源（PostgreSQL、SQL Server、Oracle 等）
- 加入前端完善的管理界面（列表、详情、表单校验等）

---
 

## 常见问题
- “表是否会自动创建？”
  - 会。应用启动时会调用 SQLAlchemy `create_all` 在 MySQL 创建 `t_db_source`（若不存在）。
- “前端请求  CORS 被拒绝？”
  - 确认后端正在运行且 `CORS_ORIGINS` 包含前端地址。
- “连通性测试失败？”
  - 确认目标 MySQL 服务可访问、账号/密码/端口正确，并检查防火墙与网络连通。
- “访问 http://127.0.0.1:8000/health 无响应或前端一直等待？”
  - 通常为后端端口被占用或启动时数据库不可达导致阻塞。
  - 端口占用排查（Windows）：
    ```powershell
    netstat -ano | findstr :8000
    # 如被占用，可结束占用进程：Stop-Process -Id <PID> -Force
    ```
  - 推荐使用仓库脚本进行“安全释放端口”：
    - 后端：`scripts\start_backend.bat 8001 backend`（默认只结束当前用户的 `python.exe/uvicorn.exe`）
    - 前端：`scripts\start_frontend.bat 5173 8001`（默认只结束当前用户的 `node.exe`）
    - 仅在确认安全时使用 `--force` 参数覆盖。
  - 临时切换端口（推荐先验证）：
    - 后端：
      ```powershell
      uvicorn app.main:app --reload --port 8001 --app-dir backend
      ```
    - 前端代理 `frontend/vite.config.js`：
      ```js
      proxy: { '/api': { target: 'http://127.0.0.1:8001', changeOrigin: true } }
      ```
  - 数据库不可达导致卡住：为 `DATABASE_URL` 增加超时避免长时间阻塞，例如：
    ```
    mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4&connect_timeout=3
    ```
  - 快速自检（不依赖外部 DB）：可先用 SQLite 启动验证：
    ```
    DATABASE_URL=sqlite+aiosqlite:///./db_expert.db
    ```

---

## 许可
本项目仅用于内部 PoC/演示，后续可根据需要选择合适的开源许可。
![alt text](image.png)