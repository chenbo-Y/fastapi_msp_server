from fastapi import FastAPI, HTTPException, Path, Query, Body, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src.core.config import settings
from src.core.mcp import MCPHandler, MCPMessage
from src.services.daily_quote import get_daily_quote, get_random_quote
from src.services.csv_tool import csv_read, csv_visualize, csv_aggregate, csv_list
from src.services.excel_tool import excel_list, excel_read, excel_info

class MCPInitResponse(BaseModel):
    session_id: str
    auth_key: str
    supported_tools: List[str]
    tool_definitions: Dict[str, Any]

class MCPMessageResponse(BaseModel):
    message_id: str
    tool_name: str
    result: Dict[str, Any]

class MCPMessageRequest(BaseModel):
    message_id: Optional[str] = None
    tool_name: str
    arguments: Dict[str, Any] = {}
    authentication_key: Optional[str] = None

app = FastAPI (
    title=settings.PROJECT_NAME,
    description="MCP Server for Excel and CSV data processing",
    version="1.0.0"
)

mcp_handler.register_tool(
    "csv_list",
    csv_list,
    "列出可用的CSV文件"
)
mcp_handler.register_tool(
    "csv_read",
    csv_read,
    "读取CSV文件内容"
)
mcp_handler.register_tool(
    "excel_info",
    excel_info,
    "获取Excel文件信息"
)
mcp_handler.register_tool(
    "excel_list",
    excel_list,
    "列出可用的Excel文件"
)
mcp_handler.register_tool(
    "excel_read",
    excel_read,
    "读取Excel文件内容"
)
mcp_handler.register_tool(
    "csv_aggregate",
    csv_aggregate,
    "对CSV数据进行聚合操作"
)
mcp_handler.register_tool(
    "csv_visualize",
    csv_visualize,
    "可视化CSV数据"
)
mcp_handler.register_tool(
    "random_quote",
    get_random_quote,
    "获取随机鸡汤"
)
mcp_handler.register_tool(
    "daily_quote",
    get_daily_quote
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "stauts": "online",
        "service": settings.PROJECT_NAME
        "version": app.version,
        "api_prefix": settings.API_PREFIX
    }

@app.get(f"{settings.API_PREFIX}/mcp/tools")
async def get_tools():
    return {
        "tools": list(mcp_handler.get_tool_definitions().keys())
        "definitions": mcp_handler.get_tool_definitions()
    }

@app.post(
    f"{settings.API_PREFIX}/mcp/init",
    response_model=MCPInitResponse.
    status_code=status.HTTP_201_CREATED
)
async def init_session()
    """初始化MCP会话"""
    session = mcp_handler.create_session()
    return {
        "session_id": session.session_id,
        "auth_key": session.auth_key,
        "supported_tools": session.supported_tools,
        "tool_definitions": mcp_handler.get_tool_definitions()
    }

@app.post(
    f"{settings.API_PREFIX}/mcp/session/{session_id}/message",
    response_model=MCPMessageResponse
)
async def process_message(
    message: MCPMessageReques = Body(...),
    session_id: str = Path(...)
):
    mcp_message = MCPMessage(
        message_id=message.message_id,
        tool_name=message.tool_name,
        arguments=message.arguments,
        authentication_key=message.authentication_key
    )
    response = mcp_handler.process_message(mcp_message, session_id)
    if response.error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.error
        )
    return {
        "message_id": response.message_id,
        "tool_name": response.tool_name,
        "result": response.result
    }

@app.delete(
    f"{settings.API_PREFIX}/mcp/session/{{session_id}}",
)
async def disconnect_session(session_id: str = Path(...)):
    session = mcp_handler.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会话 {session_id} 不存在"
        )
    session.disconnect()
    return {
        "message": f"会话 {session_id} 已断开连接"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='main:app', host="127.0.0.1", port=8000, reload=True, workers=1)
