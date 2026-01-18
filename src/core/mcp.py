import asyncio
import inspect
import uuid
from typing import Any, Dict, List, Optional, Callable, Type
from pydantic import BaseModel, Field

from .config import settings

class ToolDefinition:
    """工具定义类"""

    def __init__(self,
                name: str,
                function: Callable,
                description: str = "",
                params_schema: Optional[Type[BaseModel]] = None):
        self.name = name
        self.function = function
        self.description = description
        self.params_schema = params_schema # 存储类对象

    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具函数"""

        try:
            # 如果有参数模式，验证参数
            if self.params_schema:
                # 从kwargs创建模型实例，验证参数
                params = self.params_schema(**kwargs) # 等价于params = classinstance（**kwargs)
                # 将验证后的参数转换为字典
                validated_params = params.model_dump()
                # 使用验证后的参数调用函数
                result = self.function(**validated_params)
            else:
                # 没有参数模式，直接调用函数
                result = self.function(**kwargs)

            # 检查结果是否是协程（异步函数的返回值）
            if inspect.iscoroutine(result):
                # 如果是协程，使用事件循环运行它
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:o
                    # 如果没有事件循环，则创建一个新的事件循环
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                # 运行协程并获取结果
                if loop.is_running():
                    # 如果事件循环已经在运行，则创建一个新的事件循环来运行协程
                    # 这是FastAPI这样的异步框架中是必要的
                    result = asyncio.run_coroutine_threadsafe(result, loop).result()
                else:
                    # 如果事件循环没有运行，则直接使用它来运行协程
                    result = loop.run_until_complete(result)
                
            return result
        except Exception as e:
            # 捕获任何异常并返回错误信息
            # 可以在这里添加日志记录
            print(f"工具执行错误： {str(e)}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """转换工具定义为字典"""
        result = {
            "name": self.name,
            "description": self.description
        }

        # 如果有参数模式，则添加参数信息
        if self.params_schema:
            # 检查params_schema是否为类而不是函数
            if hasattr(self.params_schema, 'model_json_schema'):
                schema = self.params_schema.model_json_schema()
                result["parameters"] = schema.get("properties", {})
                result["required"] = schema.get("required", [])
            else:
                # 如果是函数或其他类型，则添加简单的参数描述
                result["parameters"] = {
                    "message": "参数结构无法解析"
                }
        
        return result

class MCPSession:
    """MCP 会话管理"""

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.auth_key = str(uuid.uuid4())
        self.supported_tools: List[str] = []
        self.connected = True

    def verify_auth(self, auth_key: str) -> bool:
        return self.auth_key == auth_key

    def disconnect(self):
        self.connected = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "auth_key": self.auth_key,
            "supported_tools": self.supported_tools,
            "connected": self.connected
        }

class MCPMessage(BaseModel):
    """MCP 消息模型"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: str
    arguments: Dict[str, Any] = {}
    authentication_key: Optional[str] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class MCPHandler:
    """MCP 消息处理器"""

    def __init__(self):
        self._sessions: Dict[str, MCPSession] = {}
        self._tools: Dict[str, ToolDefinition] = {}

    def create_session(self) -> MCPSession:
        session = MCPSession()
        session.supported_tools = list(self._tools.keys())
        self._sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[MCPSession]:
        return self._sessions.get(session_id)

    def register_tool(
        self,
        tool_name: str,
        tool_func: Callable,
        description: str = "",
        params_schema: Optional[Type[BaseModel]] = None,
        force: bool = False
    ) -> None:
        """注册工具函数，当force=True时会覆盖已存在的工具"""
        if tool_name in self._tools and not force:
            # 如果工具已经注册且不强制覆盖，则跳过注册
            print(f"工具 {tool_name} 已经注册，跳过注册")
            return

        # 验证params_schema是否为Pydantic模型类
        if params_schema is not None and not (isinstance(params_schema, type) and issubclass(params_schema, BaseModel)):
            print(f"警告： 工具 {tool_name} 的params_schema不适Pydantic BaseModel类，将被设置为None")
            params_schema = None

        # 创建工具定义
        tool_def = ToolDefinition(
            name=tool_name,
            function=tool_func,
            description=description,
            params_schema=params_schema
        )

        self._tools[tool_name] = tool_def
    
    def get_tool_definitions(self) -> Dict[str, Dict[str, Any]]:
        """获取所有工具定义"""

        return {
            name: tool.to_dict() for name, tool in self._tools.items()
        }

    def process_message(self, message: MCPMessage, session_id: str) -> MCPMessage:
        session = self.get_session(session_id)
        if not session:
            return MCPMessage(
                message_id=message.message_id,
                tool_name=message.tool_name,
                error=f"会话 {session_id} 不存在"
            )

        if not session.connected:
            return MCPMessage(
                message_id=message.message_id,
                tool_name=message.tool_name,
                error=f"会话 {session_id} 已断开连接"
            )

        if not session.verify_auth(message.authentication_key):
            return MCPMessage(
                message_id=message.message_id,
                tool_name=message.tool_name,
                error="无效的认证密钥"
            )

        if message.tool_name not in self._tools:
            return MCPMessage(
                message_id=message.message_id,
                tool_name=message.tool_name,
                error=f"工具 {message.tool_name} 未注册"
            )
        try:
            # 获取工具定义
            tool = self._tools[message.tool_name]
            # 执行工具
            result = tool.execute(**message.arguments)

            # 检查结果是否包含错误信息
            if isinstance(result, dict) and "error" in result:
                print(f"工具执行返回错误：{result['error']}")
                return MCPMessage(
                    message_id=message.message_id,
                    tool_name=message.tool_name,
                    error=result["error"],
                    result=None
                )

            # 构建响应
            return MCPMessage(
                message_id=message.message_id,
                tool_name=message.tool_name,
                result=result
            )
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"工具调用错误: {str(e)}\n{error_detail}")
            return MCPMessage(
                message_id=message.message_id,
                tool_name=message.tool_name,
                error=f"工具调用错误: {str(e)}"
            )

# 全局MCP处理器实例
mcp_handler = MCPHandler()