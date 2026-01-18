# FastAPI MCP Server

一个基于 FastAPI 的 Model Context Protocol (MCP) 服务器，提供 Excel 和 CSV 数据处理、每日语录等工具服务的 RESTful API 接口。

## 📋 目录

- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [API 文档](#api-文档)
- [使用示例](#使用示例)
- [配置说明](#配置说明)
- [开发指南](#开发指南)

## ✨ 功能特性

### 数据处理工具
- **CSV 工具**
  - 列出可用 CSV 文件
  - 读取 CSV 文件内容
  - 数据聚合分析
  - 数据可视化（支持柱状图、折线图、散点图、饼图）

- **Excel 工具**
  - 列出可用 Excel 文件
  - 读取 Excel 文件内容（支持多工作表）
  - 获取 Excel 文件详细信息

### 其他工具
- 每日鸡汤语录（同一天返回固定内容）
- 随机鸡汤语录

### 核心功能
- MCP 协议支持（会话管理、工具注册、消息处理）
- 支持同步和异步工具函数
- Pydantic 参数验证
- CORS 中间件支持
- 自动生成的 API 文档

## 📁 项目结构

```
mcp_server/
├── src/
│   ├── main.py              # FastAPI 应用主入口
│   ├── core/                # 核心模块
│   │   ├── config.py        # 配置管理
│   │   └── mcp.py           # MCP 协议处理器
│   └── services/            # 服务模块
│       ├── csv_tool.py      # CSV 数据处理服务
│       ├── excel_tool.py    # Excel 数据处理服务
│       └── daily_quote.py   # 每日语录服务
├── data/                    # 数据文件目录（自动创建）
│   ├── csv/                 # CSV 文件存储目录
│   └── excel/               # Excel 文件存储目录
├── 技术文档.md              # 详细技术文档
└── README.md                # 项目说明文档
```

## 🛠 技术栈

- **Web 框架**: FastAPI
- **数据验证**: Pydantic
- **数据处理**: Pandas
- **数据可视化**: Matplotlib
- **异步支持**: asyncio
- **服务器**: Uvicorn

## 🚀 快速开始

### 环境要求

- Python 3.7+
- pip 或 conda

### 安装步骤

1. **克隆项目**（如果从仓库获取）

```bash
git clone <repository-url>
cd mcp_server
```

2. **安装依赖**

```bash
pip install fastapi uvicorn pydantic pydantic-settings pandas matplotlib openpyxl
```

或者创建 `requirements.txt` 文件：

```txt
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pandas>=2.0.0
matplotlib>=3.7.0
openpyxl>=3.1.0
```

然后安装：

```bash
pip install -r requirements.txt
```

3. **配置环境变量**（可选）

创建 `.env` 文件（可选，所有配置都有默认值）：

```env
PROJECT_NAME=FASTAPI MCP Server
API_PREFIX=/api
DEBUG=True
EXCEL_FILES_DIR=./data/excel
CSV_FILES_DIR=./data/csv
DEEPSEEK_API_KEY=your_api_key_here
```

4. **准备数据文件**（可选）

将 CSV 和 Excel 文件放入对应目录：

```bash
mkdir -p data/csv data/excel
# 将您的文件复制到对应目录
```

5. **启动服务**

```bash
cd src
python main.py
```

或者使用 uvicorn 直接启动：

```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

6. **验证服务**

访问以下地址验证服务是否正常：

- 服务状态: http://127.0.0.1:8000/
- API 文档 (Swagger): http://127.0.0.1:8000/docs
- API 文档 (ReDoc): http://127.0.0.1:8000/redoc

## 📚 API 文档

### 基础端点

#### GET `/`

获取服务状态信息。

**响应示例**:
```json
{
  "stauts": "online",
  "service": "FASTAPI MCP Server",
  "version": "1.0.0",
  "api_prefix": "/api"
}
```

#### GET `/api/mcp/tools`

获取所有可用工具列表。

**响应示例**:
```json
{
  "tools": ["csv_list", "csv_read", "excel_list", ...],
  "definitions": {
    "csv_list": {
      "name": "csv_list",
      "description": "列出可用的CSV文件",
      "parameters": {}
    },
    ...
  }
}
```

### MCP 协议端点

#### POST `/api/mcp/init`

初始化 MCP 会话。

**响应示例**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "auth_key": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "supported_tools": ["csv_list", "csv_read", ...],
  "tool_definitions": {...}
}
```

#### POST `/api/mcp/session/{session_id}/message`

处理 MCP 消息，调用工具。

**请求体**:
```json
{
  "message_id": "optional-uuid",
  "tool_name": "csv_list",
  "arguments": {},
  "authentication_key": "your-auth-key"
}
```

**响应示例**:
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "tool_name": "csv_list",
  "result": {
    "files": ["data.csv", "sales.csv"]
  }
}
```

#### DELETE `/api/mcp/session/{session_id}`

断开指定会话。

**响应示例**:
```json
{
  "message": "会话 {session_id} 已断开连接"
}
```

## 💡 使用示例

### 1. 使用 curl 调用 API

#### 初始化会话

```bash
curl -X POST http://127.0.0.1:8000/api/mcp/init
```

#### 列出 CSV 文件

```bash
curl -X POST http://127.0.0.1:8000/api/mcp/session/{session_id}/message \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "csv_list",
    "arguments": {},
    "authentication_key": "your-auth-key"
  }'
```

#### 读取 CSV 文件

```bash
curl -X POST http://127.0.0.1:8000/api/mcp/session/{session_id}/message \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "csv_read",
    "arguments": {
      "file_path": "data.csv",
      "delimiter": ",",
      "encoding": "utf-8"
    },
    "authentication_key": "your-auth-key"
  }'
```

#### CSV 数据聚合

```bash
curl -X POST http://127.0.0.1:8000/api/mcp/session/{session_id}/message \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "csv_aggregate",
    "arguments": {
      "file_path": "sales.csv",
      "group_by": "category",
      "agg_column": "sales",
      "agg_func": "sum"
    },
    "authentication_key": "your-auth-key"
  }'
