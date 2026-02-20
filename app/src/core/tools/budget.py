"""Budget and savings plan CRUD; data stored in src/storage/budget/{year}.json."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from langchain.tools import tool

# Storage under project src/storage/budget/
_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "budget"

# 每月支出分類（用於詢問使用者並寫入 monthly_expenses）
EXPENSE_CATEGORIES = ("房貸", "交通", "伙食", "備用金", "投資金", "其他")
# 旅遊為年度預算，另存 yearly_travel_budget


def _path_for_year(year: int) -> Path:
    _STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    return _STORAGE_DIR / f"{year}.json"


def _default_data(year: int) -> dict[str, Any]:
    return {
        "year": year,
        "monthly_budget": None,
        "yearly_budget": None,
        "yearly_travel_budget": None,  # 旅遊：年度預算
        "monthly_expenses": {c: None for c in EXPENSE_CATEGORIES},
        "savings_plans": [],
        "wishlist": [],
    }


def _load(year: int) -> dict[str, Any]:
    p = _path_for_year(year)
    if not p.exists():
        data = _default_data(year)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data
    try:
        raw = p.read_text(encoding="utf-8")
        if not raw.strip():
            return _default_data(year)
        data = json.loads(raw)
    except (json.JSONDecodeError, OSError) as e:
        # 檔案損壞或格式錯誤時回退預設，避免 crash
        data = _default_data(year)
        try:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass
        return data
    # 補齊欄位
    if "monthly_expenses" not in data:
        data["monthly_expenses"] = {c: None for c in EXPENSE_CATEGORIES}
    for c in EXPENSE_CATEGORIES:
        if c not in data["monthly_expenses"]:
            data["monthly_expenses"][c] = None
    if "wishlist" not in data:
        data["wishlist"] = []
    if "yearly_travel_budget" not in data:
        data["yearly_travel_budget"] = None
    return data


def _save(year: int, data: dict[str, Any]) -> None:
    data["year"] = year
    p = _path_for_year(year)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Budget (year-level)
# ---------------------------------------------------------------------------

@tool
def get_budget(year: int | None = None) -> str:
    """Get monthly and yearly budget for a year. Defaults to current year if not given."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    monthly = data.get("monthly_budget")
    yearly = data.get("yearly_budget")
    if monthly is None and yearly is None:
        return f"{y} 年尚未設定預算。"
    parts = []
    if monthly is not None:
        parts.append(f"月預算：{monthly}")
    if yearly is not None:
        parts.append(f"年預算：{yearly}")
    return f"{y} 年 " + "，".join(parts)


@tool
def set_budget(
    monthly_budget: int | None = None,
    yearly_budget: int | None = None,
    year: int | None = None,
) -> str:
    """Set monthly and/or yearly budget for a year. Defaults to current year."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    if monthly_budget is not None:
        data["monthly_budget"] = monthly_budget
    if yearly_budget is not None:
        data["yearly_budget"] = yearly_budget
    _save(y, data)
    parts = [f"{y} 年預算已更新"]
    if data.get("monthly_budget") is not None:
        parts.append(f"月預算 {data['monthly_budget']}")
    if data.get("yearly_budget") is not None:
        parts.append(f"年預算 {data['yearly_budget']}")
    return "；".join(parts) + "。"


@tool
def get_yearly_travel_budget(year: int | None = None) -> str:
    """Get yearly travel budget for a year. 旅遊是年度預算，不是每月支出. Defaults to current year."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    val = data.get("yearly_travel_budget")
    if val is None:
        return f"{y} 年尚未設定旅遊預算。"
    return f"{y} 年旅遊預算：{val} 元。"


@tool
def set_yearly_travel_budget(amount: int, year: int | None = None) -> str:
    """Set yearly travel budget for a year. 旅遊是年度預算. Defaults to current year."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    data["yearly_travel_budget"] = amount
    _save(y, data)
    return f"{y} 年旅遊預算已設為 {amount} 元。"


# ---------------------------------------------------------------------------
# Savings plans (CRUD)
# ---------------------------------------------------------------------------

@tool
def list_savings_plans(year: int | None = None) -> str:
    """List all savings plans for a year. Defaults to current year."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    plans = data.get("savings_plans") or []
    if not plans:
        return f"{y} 年尚無存錢規劃。"
    def _line(p: dict) -> str:
        name = p.get("name") or "未命名"
        pid = p.get("id") or ""
        target = p.get("target_amount") if p.get("target_amount") is not None else "未設"
        monthly = p.get("monthly_amount") if p.get("monthly_amount") is not None else "未設"
        note = (p.get("note") or "").strip()
        return f"- {name} (id: {pid})：目標 {target}，每月 {monthly}" + (f"；{note}" if note else "")

    lines = [_line(p) for p in plans]
    return f"{y} 年存錢規劃：\n" + "\n".join(lines)


