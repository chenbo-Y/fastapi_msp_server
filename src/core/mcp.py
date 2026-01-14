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
        self.params_schema = params_schema

    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具函数"""

        try:
            # 如果有参数模式，验证参数
            if self.params_schema:
                # 从kwargs创建模型实例，验证参数
                params = self.params_schema(**kwargs)
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
                except RuntimeError:
                    # 如果没有事件循环，则创建一个新的事件循环
                    loop = asyncio.new_event_lop()
                    asyncio.set_event_loop(loop)

                # 运行协程并获取结果
                if loop.is_running():
                    # 如果事件循环已经在运行，则创建一个新的事件循环来运行协程
                    # 这是FastAPI这样的异步框架中是必要的
                    result = asyncio.run_corotine_threadsafe(result, loop).result()
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
            if hasattr(self.params_schama, 'model_json_schema'):
                schema = self.params_schema.model_json_schema()
                result["parameters"] = schema.get("properties", {})
                result ["required"] = schema.get("required", [])
            else:
                # 如果是函数或其他类型，则添加简单的参数描述
                result["parameters"] = {
                    "message": "参数结构无法解析"
                }
        
        return result