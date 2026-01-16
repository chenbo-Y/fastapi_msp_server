import os
import pandas as pd
from typing import Dict, List, Any, Optional

from src.core.config import settings

def excel_list() -> Dict[str, Any]:
    """列出可用的Excel文件"""
    try:
        os.makedirs(settings.EXCEL_FILES_DIR, exist_ok=True)
        files = [f for f in os.listdir(settings.EXCEL_FILES_DIR) if f.endswith('.xlsx')]
        return {
            "files": files
        }
    except Exception as e:
        raise ValueError(f"列出Excel文件失败: {str(e)}")

def excel_read(file_name: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
    """读取Excel文件"""
    try:
        file_path = os.path.join(settings.EXCEL_FILES_DIR, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_name} 不存在")
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            # 读取第一个工作表
            df = pd.read_excel(file_path)
        # 将DataFrame转换为字典
        records = df.to_dict(orient="records")
        columns = df.columns.tolist()
        return {
            "file_name": file_name,
            "sheet_name": sheet_name or "默认工作表",
            "columns": columns,
            "rows": records,
            "row_count": len(records)
        }
    except Exception as e:
        raise ValueError(f"读取Excel文件失败: {str(e)}")

def excel_info(file_name: str) -> Dict[str, Any]:
    """获取Excel文件信息"""
    try:
        file_path = os.path.join(settings.EXCEL_FILES_DIR, file_name)
        if not os.path.exists(file_path):
            raise ValueError(f"文件 {file_name} 不存在")

        # 读取所有工作表名称
        xl = pd.ExcelFile(file_path)
        sheet_names = xl.sheet_names

        # 获取每个工作表的大小
        sheets_info = []
        for sheet in sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)
            sheets_info.append(
                {
                    "name": sheet,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": df.columns.tolist()
                }
            )
        return {
            "file_name": file_name,
            "sheets": sheets_info,
            "sheet_count": len(sheets_info),
            "file_size_kb": round(os.path.getsize(file_path) / 1024, 2)
        }
    except Exception as e:
        raise ValueError(f"获取Excel文件信息失败: {str(e)}")
        