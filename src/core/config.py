from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import Field

class Settings(BaseSettings):
    # 项目基本配置
    PROJECT_NAME: str = "FASTAPI MCP Server"
    API_PREFIX: str = "/api"
    DEBUG: bool = True
    # 数据目录
    EXCEL_FILES_DIR: str = "./data/excel"
    CSV_FILES_DIR: str = "./data/csv"

    # MCP 相关配置
    ALLOWD_TOOLS: List[str] = [
        "excel_list",
        "excel_read",
        "excel_info",
        "csv_read",
        "csv_visualize",
        "csv_aggregate",
        "csv_list",
        "daily_quote",
        "random_quote",
        "weather",
        "text_analyze"
    ]

    # DeepSeek API配置 这里主要是配置deepseek的apikey
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"

    # n8n 集成设置
    N8N_INTEGRATION_ENABLED: bool = False
    N8N_URL: str = "http://localhost:5678"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', case_sensitive=True)

settings = Settings()