import random
import datetime
from typing import Dict, Any

# 鸡汤语录集
QUOTES = [
    "今天又是美好的一天，加油！",
    "不要放弃，坚持就是胜利！",
    "相信自己，你能做到！",
    "每一天都是新的开始，加油！",
    "不要害怕失败，失败是成功之母！",
    "相信自己，你能做到！",
    "每一天都是新的开始，加油！",
    "不要害怕失败，失败是成功之母！",
    "相信自己，你能做到！",
    "每一天都是新的开始，加油！",
    "不要害怕失败，失败是成功之母！"
]

def get_daily_quote() -> Dict[str, Any]:
    """
    获取每日鸡汤语录
    """
    today = datetime.datetime.now()
    date_str = today.strftime("%Y-%m-%d")

    # 使用当前日期作为种子，确保同一天返回相同的"每日鸡汤"
    seed = int(today.strftime("%Y%m%d"))
    random.seed(seed)
    # 随机选择一条鸡汤
    quote = random.choice(QUOTES)
    # 恢复随机数种子
    random.seed()
    return {
        "date": date_str,
        "quote": quote,
        "category": "inspiration"
    }

def get_random_quote(category: str = None) -> Dict[str, Any]:
    """
    获取随机鸡汤

    Args:
        category: 分类（可选），当前仅支持inspiration
    
    Returns:
        包含鸡汤语录和相关信息的字典
    """

    quote = random.choice(QUOTES)
    return {
        "quote": quote,
        "category": "inspiration"
    }