@tool
def add_savings_plan(
    name: str,
    target_amount: int | None = None,
    monthly_amount: int | None = None,
    note: str = "",
    year: int | None = None,
) -> str:
    """Add a savings plan for a year. Give at least name; target_amount and monthly_amount are optional."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    plans = data.get("savings_plans") or []
    plan_id = str(uuid.uuid4())[:8]
    plan = {
        "id": plan_id,
        "name": name,
        "target_amount": target_amount,
        "monthly_amount": monthly_amount,
        "note": note or "",
    }
    plans.append(plan)
    data["savings_plans"] = plans
    _save(y, data)
    return f"已新增存錢規劃「{name}」(id: {plan_id})。"


@tool
def update_savings_plan(
    plan_id: str,
    name: str | None = None,
    target_amount: int | None = None,
    monthly_amount: int | None = None,
    note: str | None = None,
    year: int | None = None,
) -> str:
    """Update an existing savings plan by id. Only provided fields are updated."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    plans = data.get("savings_plans") or []
    for p in plans:
        if p.get("id") == plan_id:
            if name is not None:
                p["name"] = name
            if target_amount is not None:
                p["target_amount"] = target_amount
            if monthly_amount is not None:
                p["monthly_amount"] = monthly_amount
            if note is not None:
                p["note"] = note
            _save(y, data)
            return f"已更新存錢規劃 id {plan_id}。"
    return f"找不到 id 為 {plan_id} 的存錢規劃。"


@tool
def delete_savings_plan(plan_id: str, year: int | None = None) -> str:
    """Delete a savings plan by id."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    plans = data.get("savings_plans") or []
    for i, p in enumerate(plans):
        if p.get("id") == plan_id:
            plans.pop(i)
            data["savings_plans"] = plans
            _save(y, data)
            return f"已刪除存錢規劃 id {plan_id}。"
    return f"找不到 id 為 {plan_id} 的存錢規劃。"


# ---------------------------------------------------------------------------
# Monthly expense categories (房貸、交通、伙食、備用金、投資金、其他)
# ---------------------------------------------------------------------------

@tool
def get_monthly_expenses(year: int | None = None) -> str:
    """Get current monthly expense breakdown by category (房貸、交通、伙食、備用金、投資金、旅遊、其他). Defaults to current year."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    expenses = data.get("monthly_expenses") or {}
    lines = []
    total = 0
    for cat in EXPENSE_CATEGORIES:
        val = expenses.get(cat)
        if val is not None:
            lines.append(f"- {cat}：{val}")
            total += val
        else:
            lines.append(f"- {cat}：未填")
    if not lines:
        return f"{y} 年尚未填寫每月支出。"
    return f"{y} 年每月支出：\n" + "\n".join(lines) + (f"\n合計：{total}" if total else "")


@tool
def set_monthly_expense(
    category: str,
    amount: int,
    year: int | None = None,
) -> str:
    """Set one monthly expense category. category must be one of: 房貸, 交通, 伙食, 備用金, 投資金, 旅遊, 其他."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    if category not in EXPENSE_CATEGORIES:
        return f"類別必須是以下之一：{', '.join(EXPENSE_CATEGORIES)}。"
    data = _load(y)
    if "monthly_expenses" not in data:
        data["monthly_expenses"] = {c: None for c in EXPENSE_CATEGORIES}
    data["monthly_expenses"][category] = amount
    _save(y, data)
    return f"已將「{category}」設為每月 {amount} 元。"


# ---------------------------------------------------------------------------
# Wishlist（想買的東西）：記錄並可討論何時能買
# ---------------------------------------------------------------------------

@tool
def list_wishlist(year: int | None = None) -> str:
    """List all wishlist items (things the user wants to buy). Defaults to current year."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    items = data.get("wishlist") or []
    if not items:
        return f"{y} 年目前沒有記錄想買的東西。"
    lines = [f"- {i.get('name', '?')}：約 {i.get('price', '?')} 元 (id: {i.get('id', '')})" + (f"；{i.get('note', '')}" if i.get("note") else "") for i in items]
    return f"{y} 年想買的清單：\n" + "\n".join(lines)


@tool
def add_wishlist_item(
    name: str,
    price: int,
    note: str = "",
    year: int | None = None,
) -> str:
    """Add something the user wants to buy (name and approximate price). Use for discussing when they can afford it."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    items = data.get("wishlist") or []
    item_id = str(uuid.uuid4())[:8]
    items.append({"id": item_id, "name": name, "price": price, "note": note or ""})
    data["wishlist"] = items
    _save(y, data)
    return f"已加入「{name}」約 {price} 元 (id: {item_id})。之後可以一起看預算與儲蓄，討論什麼時候可以買。"


@tool
def update_wishlist_item(
    item_id: str,
    name: str | None = None,
    price: int | None = None,
    note: str | None = None,
    year: int | None = None,
) -> str:
    """Update a wishlist item by id. Only provided fields are updated."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    items = data.get("wishlist") or []
    for i in items:
        if i.get("id") == item_id:
            if name is not None:
                i["name"] = name
            if price is not None:
                i["price"] = price
            if note is not None:
                i["note"] = note
            _save(y, data)
            return f"已更新想買的東西 id {item_id}。"
    return f"找不到 id 為 {item_id} 的項目。"


@tool
def delete_wishlist_item(item_id: str, year: int | None = None) -> str:
    """Remove a wishlist item by id."""
    from datetime import datetime
    y = year if year is not None else datetime.now().year
    data = _load(y)
    items = data.get("wishlist") or []
    for idx, i in enumerate(items):
        if i.get("id") == item_id:
            items.pop(idx)
            data["wishlist"] = items
            _save(y, data)
            return f"已從清單移除 id {item_id}。"
    return f"找不到 id 為 {item_id} 的項目。"
