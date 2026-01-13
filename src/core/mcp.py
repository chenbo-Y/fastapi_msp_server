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