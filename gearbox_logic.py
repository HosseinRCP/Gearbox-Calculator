"""
منطق محاسبات «دستچین گیربکس»
این فایل هیچ ارتباطی به رابط کاربری ندارد.
"""

import os
import sys
import json
import math
from pathlib import Path

import calculator_logic as logic


# رنگ‌های خطوط دنده‌ها در نمودار
GEAR_COLORS = [
    "#2563eb", "#16a34a", "#dc2626", "#d97706",
    "#7c3aed", "#0891b2", "#db2777", "#65a30d",
]

# شرکت‌هایی که فعلاً غیرفعال هستند (داده واقعی ندارند)
# هر وقت ضرایب سایپا آماده شد، "saipa" را از این مجموعه حذف کن
DISABLED_COMPANIES = {"saipa"}


def _base_dir():
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent


def load_gear_db():
    path = _base_dir() / "assets" / "gear_data.json"
    if not path.is_file():
        return {"gears": [], "diffs": []}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return {"gears": data.get("gears", []), "diffs": data.get("diffs", [])}
    except Exception:
        return {"gears": [], "diffs": []}


def filter_by_company(items, company):
    """
    فیلتر بر اساس شرکت. شرکت‌های غیرفعال کلاً حذف می‌شوند.
    """
    result = []
    for x in items:
        comp = x.get("company")
        if comp in DISABLED_COMPANIES:
            continue
        if company == "all" or comp == company:
            result.append(x)
    return result


def line_slope(total_ratio, tire_cm):
    if tire_cm <= 0:
        return 0.0
    return (100000.0 / (60.0 * tire_cm)) * total_ratio


def rpm_at_speed(speed, total_ratio, tire_cm):
    if tire_cm <= 0:
        return 0.0
    wheel_rpm = (speed * 100000.0 / 60.0) / tire_cm
    return wheel_rpm * total_ratio


def speed_at_rpm(rpm, total_ratio, tire_cm):
    if total_ratio <= 0:
        return 0.0
    wheel_rpm = rpm / total_ratio
    return (tire_cm / 100000.0 * 60.0) * wheel_rpm


def ratio_from_speed_rpm(speed, rpm, diff_ratio, tire_cm):
    if speed <= 0 or rpm <= 0 or tire_cm <= 0 or diff_ratio <= 0:
        return None, None
    wheel_rpm = (speed * 100000.0 / 60.0) / tire_cm
    if wheel_rpm <= 0:
        return None, None
    total = rpm / wheel_rpm
    gear = total / diff_ratio
    return total, gear


def find_closest(target_ratio, gear_db):
    if not gear_db or target_ratio is None:
        return None
    best = None
    best_err = None
    for g in gear_db:
        try:
            err = abs(float(g["ratio"]) - target_ratio)
        except Exception:
            continue
        if best_err is None or err < best_err:
            best_err = err
            best = g
    if best is None:
        return None
    return {
        **best,
        "error": best_err,
        "error_percent": (best_err / target_ratio * 100.0) if target_ratio else 0.0,
    }


def suggest_set(target_totals, gear_db, diff_db, tire_cm):
    if not target_totals or not gear_db or not diff_db:
        return None
    best = None
    for d in diff_db:
        try:
            diff = float(d["ratio"])
        except Exception:
            continue
        if diff <= 0:
            continue
        total_err = 0.0
        picks = []
        ok = True
        for target_total in target_totals:
            target_gear = target_total / diff
            match = find_closest(target_gear, gear_db)
            if match is None:
                ok = False
                break
            achieved_total = float(match["ratio"]) * diff
            total_err += abs(achieved_total - target_total)
            picks.append({
                "gear": match,
                "achieved_total": achieved_total,
                "target_total": target_total,
            })
        if not ok:
            continue
        if best is None or total_err < best["error"]:
            best = {"diff": d, "picks": picks, "error": total_err}
    return best


def suggest_set_by_position(target_by_position, gear_db, diff_db):
    """
    پیشنهاد همزمان دیفرانسیل + دنده‌ها بر اساس موقعیت هر دنده.
    target_by_position: دیکشنری {شماره دنده: ضریب کل}
    وقتی کاربر دیفرانسیل را نمی‌داند استفاده می‌شود.
    """
    if not target_by_position or not gear_db or not diff_db:
        return None
    best = None
    for d in diff_db:
        try:
            diff = float(d["ratio"])
        except Exception:
            continue
        if diff <= 0:
            continue
        total_err = 0.0
        picks = {}
        ok = True
        for pos, target_total in target_by_position.items():
            target_gear = target_total / diff
            candidates = [g for g in gear_db if g.get("position") == pos]
            match = find_closest(target_gear, candidates)
            if match is None:
                ok = False
                break
            achieved = float(match["ratio"]) * diff
            total_err += abs(achieved - target_total)
            picks[pos] = {
                "gear": match,
                "achieved_total": achieved,
                "target_total": target_total,
            }
        if not ok:
            continue
        if best is None or total_err < best["error"]:
            best = {"diff": d, "picks": picks, "error": total_err}
    return best