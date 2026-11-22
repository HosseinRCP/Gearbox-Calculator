"""
ذخیره و بازیابی پریست‌ها.
پریست‌ها در پوشه اختصاصی برنامه (AppData) ذخیره می‌شوند،
نه کنار فایل اجرایی و نه داخل پوشه پروژه.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


APP_NAME = "GearboxCalculator"


def preset_dir():
    """
    پوشه ذخیره پریست‌ها در پروفایل کاربر
    """
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    d = base / APP_NAME / "presets"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return d


def list_presets():
    """
    لیست اسم پریست‌های ذخیره‌شده
    """
    d = preset_dir()
    try:
        return sorted(p.stem for p in d.glob("*.json"))
    except Exception:
        return []


def save_preset(name, data):
    """
    ذخیره پریست. حتی اگر بعضی فیلدها خالی باشند ذخیره می‌شود.
    """
    name = str(name).strip() or "preset"
    path = preset_dir() / f"{name}.json"
    payload = {
        "meta": {"name": name, "updated": datetime.now().isoformat()},
        "data": data,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def load_preset(name):
    """
    خواندن پریست. اگر نبود یا خراب بود، None برمی‌گرداند.
    """
    path = preset_dir() / f"{name}.json"
    if not path.is_file():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        return payload.get("data", {})
    except Exception:
        return None


def delete_preset(name):
    """
    حذف پریست
    """
    path = preset_dir() / f"{name}.json"
    try:
        path.unlink(missing_ok=True)
        return True
    except Exception:
        return False