"""Goals storage: year / quarter / week / day. Data under src/storage/goals/."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain.tools import tool

_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "goals"


def _ensure_dir() -> None:
    _STORAGE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Year
# ---------------------------------------------------------------------------

def _year_path(year: int) -> Path:
    _ensure_dir()
    return _STORAGE_DIR / f"year_{year}.json"


def _default_year(year: int) -> dict[str, Any]:
    return {
        "year": year,
        "year_theme": None,
        "outcomes": [],
        "constraints": None,
        "north_star_metrics": None,
    }


def _load_year(year: int) -> dict[str, Any]:
    p = _year_path(year)
    if not p.exists():
        data = _default_year(year)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data
    raw = p.read_text(encoding="utf-8")
    if not raw.strip():
        return _default_year(year)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        data = _default_year(year)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data


@tool
def get_year_plan(year: int | None = None) -> str:
    """Get annual plan for a year: theme, outcomes, constraints, north star metrics. Defaults to current year."""
    y = year if year is not None else datetime.now().year
    data = _load_year(y)
    if not data.get("year_theme") and not data.get("outcomes"):
        return f"{y} 年尚未設定年度計劃。"
    parts = [f"{y} 年度計劃："]
    if data.get("year_theme"):
        parts.append(f"主題：{data['year_theme']}")
    if data.get("outcomes"):
        parts.append("Outcomes：" + "；".join(str(o) for o in data["outcomes"]))
    if data.get("constraints"):
        parts.append(f"限制：{data['constraints']}")
    if data.get("north_star_metrics"):
        parts.append(f"北極星指標：{data['north_star_metrics']}")
    return "\n".join(parts)


@tool
def set_year_plan(
    year_theme: str | None = None,
    outcomes: list[str] | None = None,
    constraints: str | None = None,
    north_star_metrics: str | None = None,
    year: int | None = None,
) -> str:
    """Save annual plan to storage. MUST be called whenever user provides or you generate year theme or outcomes - otherwise nothing is persisted and year_2026.json stays empty. Parameters: year_theme (one string), outcomes (list of strings), constraints, north_star_metrics, year (int). Defaults to current year if year omitted."""
    y = year if year is not None else datetime.now().year
    data = _load_year(y)
    if year_theme is not None:
        data["year_theme"] = year_theme
    if outcomes is not None:
        data["outcomes"] = outcomes
    if constraints is not None:
        data["constraints"] = constraints
    if north_star_metrics is not None:
        data["north_star_metrics"] = north_star_metrics
    _year_path(y).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"{y} 年度計劃已更新。"


# ---------------------------------------------------------------------------
# Quarter
# ---------------------------------------------------------------------------

def _quarter_path(year: int, quarter: int) -> Path:
    _ensure_dir()
    return _STORAGE_DIR / f"quarter_{year}_q{quarter}.json"


def _default_quarter(year: int, quarter: int) -> dict[str, Any]:
    return {
        "year": year,
        "quarter": quarter,
        "objectives": [],
        "key_results": [],
        "quarter_projects": [],
    }


def _load_quarter(year: int, quarter: int) -> dict[str, Any]:
    p = _quarter_path(year, quarter)
    if not p.exists():
        data = _default_quarter(year, quarter)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _default_quarter(year, quarter)


@tool
def get_quarter_okr(year: int | None = None, quarter: int | None = None) -> str:
    """Get quarter OKR (objectives, key results, projects). Defaults to current year and current quarter (1-4)."""
    now = datetime.now()
    y = year if year is not None else now.year
    q = quarter if quarter is not None else (now.month - 1) // 3 + 1
    data = _load_quarter(y, q)
    if not data.get("objectives") and not data.get("key_results"):
        return f"{y} Q{q} 尚未設定 OKR。"
    parts = [f"{y} Q{q} OKR："]
    if data.get("objectives"):
        parts.append("Objectives：" + "；".join(str(o) for o in data["objectives"]))
    if data.get("key_results"):
        parts.append("Key Results：" + "；".join(str(k) for k in data["key_results"]))
    if data.get("quarter_projects"):
        parts.append("專案/里程碑：" + "；".join(str(p) for p in data["quarter_projects"]))
    return "\n".join(parts)


@tool
def set_quarter_okr(
    objectives: list[str] | None = None,
    key_results: list[str] | None = None,
    quarter_projects: list[str] | None = None,
    year: int | None = None,
    quarter: int | None = None,
) -> str:
    """Set or update quarter OKR. Pass only fields to update. Quarter 1-4. Defaults to current quarter."""
    now = datetime.now()
    y = year if year is not None else now.year
    q = quarter if quarter is not None else (now.month - 1) // 3 + 1
    data = _load_quarter(y, q)
    if objectives is not None:
        data["objectives"] = objectives
    if key_results is not None:
        data["key_results"] = key_results
    if quarter_projects is not None:
        data["quarter_projects"] = quarter_projects
    _quarter_path(y, q).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"{y} Q{q} OKR 已更新。"


# ---------------------------------------------------------------------------
# Week
# ---------------------------------------------------------------------------

def _week_path(year: int, week: int) -> Path:
    _ensure_dir()
    return _STORAGE_DIR / f"week_{year}_w{week}.json"


def _default_week(year: int, week: int) -> dict[str, Any]:
    return {
        "year": year,
        "week": week,
        "weekly_commitments": [],
        "capacity_plan": None,
    }


def _load_week(year: int, week: int) -> dict[str, Any]:
    p = _week_path(year, week)
    if not p.exists():
        data = _default_week(year, week)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _default_week(year, week)


@tool
def get_week_plan(year: int | None = None, week: int | None = None) -> str:
    """Get week plan: commitments (deliverables), capacity. Defaults to current ISO week."""
    now = datetime.now()
    y = year if year is not None else now.year
    w = week if week is not None else now.isocalendar()[1]
    data = _load_week(y, w)
    if not data.get("weekly_commitments") and data.get("capacity_plan") is None:
        return f"{y} 第 {w} 週尚未設定計劃。"
    parts = [f"{y} W{w}："]
    if data.get("weekly_commitments"):
        parts.append("本週 deliverables：" + "；".join(str(c) for c in data["weekly_commitments"]))
    if data.get("capacity_plan") is not None:
        parts.append(f"容量計畫：{data['capacity_plan']}")
    return "\n".join(parts)


@tool
def set_week_plan(
    weekly_commitments: list[str] | None = None,
    capacity_plan: str | None = None,
    year: int | None = None,
    week: int | None = None,
) -> str:
    """Set or update week plan. Defaults to current ISO week."""
    now = datetime.now()
    y = year if year is not None else now.year
    w = week if week is not None else now.isocalendar()[1]
    data = _load_week(y, w)
    if weekly_commitments is not None:
        data["weekly_commitments"] = weekly_commitments
    if capacity_plan is not None:
        data["capacity_plan"] = capacity_plan
    _week_path(y, w).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"{y} W{w} 計劃已更新。"


# ---------------------------------------------------------------------------
# Day
# ---------------------------------------------------------------------------

def _day_path(date_str: str | None = None) -> Path:
    _ensure_dir()
    if date_str:
        return _STORAGE_DIR / f"day_{date_str}.json"
    today = datetime.now().strftime("%Y-%m-%d")
    return _STORAGE_DIR / f"day_{today}.json"


def _default_day(date_str: str) -> dict[str, Any]:
    return {
        "date": date_str,
        "mit": None,
        "top3": [],
        "time_blocks": None,
        "buffer": None,
        "shutdown_checklist": [],
    }


def _load_day(date_str: str | None = None) -> tuple[str, dict[str, Any]]:
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    p = _STORAGE_DIR / f"day_{date_str}.json"
    if not p.exists():
        data = _default_day(date_str)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return date_str, data
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        data.setdefault("date", date_str)
        return date_str, data
    except (json.JSONDecodeError, OSError):
        return date_str, _default_day(date_str)


@tool
def get_day_plan(date: str | None = None) -> str:
    """Get day plan: MIT, Top3, time blocks, buffer, shutdown checklist. Date YYYY-MM-DD; default today."""
    date_str, data = _load_day(date)
    if not data.get("mit") and not data.get("top3"):
        return f"{date_str} 尚未設定每日計劃。"
    parts = [f"{date_str} 計劃："]
    if data.get("mit"):
        parts.append(f"MIT：{data['mit']}")
    if data.get("top3"):
        parts.append("Top3：" + "；".join(str(t) for t in data["top3"]))
    if data.get("time_blocks"):
        parts.append(f"Time blocks：{data['time_blocks']}")
    if data.get("buffer") is not None:
        parts.append(f"Buffer：{data['buffer']}")
    if data.get("shutdown_checklist"):
        parts.append("Shutdown：" + "；".join(str(s) for s in data["shutdown_checklist"]))
    return "\n".join(parts)


@tool
def set_day_plan(
    mit: str | None = None,
    top3: list[str] | None = None,
    time_blocks: str | None = None,
    buffer: str | None = None,
    shutdown_checklist: list[str] | None = None,
    date: str | None = None,
) -> str:
    """Set or update day plan. Date YYYY-MM-DD; default today. Pass only fields to update."""
    date_str, data = _load_day(date)
    if mit is not None:
        data["mit"] = mit
    if top3 is not None:
        data["top3"] = top3
    if time_blocks is not None:
        data["time_blocks"] = time_blocks
    if buffer is not None:
        data["buffer"] = buffer
    if shutdown_checklist is not None:
        data["shutdown_checklist"] = shutdown_checklist
    _day_path(date_str).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"{date_str} 計劃已更新。"
