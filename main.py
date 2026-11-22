"""
نقطه شروع برنامه
"""

import os
import sys

# این خط حتماً باید قبل از وارد کردن فایل‌های خودمان باشد.
# باعث می‌شود اصلاً فایل کش (__pycache__) ساخته نشود.
sys.dont_write_bytecode = True

import shutil
import traceback
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont

from ui_main_window import MainWindow, load_fonts


# این پوشه‌ها هنگام پاک‌سازی کش رد می‌شوند
SKIP_DIRS = {
    "venv", ".venv", "env", ".env",
    "site-packages", "build", "dist",
    ".git", ".idea", ".vscode",
}


def is_frozen():
    """
    آیا برنامه به صورت فایل اجرایی (exe) اجرا شده است؟
    """
    return getattr(sys, "frozen", False)


def app_dir():
    """
    پوشه کنار فایل اجرایی (در نسخه exe)
    یا پوشه کنار فایل برنامه (در حالت اجرا با پایتون)
    """
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def clean_cache():
    """
    پاک‌سازی کش‌های باقی‌مانده از اجرای قبلی.

    نکته‌ها:
    - در نسخه exe اجرا نمی‌شود، چون کش جداگانه‌ای ساخته نمی‌شود
      و فایل‌های موقت را خودِ exe موقع بسته شدن پاک می‌کند.
    - پوشه venv و کتابخانه‌ها پاک نمی‌شوند تا سرعت برنامه کم نشود.
    """
    if is_frozen():
        return

    base = Path(__file__).resolve().parent

    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        if "__pycache__" in dirs:
            shutil.rmtree(Path(root) / "__pycache__", ignore_errors=True)
            dirs.remove("__pycache__")

        for name in files:
            if name.endswith(".pyc"):
                try:
                    (Path(root) / name).unlink(missing_ok=True)
                except Exception:
                    pass


def set_windows_taskbar_id():
    """
    روی ویندوز باعث می‌شود آیکون خود برنامه در نوار وظیفه
    نمایش داده شود، نه آیکون پایتون.
    """
    if os.name != "nt":
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "GRS.GearboxCalculator"
        )
    except Exception:
        pass


def log_uncaught_exception(exc_type, exc_value, exc_tb):
    """
    در نسخه exe بدون کنسول، خطاها دیده نمی‌شوند.
    اینجا متن خطا در error_log.txt ذخیره می‌شود
    تا بتوان آن را بررسی و رفع کرد.
    """
    text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

    try:
        with open(app_dir() / "error_log.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass

    try:
        if QApplication.instance() is not None:
            QMessageBox.critical(None, "Error", text[-1500:])
    except Exception:
        pass

    try:
        sys.__excepthook__(exc_type, exc_value, exc_tb)
    except Exception:
        pass


def main():
    set_windows_taskbar_id()
    sys.excepthook = log_uncaught_exception

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Gearbox Ratio Calculator")

    # بارگذاری فونت Shabnam از پوشه fonts
    # (حتماً بعد از ساخت QApplication انجام شود)
    font_family, regular_font, bold_font = load_fonts("Shabnam")
    app.setFont(QFont(font_family, 10))

    window = MainWindow(font_family, regular_font, bold_font)
    window.show()

    try:
        exit_code = app.exec()
    finally:
        # موقع بسته شدن برنامه، کش‌های قدیمی پاک شوند
        clean_cache()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()