```

#### 读取 Excel 文件

```bash
curl -X POST http://127.0.0.1:8000/api/mcp/session/{session_id}/message \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "excel_read",
    "arguments": {
      "file_name": "data.xlsx",
      "sheet_name": "Sheet1"
    },
    "authentication_key": "your-auth-key"
  }'
```

#### 获取每日语录

```bash
curl -X POST http://127.0.0.1:8000/api/mcp/session/{session_id}/message \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "daily_quote",
    "arguments": {},
    "authentication_key": "your-auth-key"
  }'
```

### 2. 使用 Python 客户端

```python
import requests

# 服务器地址
BASE_URL = "http://127.0.0.1:8000"

# 1. 初始化会话
response = requests.post(f"{BASE_URL}/api/mcp/init")
session_data = response.json()
session_id = session_data["session_id"]
auth_key = session_data["auth_key"]

# 2. 调用工具
def call_tool(tool_name, arguments):
    url = f"{BASE_URL}/api/mcp/session/{session_id}/message"
    payload = {
        "tool_name": tool_name,
        "arguments": arguments,
        "authentication_key": auth_key
    }
    response = requests.post(url, json=payload)
    return response.json()

# 3. 使用示例
# 列出 CSV 文件
result = call_tool("csv_list", {})
print(result)

# 读取 CSV 文件
result = call_tool("csv_read", {
    "file_path": "data.csv",
    "delimiter": ",",
    "encoding": "utf-8"
})
print(result)

# 获取每日语录
result = call_tool("daily_quote", {})
print(result)

# 4. 断开会话
requests.delete(f"{BASE_URL}/api/mcp/session/{session_id}")
```

### 3. 使用 Swagger UI

访问 http://127.0.0.1:8000/docs 可以直接在浏览器中测试所有 API 端点。

## ⚙️ 配置说明

配置文件位于 `src/core/config.py`，支持通过环境变量或 `.env` 文件配置。

### 主要配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `PROJECT_NAME` | str | "FASTAPI MCP Server" | 项目名称 |
| `API_PREFIX` | str | "/api" | API 路径前缀 |
| `DEBUG` | bool | True | 调试模式 |
| `EXCEL_FILES_DIR` | str | "./data/excel" | Excel 文件目录 |
| `CSV_FILES_DIR` | str | "./data/csv" | CSV 文件目录 |
| `DEEPSEEK_API_KEY` | Optional[str] | None | DeepSeek API 密钥 |

### 环境变量配置

所有配置项都可以通过环境变量设置：

```bash
export PROJECT_NAME="My MCP Server"
export API_PREFIX="/api/v1"
export DEBUG=False
```

## 🔧 开发指南

### 添加新工具

1. 在 `src/services/` 目录下创建新的服务文件或扩展现有文件

```python
# src/services/my_tool.py
def my_new_tool(param1: str, param2: int = 10) -> dict:
    """新工具函数"""
    return {"result": f"处理 {param1} 和 {param2}"}
```

2. 在 `src/main.py` 中注册工具

```python
from src.services.my_tool import my_new_tool

mcp_handler.register_tool(
    "my_new_tool",
    my_new_tool,
    "新工具的描述"
)
```

### 添加参数验证

使用 Pydantic 模型定义参数验证：

```python
from pydantic import BaseModel

class MyToolParams(BaseModel):
    param1: str
    param2: int = 10

mcp_handler.register_tool(
    "my_new_tool",
    my_new_tool,
    "新工具的描述",
    params_schema=MyToolParams
)
```

### 支持异步工具

工具函数可以是异步的，系统会自动处理：

```python
async def async_tool(param: str) -> dict:
    import asyncio
    await asyncio.sleep(0.1)  # 模拟异步操作
    return {"result": param}

mcp_handler.register_tool(
    "async_tool",
    async_tool,
    "异步工具"
)
```

## 📝 已注册的工具列表

- `csv_list` - 列出可用的CSV文件
- `csv_read` - 读取CSV文件内容
- `csv_aggregate` - 对CSV数据进行聚合操作
- `csv_visualize` - 可视化CSV数据
- `excel_list` - 列出可用的Excel文件
- `excel_read` - 读取Excel文件内容
- `excel_info` - 获取Excel文件信息
- `random_quote` - 获取随机鸡汤
- `daily_quote` - 获取每日鸡汤

## ⚠️ 注意事项

1. **文件路径安全**: 当前实现中，建议验证文件路径以防止目录遍历攻击
2. **文件大小限制**: 大文件可能导致内存问题，建议在生产环境中添加文件大小限制
3. **CORS 配置**: 默认允许所有来源，生产环境应限制允许的域名
4. **认证机制**: 当前使用简单的 UUID 认证，生产环境建议使用更安全的认证方式

## 📖 更多文档

详细的技术文档请参考 [技术文档.md](./技术文档.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

（待补充）

## 👤 作者

（待补充）

## 📞 联系方式

（待补充）

---

**注意**: 本项目仍在开发中，部分功能可能不完整。如有问题，请提交 Issue。

