# modules/billing.py

from typing import List, Tuple, Optional
from modules.prices import PRODUCT_PRICES

class Billing:
    """
    简单的账单管理类。
    维护已添加商品列表、总价，并支持根据索引添加、删除最后一项等操作。
    """

    def __init__(self):
        # items: List of (label, price)
        self.items: List[Tuple[str, float]] = []
        # 当前总价
        self.total: float = 0.0

    def add_item(self, label: str, price: float) -> Tuple[str, float]:
        """
        添加一笔商品。
        返回 (label, price) 以便上层调用打印或显示。
        """
        self.items.append((label, price))
        self.total += price
        return label, price

    def remove_last_item(self) -> Tuple[Optional[str], float]:
        """
        删除最后一笔商品，返回 (label, price)。
        如果没有商品，返回 (None, 0.0)。
        """
        if not self.items:
            return None, 0.0
        label, price = self.items.pop()
        self.total -= price
        return label, price

    def add_item_by_index(self, idx: int) -> Tuple[str, float]:
        """
        根据 PRODUCT_PRICES 的键列表，以索引方式手动添加。
        会按照 dict 的 key 顺序构建一个列表，然后取第 idx 项。
        抛出 IndexError 如果 idx 越界。
        """
        keys = list(PRODUCT_PRICES.keys())
        if idx < 0 or idx >= len(keys):
            raise IndexError(f"Invalid product index: {idx}")
        label = keys[idx]
        price = PRODUCT_PRICES[label]
        return self.add_item(label, price)

    def last_item_name(self) -> Optional[str]:
        """
        返回最后一笔商品的名称，不移除它。
        如果没有商品，返回 None。
        """
        if not self.items:
            return None
        return self.items[-1][0]
