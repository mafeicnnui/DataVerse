# Data Verse 星域运维平台

一个包含 FastAPI 后端与 Vue 3 前端的全栈项目，用于管理数据库连接信息（首期支持 MySQL）：新增、修改、删除、列表与连通性测试。

后端使用 MySQL 存储连接信息（通过 SQLAlchemy 异步引擎 + aiomysql），并提供 RESTful API；前端基于 Vite + Vue 3，调用后端接口进行管理。

---

## 功能特性
- 连接管理（MySQL）
  - 新增、查询、更新、删除
  - 连通性测试（使用 PyMySQL）
- RESTful API，内置 Swagger 文档 `/docs`
- CORS 已开启，默认允许 `http://localhost:5173`

---

## 目录结构
```
./
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  │  ├─ deps.py
│  │  │  └─ routes/
│  │  │     └─ connections.py
│  │  ├─ core/
│  │  │  └─ config.py
│  │  ├─ db/
│  │  │  └─ base.py
│  │  ├─ models/
│  │  │  └─ connection.py   # ORM 映射到 MySQL 表 t_db_source
│  │  ├─ schemas/
│  │  │  └─ connection.py
│  │  └─ main.py
│  └─ requirements.txt
├─ frontend/
│  ├─ index.html
│  ├─ package.json
│  ├─ vite.config.js
│  └─ src/
│     └─ main.js
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
  - 如检测为疑似系统/他人进程占用，将提示并退出（退出码 2），请更换端口或手动处理。
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
- `vite.config.js` 已配置代理，将 `/api` 代理到 `http://127.0.0.1:8000`

> 当前仓库已放置前端基础脚手架。你可以基于后端 API 自行搭建页面，或后续补充我们提供的界面组件。

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

## 前端 E2E 测试 / Playwright 安装

本项目前端可选用 Playwright 进行端到端（E2E）测试。以下为 Windows（PowerShell）环境的安装与常见问题处理步骤。

### 安装步骤（建议按顺序执行）
1) 以管理员身份运行 PowerShell
   - 右键 PowerShell → 以管理员身份运行。

2) 切换到项目目录（示例）
   - 例如：`d:\work\windsurf\python\DataVerse`（请在你的项目根目录下操作）。

3) 初始化并安装 Playwright 依赖
```powershell
npm init -y
npm install -D @playwright/test
```

4)（推荐）将浏览器缓存目录设置到可写位置，避免权限/杀软拦截
```powershell
New-Item -ItemType Directory -Force -Path "D:\Playwright\ms-playwright" | Out-Null
setx PLAYWRIGHT_BROWSERS_PATH "D:\Playwright\ms-playwright"
```
- 设置环境变量后请“重启 PowerShell”再继续。

5)（可选）清理历史半成品下载
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\AppData\Local\ms-playwright" -ErrorAction SilentlyContinue
```

6) 安装浏览器
```powershell
# 安装默认所需浏览器
npx playwright install

# 仅安装 Chromium（可选）
npx playwright install chromium

# 安装 Chrome 稳定版通道（如确需）
npx playwright install chrome
```

7) 国内网络环境建议设置下载镜像后再安装
```powershell
setx PLAYWRIGHT_DOWNLOAD_HOST "https://npmmirror.com/mirrors/playwright"
# 重启 PowerShell 生效后，重新执行：npx playwright install
```

### 常见问题排查
- 权限不足/Failed to install browsers：
  - 以管理员运行 PowerShell。
  - 使用 `PLAYWRIGHT_BROWSERS_PATH` 指向可写目录（如 `D:\Playwright\ms-playwright`）。
  - 检查杀毒/EDR 是否拦截，必要时为该目录加白名单。
- 提示先安装依赖：先执行 `npm install` 或 `npm install -D @playwright/test` 再运行 `npx playwright install`。
- 下载超时/被墙：配置 `PLAYWRIGHT_DOWNLOAD_HOST` 镜像，重启终端后重试。
- 代理网络：按需设置 `HTTP_PROXY`/`HTTPS_PROXY` 环境变量。
- 版本校验：
```powershell
node -v
npm -v
```

> 说明：Playwright 默认将浏览器下载到 `C:\Users\<你>\AppData\Local\ms-playwright`。若该目录受限（权限/策略/杀软），请使用上文的环境变量改到可写路径。

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
