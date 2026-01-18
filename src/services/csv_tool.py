import pandas as pd
import json
from typing import Dict, Any, List, Optional
import os
from pathlib import Path
import mapplotlib.pyplot as plt
import io
import base64

# 数据文件存储目录
DATA_DIR = Path("./data/csv")
os.makedirs(DATA_DIR, exist_ok=True)

def csv_read(file_path: str, delimiter: str = ",", encoding: str = "utf-8") -> Dict[str, Any]:
    """
    读取CSV文件内容
    Args:
        file_path: CSV文件路劲给（相对于data/csv目录）
        dilimiter: 分隔符，默认逗号
        encoding: 编码，默认utf-8
    Returns:
        包含表格数据的字典
    """
    full_path = DATA_DIR / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"文件 {file_path} 不存在")
    
    try:
        df = pd.read_csv(full_path, delimiter=delimiter, encoding=encoding)
        # 转换为字典，并处理NaN值
        records = df.fillna("").to_dict(orient="records")
        # 获取表头信息
        columns = df.columns.tolist()
        # 获取基本统计信息
        stats = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns":columns,
            "sample_rows": records[:5] if records else []
        }
        return {
            "stats": stats,
            "data": records[:100], # 限制返回前100行，避免数据过大
            "truncated": len(records) > 100
        }
    except Exception as e:
        raise ValueError(f"读取CSV文件失败: {str(e)}")

def csv_visualize(file_path: str, x_column: str, y_column: str, chart_type: str = "bar", title: str = "数据可视化") -> Dict[str, Any]:
    """
    基于CSV数据创建可视化图表

    Args:
        file_path: CSV文件路径
        x_column: X轴列名
        y_column: Y轴列名
        chart_type: 图表类型，可选bar, line, pie
        title: 图表标题

    Returns:
        Base64编码的图表图像
    """
    full_path = DATA_DIR / file_path
    if not full_path.exists():
        raise FileNotFoundError(f"文件 {file_path} 不存在")
    try:
        df = pd.read_csv(full_path)
        if x_column not in df.columns:
            raise ValueError(f"列名 {x_column} 不存在")
        if y_column not in df.columns:
            raise ValueError(f"列名 {y_column} 不存在")

        # 创建图表
        plt.figure(figsize=(10, 6))
        
        if chart_type == "bar":
            df.plot(kind="bar", x=x_column, y=y_column, title=title)
        elif chart_type == "line":
            df.plot(kind="line", x=x_column, y=y_column, title=title)
        elif chart_type == "scatter":
            df.plot(kind="scatter", x=x_column, y=y_column, title=title)
        elif chart_type == "pie":
            # 饼图需要特殊处理
            pie_data = df.set_index(x_column)[y_column]
            pie_data.plot(kind="pie", title=title)
        else:
            raise ValueError(f"不支持的图表类型: {chart_type}")
        plt.tight_layout()


        # 将图表转换为Base64编码
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode()
        plt.close()
        return {
            "chart_type": chart_type,
            "title": title,
            "image_base64": img_str
        }
    except Exception as e:
        raise ValueError(f"可视化失败": {str(e)}")

def csv_aggregate(file_path: str, group_by: str, agg_column: str, agg_func: str = "sum") -> Dict[str, Any]:
    """
    对CSV数据进行聚合操作

    Args:
        file_path: CSV文件路径
        group_by: 分组列名
        agg_column: 聚合列名
        agg_func: 聚合函数，可选sum, mean, max, min, count

    Returns:
        聚合结果
    """
    full_path = DATA_DIR / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"文件 {file_path} 不存在")
    
    try:
        df = pd.read_csv(full_path)
        if group_by not in df.columns:
            raise ValueError(f"列名 {group_by} 不存在")
        if agg_column not in df.columns:
            raise ValueError(f"列名 {agg_column} 不存在")
        
        # 验证聚合函数
        valid_funcs = ["sum", "mean", "max", "min", "count"]
        if agg_func not in valid_funcs:
            raise ValueError(f"不支持的聚合函数: {agg_func}")
        
        # 执行聚合操作
        grouped = df.groupby(group_by)[agg_column].agg(agg_func).reset_index()

        # 转换为记录列表
        result = grouped.to_dict(orient="records")
        return {
            "aggregation": result,
            "group_by": group_by,
            "agg_column": agg_column,
            "agg_func": agg_func
        }
    except Exception as e:
        raise ValueError(f"聚合失败: {str(e)}")

def csv_list() -> Dict[str, Any]:
    """
    列出可用的CSV文件

    Returns:
        可用的CSV文件列表
    """
    files = []
    for file_path in DATA_DIR.glob("**/*.csv"):
        rel_path = file_path.relative_to(DATA_DIR)
        files.append(str(rel_path))
    return {
        "files": files
    }
        
    