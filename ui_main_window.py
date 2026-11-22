"""
فایل رابط کاربری
پنجره اصلی با دو حالت: محاسبه‌گر (آبی) و دستچین گیربکس (قرمز)
"""

import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFontDatabase, QIcon, QPixmap, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QGroupBox, QTabWidget,
    QMessageBox, QFileDialog, QScrollArea, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect, QStackedWidget,
)

import fpdf as fpdf_module
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

import calculator_logic as logic
import gearbox_logic as glogic
from ui_gearbox_builder import GearboxBuilderWidget


# -------------------------------------------------
# فقط fpdf2 نسخه ۲.۸ به بالا پذیرفته می‌شود
# -------------------------------------------------
FPDF2_MIN_VERSION = (2, 8)
FPDF2_VERSION_TEXT = str(getattr(fpdf_module, "__version__", "unknown"))


def _pdf_lib_version():
    numbers = []
    for chunk in FPDF2_VERSION_TEXT.split(".")[:2]:
        digits = ""
        for ch in chunk:
            if ch.isdigit():
                digits += ch
            else:
                break
        numbers.append(int(digits) if digits else 0)
    while len(numbers) < 2:
        numbers.append(0)
    return tuple(numbers)


FPDF2_OK = _pdf_lib_version() >= FPDF2_MIN_VERSION


# -------------------------------------------------
# ترجمه‌ها
# -------------------------------------------------
TRANSLATIONS = {
    "en": {
        "app_title": "Gearbox Ratio Calculator",
        "menu": "Menu", "settings": "Settings", "language": "Language",
        "input_mode": "Gear/Diff input method", "theme": "Theme",
        "theme_light": "Light", "theme_dark": "Dark",
        "code": "Code", "ratio": "Ratio",
        "tab_speed_from_rpm": "Speed from RPM",
        "tab_rpm_from_speed": "RPM from Speed",
        "tab_missing_ratio": "Missing ratio",
        "rpm": "Engine RPM", "speed": "Vehicle speed (km/h)",
        "gear_code": "Gear code (e.g. 4735 = 35/47)",
        "diff_code": "Diff code (e.g. 1041 = 41/10)",
        "gear_ratio": "Gear ratio (e.g. 0.745)",
        "diff_ratio": "Diff ratio (e.g. 4.10)",
        "ring": "Ring size (inch)",
        "sidewall": "Tire sidewall (%)",
        "pahna": "Tire width (mm)",
        "known_side": "Which ratio do you have?",
        "known_diff": "I have Diff", "known_gear": "I have Gear",
        "calculate_speed": "Calculate Speed",
        "calculate_rpm": "Calculate RPM",
        "calculate_missing": "Calculate missing ratio",
        "result": "Result",
        "speed_result": "Speed", "rpm_result": "Engine RPM",
        "total_ratio_result": "Total ratio",
        "gear_ratio_result": "Gear ratio",
        "diff_ratio_result": "Diff ratio",
        "suggested_code": "Suggested code",
        "copy_result": "Copy Result",
        "copied": "Result copied to clipboard.",
        "no_result": "No result to copy.",
        "pdf_language": "PDF language",
        "pdf_en": "English", "pdf_fa": "Persian",
        "pdf_both": "Both (English first)",
        "invalid_number": "Please enter all numbers correctly.",
        "invalid_code": "Code must be 4 digits, e.g. 4735.",
        "invalid_ratio": "Ratio must be a positive number like 0.745.",
        "save_pdf": "Save PDF",
        "pdf_saved": "PDF file saved.",
        "pdf_error": "Error saving PDF.",
        "error": "Error",
        "choose_persian_font": "Choose a Persian TTF font",
        "pdf_font_missing_title": "Persian font not found",
        "pdf_font_missing": "No Persian font found. Choose a .ttf Persian font, for example Shabnam.ttf.",
        "pdf_save_title": "Save PDF file",
        "pdf_filter": "PDF files (*.pdf)",
        "close_menu": "Close menu",
        "manufacturer": "Manufacturer",
        "company_all": "All companies",
        "company_saipa": "SAIPA",
        "company_ikco": "IKCO",
        "mode_builder": "🔧 Gearbox Builder",
        "mode_calculator": "📊 Ratio Calculator",
        "disclaimer": "These calculations assume ideal conditions; wheel rolling circumference and clutch disc slippage are not accounted for.",
    },
    "fa": {
        "app_title": "محاسبه‌گر ضریب گیربکس",
        "menu": "منو", "settings": "تنظیمات", "language": "زبان",
        "input_mode": "روش ورود ضریب دنده/دیفرانسیل", "theme": "پوسته",
        "theme_light": "روشن", "theme_dark": "تاریک",
        "code": "کد", "ratio": "ضریب",
        "tab_speed_from_rpm": "سرعت از دور موتور",
        "tab_rpm_from_speed": "دور موتور از سرعت",
        "tab_missing_ratio": "ضریب گمشده",
        "rpm": "دور موتور", "speed": "سرعت خودرو (کیلومتر/ساعت)",
        "gear_code": "کد دنده (مثلاً 4735 = 35/47)",
        "diff_code": "کد دیفرانسیل (مثلاً 1041 = 41/10)",
        "gear_ratio": "ضریب دنده (مثلاً 0.745)",
        "diff_ratio": "ضریب دیفرانسیل (مثلاً 4.10)",
        "ring": "سایز رینگ (اینچ)",
        "sidewall": "فاق تایر (%)",
        "pahna": "پهنای لاستیک (میلی‌متر)",
        "known_side": "کدام ضریب را دارید؟",
        "known_diff": "ضریب دیفرانسیل را دارم",
        "known_gear": "ضریب دنده را دارم",
        "calculate_speed": "محاسبه سرعت",
        "calculate_rpm": "محاسبه دور موتور",
        "calculate_missing": "محاسبه ضریب گمشده",
        "result": "نتیجه",
        "speed_result": "سرعت", "rpm_result": "دور موتور",
        "total_ratio_result": "ضریب کل",
        "gear_ratio_result": "ضریب دنده",
        "diff_ratio_result": "ضریب دیفرانسیل",
        "suggested_code": "کد پیشنهادی",
        "copy_result": "کپی نتیجه",
        "copied": "نتیجه در کلیپ‌بورد کپی شد.",
        "no_result": "نتیجه‌ای برای کپی وجود ندارد.",
        "pdf_language": "زبان خروجی PDF",
        "pdf_en": "انگلیسی", "pdf_fa": "فارسی",
        "pdf_both": "هر دو (اول انگلیسی)",
        "invalid_number": "لطفاً همه عددها را درست وارد کنید.",
        "invalid_code": "کد باید ۴ رقم باشد، مثلاً 4735.",
        "invalid_ratio": "ضریب باید عدد مثبت باشد، مثلاً 0.745.",
        "save_pdf": "ذخیره PDF",
        "pdf_saved": "فایل PDF ذخیره شد.",
        "pdf_error": "خطا در ذخیره PDF.",
        "error": "خطا",
        "choose_persian_font": "انتخاب فونت فارسی TTF",
        "pdf_font_missing_title": "فونت فارسی پیدا نشد",
        "pdf_font_missing": "فونت فارسی پیدا نشد. یک فایل فونت .ttf فارسی انتخاب کنید، مثلاً Shabnam.ttf.",
        "pdf_save_title": "ذخیره فایل PDF",
        "pdf_filter": "فایل PDF (*.pdf)",
        "close_menu": "بستن منو",
        "manufacturer": "شرکت سازنده",
        "company_all": "همه شرکت‌ها",
        "company_saipa": "سایپا",
        "company_ikco": "ایران خودرو",
        "mode_builder": "🔧 دستچین گیربکس",
        "mode_calculator": "📊 محاسبه ضریب",
        "disclaimer": "این محاسبات در حالت ایده‌آل است؛ محیط غلتشی چرخ و لغزش دیسک و صفحه در این محاسبه اعمال نشده است.",
    },
}

TONES = {
    "light": {
        "success": "#15803d", "info": "#1d4ed8",
        "missing": "#047857", "error": "#dc2626",
    },
    "dark": {
        "success": "#4ade80", "info": "#60a5fa",
        "missing": "#34d399", "error": "#f87171",
    },
}

MENU_WIDTH = 280
CONTENT_MAX_WIDTH = 760


# -------------------------------------------------
# توابع کمکی
# -------------------------------------------------
def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent


def get_asset_path(filename):
    path = get_base_dir() / "assets" / filename
    if path.is_file():
        return str(path)
    return None


LOG_FILE_NAME = "error_log.txt"
LOG_MAX_CHARS = 100_000


def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def write_log(text):
    try:
        from datetime import datetime
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"===== {stamp} =====\n{text}\n"
        path = app_dir() / LOG_FILE_NAME
        old = ""
        if path.is_file():
            try:
                old = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                old = ""
        data = old + entry
        if len(data) > LOG_MAX_CHARS:
            data = data[-LOG_MAX_CHARS:]
        path.write_text(data, encoding="utf-8")
    except Exception:
        pass


def load_fonts(preferred="Shabnam"):
    fonts_dir = get_base_dir() / "fonts"
    loaded = []
    if fonts_dir.is_dir():
        for path in sorted(fonts_dir.iterdir()):
            if path.suffix.lower() in (".ttf", ".otf"):
                font_id = QFontDatabase.addApplicationFont(str(path))
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        loaded.append((path, families))

    def is_bold(p):
        return any(w in p.stem.lower() for w in ("bold", "fat", "heavy"))

    regular = next(
        (item for item in loaded
         if preferred.lower() in item[0].stem.lower() and not is_bold(item[0])),
        None,
    )
    if regular is None:
        regular = next((item for item in loaded if not is_bold(item[0])), None)
    if regular is None and loaded:
        regular = loaded[0]

    bold = next(
        (item for item in loaded
         if preferred.lower() in item[0].stem.lower() and is_bold(item[0])),
        None,
    )
    if bold is None:
        bold = next((item for item in loaded if is_bold(item[0])), None)

    family = "Segoe UI" if os.name == "nt" else "DejaVu Sans"
    regular_path = bold_path = None
    if regular:
        regular_path = regular[0]
        family = next(
            (f for f in regular[1] if preferred.lower() in f.lower()),
            regular[1][0],
        )
    if bold:
        bold_path = bold[0]
    return family, regular_path, bold_path


def shape_fa_text(text):
    lines = str(text).split("\n")
    return "\n".join(
        get_display(arabic_reshaper.reshape(line)) for line in lines
    )


def theme_colors(theme):
    if theme == "dark":
        return {
            "bg": "#0f172a", "card": "#111827", "input_bg": "#1e293b",
            "fg": "#f8fafc", "muted": "#94a3b8", "border": "#334155",
            "primary": "#3b82f6", "primary_hover": "#2563eb",
            "success": "#22c55e", "success_hover": "#16a34a",
            "info": "#38bdf8", "info_hover": "#0ea5e9",
            "warning": "#f59e0b", "warning_hover": "#d97706",
            "disabled": "#334155", "disabled_fg": "#94a3b8",
            "result_bg": "#1e293b", "menu_bg": "#111827",
            "overlay": "rgba(0, 0, 0, 120)",
        }
    return {
        "bg": "#f3f6fb", "card": "#ffffff", "input_bg": "#ffffff",
        "fg": "#0f172a", "muted": "#64748b", "border": "#dbe2ea",
        "primary": "#2563eb", "primary_hover": "#1d4ed8",
        "success": "#16a34a", "success_hover": "#15803d",
        "info": "#0891b2", "info_hover": "#0e7490",
        "warning": "#d97706", "warning_hover": "#b45309",
        "disabled": "#cbd5e1", "disabled_fg": "#64748b",
        "result_bg": "#f8fafc", "menu_bg": "#ffffff",
        "overlay": "rgba(15, 23, 42, 90)",
    }


def get_stylesheet(theme):
    c = theme_colors(theme)
    return f"""
    QMainWindow, QWidget#CentralWidget {{
        background-color: {c['bg']};
    }}
    QWidget {{
        color: {c['fg']};
        font-size: 10pt;
    }}
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QWidget#ScrollViewport, QWidget#TabContent, QStackedWidget {{
        background: transparent;
    }}
    QGroupBox {{
        border: 1px solid {c['border']};
        border-radius: 14px;
        margin-top: 16px;
        padding: 14px 12px 12px 12px;
        background-color: {c['card']};
        font-weight: 700;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 1px 10px;
        color: {c['primary']};
        background-color: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 8px;
    }}
    QTabWidget::pane {{
        border: 1px solid {c['border']};
        border-radius: 14px;
        background-color: {c['card']};
        top: -1px;
    }}
    QTabBar::tab {{
        padding: 8px 16px;
        margin: 2px 4px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        color: {c['muted']};
        background: transparent;
    }}
    QTabBar::tab:hover {{ color: {c['fg']}; }}
    QTabBar::tab:selected {{
        background-color: {c['card']};
        color: {c['fg']};
        border: 1px solid {c['border']};
        border-bottom: 2px solid {c['primary']};
    }}
    QLabel {{ background: transparent; }}
    QLabel#FieldLabel {{ color: {c['muted']}; padding-bottom: 2px; }}
    QLineEdit, QComboBox {{
        background-color: {c['input_bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        padding: 9px 12px;
        min-height: 22px;
        color: {c['fg']};
        selection-background-color: {c['primary']};
    }}
    QLineEdit:focus, QComboBox:focus {{ border: 1.5px solid {c['primary']}; }}
    QComboBox::drop-down {{ border: none; width: 26px; }}
    QComboBox QAbstractItemView {{
        background-color: {c['card']};
        color: {c['fg']};
        border: 1px solid {c['border']};
        selection-background-color: {c['primary']};
        selection-color: white;
        outline: none;
        padding: 4px;
    }}
    QPushButton {{
        border: none;
        border-radius: 10px;
        padding: 10px 16px;
        font-weight: 700;
        background-color: {c['primary']};
        color: white;
    }}
    QPushButton:hover {{ background-color: {c['primary_hover']}; }}
    QPushButton:disabled {{ background-color: {c['disabled']}; color: {c['disabled_fg']}; }}
    QPushButton#SuccessButton {{ background-color: {c['success']}; }}
    QPushButton#SuccessButton:hover {{ background-color: {c['success_hover']}; }}
    QPushButton#InfoButton {{ background-color: {c['info']}; }}
    QPushButton#InfoButton:hover {{ background-color: {c['info_hover']}; }}
    QPushButton#WarningButton {{ background-color: {c['warning']}; }}
    QPushButton#WarningButton:hover {{ background-color: {c['warning_hover']}; }}
    QPushButton#MenuButton {{
        background-color: transparent;
        color: {c['fg']};
        font-size: 16pt;
        font-weight: 400;
        padding: 4px 10px;
        border-radius: 8px;
    }}
    QPushButton#MenuButton:hover {{ background-color: {c['input_bg']}; }}
    QPushButton#CloseMenuButton {{
        background-color: transparent;
        color: {c['muted']};
        font-size: 13pt;
        padding: 2px 8px;
    }}
    QPushButton#CloseMenuButton:hover {{ color: {c['fg']}; background-color: {c['input_bg']}; }}
    QLabel#ResultLabel {{
        background-color: {c['result_bg']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        padding: 14px;
        font-size: 13pt;
        font-weight: 800;
    }}
    QLabel#StatusLabel {{ padding: 4px 8px; color: {c['muted']}; }}
    QLabel#HeaderTitle {{ font-size: 13pt; font-weight: 800; }}
    QFrame#SideMenu {{
        background-color: {c['menu_bg']};
        border: 1px solid {c['border']};
    }}
    QFrame#Overlay {{ background-color: {c['overlay']}; }}
    QLabel#MenuTitle {{ font-size: 12pt; font-weight: 800; color: {c['primary']}; }}
    QLabel#MenuDisclaimer {{ color: {c['muted']}; font-size: 8.5pt; padding: 8px 4px 2px 4px; border-top: 1px solid {c['border']}; }}
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: {c['border']}; border-radius: 5px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: {c['muted']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """


class _Overlay(QFrame):
    """
    لایه تیره پشت منو.
    کلیک روی آن منو را نمی‌بندد؛ منو فقط با دکمه ✕ (یا Esc) بسته می‌شود.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("Overlay")

    def mousePressEvent(self, event):
        event.accept()


# -------------------------------------------------
# پنجره اصلی
# -------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, font_family, pdf_font_path=None, pdf_bold_path=None):
        super().__init__()

        self.font_family = font_family
        self.pdf_font_path = str(pdf_font_path) if pdf_font_path else None
        self.pdf_bold_path = str(pdf_bold_path) if pdf_bold_path else None

        self.lang = "fa"
        self.theme = "light"
        self.input_mode = "code"
        self.pdf_lang = "both"
        self.known_side = "diff"
        self.app_mode = "calculator"
        self.missing_company = "all"

        # دیتابیس دنده‌ها برای پیشنهاد کد در بخش محاسبه ضریب گمشده
        self.gear_db = glogic.load_gear_db()

        self.values = {
            "rpm": "", "speed": "",
            "gear_code": "", "gear_ratio": "",
            "diff_code": "", "diff_ratio": "",
            "ring": "", "sidewall": "", "pahna": "",
        }

        self.result_texts = self.empty_results()
        self.result_tones = {
            "speed": "success", "rpm": "info", "missing": "missing",
        }
        self.result_labels = {}

        self.status_timer = QTimer(self)
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.clear_status)

        self.setMinimumSize(560, 600)
        self.resize(720, 780)

        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.center() - self.rect().center())

        icon_path = get_asset_path("icon.ico") or get_asset_path("GRSLogo.png")
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        self.logo_path = get_asset_path("GRSLogo.png")

        self.apply_theme()

        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle(self.t("app_title"))

        self._build_chrome()
        self._rebuild_calculator()
        self.restore_results()
        self._build_menu_shell()

    # -----------------------------
    # توابع عمومی
    # -----------------------------
    def empty_results(self):
        return {
            "speed": {"en": "", "fa": ""},
            "rpm": {"en": "", "fa": ""},
            "missing": {"en": "", "fa": ""},
        }

    def t(self, key):
        return TRANSLATIONS[self.lang].get(key, key)

    def tone(self, name):
        return TONES[self.theme].get(name, TONES[self.theme]["info"])

    def is_rtl(self):
        return self.lang == "fa"

    def set_value(self, key, text):
        self.values[key] = text

    def ratio_field_keys(self, side):
        suffix = "code" if self.input_mode == "code" else "ratio"
        key = f"{side}_{suffix}"
        return key, key

    def apply_theme(self):
        QApplication.instance().setStyleSheet(get_stylesheet(self.theme))

    def set_status(self, text, tone_name=None):
        self.status_label.setText(text)
        if tone_name:
            self.status_label.setStyleSheet(
                f"color: {self.tone(tone_name)}; padding: 4px 8px;"
            )
        else:
            self.status_label.setStyleSheet("")
        self.status_timer.start(5000)

    def clear_status(self):
        self.status_label.setText("")
        self.status_label.setStyleSheet("")

    # -----------------------------
    # ساخت اسکلت اصلی (یک‌بار)
    # -----------------------------
    def _build_chrome(self):
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(16, 12, 16, 10)
        outer.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(8)

        self.menu_btn = QPushButton("\u2630")
        self.menu_btn.setObjectName("MenuButton")
        self.menu_btn.setToolTip(self.t("menu"))
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.setFixedWidth(46)
        self.menu_btn.clicked.connect(self.toggle_menu)
        header.addWidget(self.menu_btn)

        self.header_title = QLabel(self.t("app_title"))
        self.header_title.setObjectName("HeaderTitle")
        header.addWidget(self.header_title)
        header.addStretch(1)

        if self.logo_path:
            pixmap = QPixmap(self.logo_path)
            if not pixmap.isNull():
                logo = QLabel()
                logo.setPixmap(pixmap.scaled(
                    40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
                header.addWidget(logo)

        outer.addLayout(header)

        self.stack = QStackedWidget()

        self.calc_container = QWidget()
        calc_layout = QVBoxLayout(self.calc_container)
        calc_layout.setContentsMargins(0, 0, 0, 0)
        calc_layout.setSpacing(10)
        self.stack.addWidget(self.calc_container)

        self.builder_widget = GearboxBuilderWidget(self.font_family, self.theme, self.lang)
        self.stack.addWidget(self.builder_widget)

        outer.addWidget(self.stack, 1)

        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel")
        outer.addWidget(self.status_label)

    # -----------------------------
    # بازسازی بخش محاسبه‌گر
    # -----------------------------
    def rebuild_ui(self, clear_results=True):
        if clear_results:
            self.result_texts = self.empty_results()

        self.setLayoutDirection(
            Qt.RightToLeft if self.is_rtl() else Qt.LeftToRight
        )
        self.setWindowTitle(self.t("app_title"))
        self.header_title.setText(self.t("app_title"))
        self.menu_btn.setToolTip(self.t("menu"))

        self._rebuild_calculator()
        self.restore_results()
        self._fill_menu()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self._clear_layout(item.layout())

    def _rebuild_calculator(self):
        layout = self.calc_container.layout()
        self._clear_layout(layout)

        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.result_labels = {}

        self.tabs.addTab(self.build_speed_tab(), self.t("tab_speed_from_rpm"))
        self.tabs.addTab(self.build_rpm_tab(), self.t("tab_rpm_from_speed"))
        self.tabs.addTab(self.build_missing_tab(), self.t("tab_missing_ratio"))

        layout.addWidget(self.tabs, 1)

    def make_combo(self, items, current_data, callback):
        combo = QComboBox()
        for data, text in items:
            combo.addItem(text, data)
        index = combo.findData(current_data)
        if index >= 0:
            combo.setCurrentIndex(index)
        combo.activated.connect(
            lambda idx, c=combo, cb=callback: cb(c.itemData(idx))
        )
        return combo

    def create_tab_widget(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        scroll.viewport().setObjectName("ScrollViewport")

        content = QWidget()
        content.setObjectName("TabContent")
        content.setMaximumWidth(CONTENT_MAX_WIDTH)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        scroll.setWidget(content)
        return scroll, layout

    def add_field(self, layout, label_key, value_key):
        label = QLabel(self.t(label_key))
        label.setObjectName("FieldLabel")
        layout.addWidget(label)

        entry = QLineEdit(self.values.get(value_key, ""))
        entry.setPlaceholderText(self.t(label_key))
        entry.setMinimumHeight(42)
        entry.setClearButtonEnabled(True)
        entry.textChanged.connect(
            lambda text, key=value_key: self.set_value(key, text)
        )
        entry.returnPressed.connect(self.on_enter_pressed)
        layout.addWidget(entry)
        return entry

    def on_enter_pressed(self):
        idx = self.tabs.currentIndex()
        if idx == 0:
            self.calculate_speed()
        elif idx == 1:
            self.calculate_rpm()
        else:
            self.calculate_missing()

    def add_result_group(self, layout, result_key):
        result_group = QGroupBox(self.t("result"))
        result_layout = QVBoxLayout(result_group)

        result_label = QLabel("")
        result_label.setObjectName("ResultLabel")
        result_label.setWordWrap(True)
        result_label.setAlignment(Qt.AlignCenter)
        result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        result_label.setMinimumHeight(64)
        result_layout.addWidget(result_label)
        layout.addWidget(result_group)

        actions = QHBoxLayout()
        copy_btn = QPushButton(self.t("copy_result"))
        copy_btn.setObjectName("InfoButton")
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(
            lambda checked=False, key=result_key: self.copy_result(key)
        )
        pdf_btn = QPushButton(self.t("save_pdf"))
        pdf_btn.setObjectName("WarningButton")
        pdf_btn.setCursor(Qt.PointingHandCursor)
        pdf_btn.clicked.connect(
            lambda checked=False, key=result_key: self.save_pdf(key)
        )
        actions.addWidget(copy_btn)
        actions.addWidget(pdf_btn)
        actions.addStretch(1)
        layout.addLayout(actions)
        layout.addStretch(1)

        self.result_labels[result_key] = result_label

    def build_speed_tab(self):
        scroll, layout = self.create_tab_widget()
        self.add_field(layout, "rpm", "rpm")
        gk, gv = self.ratio_field_keys("gear")
        dk, dv = self.ratio_field_keys("diff")
        self.add_field(layout, gk, gv)
        self.add_field(layout, dk, dv)
        self.add_field(layout, "ring", "ring")
        self.add_field(layout, "sidewall", "sidewall")
        self.add_field(layout, "pahna", "pahna")

        btn = QPushButton(self.t("calculate_speed"))
        btn.setObjectName("SuccessButton")
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.calculate_speed)
        layout.addWidget(btn)

        self.add_result_group(layout, "speed")
        return scroll

    def build_rpm_tab(self):
        scroll, layout = self.create_tab_widget()
        self.add_field(layout, "speed", "speed")
        gk, gv = self.ratio_field_keys("gear")
        dk, dv = self.ratio_field_keys("diff")
        self.add_field(layout, gk, gv)
        self.add_field(layout, dk, dv)
        self.add_field(layout, "ring", "ring")
        self.add_field(layout, "sidewall", "sidewall")
        self.add_field(layout, "pahna", "pahna")

        btn = QPushButton(self.t("calculate_rpm"))
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.calculate_rpm)
        layout.addWidget(btn)

        self.add_result_group(layout, "rpm")
        return scroll

    def build_missing_tab(self):
        scroll, layout = self.create_tab_widget()
        self.add_field(layout, "speed", "speed")
        self.add_field(layout, "rpm", "rpm")
        self.add_field(layout, "ring", "ring")
        self.add_field(layout, "sidewall", "sidewall")
        self.add_field(layout, "pahna", "pahna")

        # انتخاب شرکت سازنده برای پیشنهاد کد
        mfg_label = QLabel(self.t("manufacturer"))
        mfg_label.setObjectName("FieldLabel")
        layout.addWidget(mfg_label)
        mfg_combo = self.make_combo(
            [
                ("all", self.t("company_all")),
                ("saipa", self.t("company_saipa")),
                ("ikco", self.t("company_ikco")),
            ],
            self.missing_company,
            self.on_missing_company,
        )
        self._disable_company_options(mfg_combo)
        layout.addWidget(mfg_combo)

        known_label = QLabel(self.t("known_side"))
        known_label.setObjectName("FieldLabel")
        layout.addWidget(known_label)
        known_combo = self.make_combo(
            [("diff", self.t("known_diff")), ("gear", self.t("known_gear"))],
            self.known_side,
            self.on_known_side,
        )
        layout.addWidget(known_combo)

        kk, kv = self.ratio_field_keys(self.known_side)
        self.add_field(layout, kk, kv)

        btn = QPushButton(self.t("calculate_missing"))
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.calculate_missing)
        layout.addWidget(btn)

        self.add_result_group(layout, "missing")
        return scroll

    def restore_results(self):
        for key, label in self.result_labels.items():
            text = self.result_texts.get(key, {}).get(self.lang, "")
            if text:
                label.setText(text)
                label.setStyleSheet(
                    f"color: {self.tone(self.result_tones.get(key, 'info'))};"
                )
            else:
                label.setText("")
                label.setStyleSheet("")

    # -----------------------------
    # منوی کشویی
    # -----------------------------
    def _build_menu_shell(self):
        self.overlay = _Overlay(self.centralWidget())
        self.overlay.hide()

        self.side_menu = QFrame(self.centralWidget())
        self.side_menu.setObjectName("SideMenu")
        self.side_menu.setFixedWidth(MENU_WIDTH)
        self.side_menu.hide()

        shadow = QGraphicsDropShadowEffect(self.side_menu)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 90))
        shadow.setOffset(0, 4)
        self.side_menu.setGraphicsEffect(shadow)

        self.menu_layout = QVBoxLayout(self.side_menu)
        self.menu_layout.setContentsMargins(18, 14, 18, 18)
        self.menu_layout.setSpacing(10)

        self._menu_anim = QPropertyAnimation(
            self.side_menu, b"pos", self.side_menu
        )
        self._menu_anim.setDuration(220)
        self._menu_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._menu_anim.finished.connect(self._on_menu_anim_finished)
        self._menu_open = False
        self._menu_closing = False

        self._fill_menu()

    def _fill_menu(self):
        self._clear_layout(self.menu_layout)

        top = QHBoxLayout()
        title = QLabel(self.t("settings"))
        title.setObjectName("MenuTitle")
        top.addWidget(title)
        top.addStretch(1)
        close_btn = QPushButton("\u2715")
        close_btn.setObjectName("CloseMenuButton")
        close_btn.setToolTip(self.t("close_menu"))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedWidth(36)
        close_btn.clicked.connect(self.close_menu)
        top.addWidget(close_btn)
        self.menu_layout.addLayout(top)

        # دکمه تغییر حالت (قرمز/آبی) به جای کمبو
        self.mode_btn = QPushButton()
        self.mode_btn.setCursor(Qt.PointingHandCursor)
        self.mode_btn.clicked.connect(self._toggle_mode)
        self._update_mode_button()
        self.menu_layout.addWidget(self.mode_btn)
        self.menu_layout.addStretch(1)

        # سلب مسئولیت در پایین منو (دوزبانه)
        disclaimer = QLabel(self.t("disclaimer"))
        disclaimer.setObjectName("MenuDisclaimer")
        disclaimer.setWordWrap(True)
        self.menu_layout.addWidget(disclaimer)

        def add_setting(label_key, combo):
            lbl = QLabel(self.t(label_key))
            lbl.setObjectName("FieldLabel")
            self.menu_layout.addWidget(lbl)
            self.menu_layout.addWidget(combo)

        add_setting("language", self.make_combo(
            [("fa", "فارسی"), ("en", "English")],
            self.lang, self.on_language,
        ))
        add_setting("theme", self.make_combo(
            [("light", self.t("theme_light")), ("dark", self.t("theme_dark"))],
            self.theme, self.on_theme,
        ))
        add_setting("input_mode", self.make_combo(
            [("code", self.t("code")), ("ratio", self.t("ratio"))],
            self.input_mode, self.on_input_mode,
        ))
        add_setting("pdf_language", self.make_combo(
            [("both", self.t("pdf_both")), ("fa", self.t("pdf_fa")),
             ("en", self.t("pdf_en"))],
            self.pdf_lang, self.on_pdf_lang,
        ))

        self.menu_layout.addStretch(1)

    def _update_mode_button(self):
        """
        دکمه همیشه حالتی را نشان می‌دهد که با کلیک به آن می‌روید.
        """
        if self.app_mode == "calculator":
            self.mode_btn.setText(self.t("mode_builder"))
            self.mode_btn.setStyleSheet(
                "QPushButton{background-color:#dc2626;color:white;border:none;"
                "border-radius:10px;padding:11px 16px;font-weight:800;font-size:11pt;}"
                "QPushButton:hover{background-color:#b91c1c;}"
            )
        else:
            self.mode_btn.setText(self.t("mode_calculator"))
            self.mode_btn.setStyleSheet(
                "QPushButton{background-color:#2563eb;color:white;border:none;"
                "border-radius:10px;padding:11px 16px;font-weight:800;font-size:11pt;}"
                "QPushButton:hover{background-color:#1d4ed8;}"
            )
            
    def _toggle_mode(self):
        if self.app_mode == "calculator":
            self.app_mode = "builder"
            self.builder_widget.set_theme(self.theme)
            self.stack.setCurrentWidget(self.builder_widget)
        else:
            self.app_mode = "calculator"
            self.stack.setCurrentWidget(self.calc_container)
        self._update_mode_button()

    def _menu_positions(self):
        parent = self.centralWidget()
        self.side_menu.setFixedHeight(parent.height())
        if self.is_rtl():
            return parent.width(), parent.width() - MENU_WIDTH
        return -MENU_WIDTH, 0

    def toggle_menu(self):
        if not hasattr(self, "_menu_open"):
            return
        if self._menu_open:
            self.close_menu()
        else:
            self.open_menu()

    def open_menu(self):
        self._fill_menu()
        parent = self.centralWidget()
        self.overlay.setGeometry(parent.rect())
        self.overlay.show()
        self.overlay.raise_()

        closed_x, open_x = self._menu_positions()
        if not self.side_menu.isVisible():
            self.side_menu.move(closed_x, 0)
        self.side_menu.show()
        self.side_menu.raise_()

        self._menu_anim.stop()
        self._menu_anim.setStartValue(self.side_menu.pos())
        self._menu_anim.setEndValue(QPoint(open_x, 0))
        self._menu_closing = False
        self._menu_anim.start()
        self._menu_open = True

    def close_menu(self):
        """
        بستن منو — فقط با دکمه ✕، کلید Esc یا دکمه ☰ صدا زده می‌شود.
        حتی اگر وضعیت داخلی ناهماهنگ باشد، تا منو دیده می‌شود آن را می‌بندد.
        """
        if not hasattr(self, "side_menu"):
            return
        if not self.side_menu.isVisible() and not self.overlay.isVisible():
            self._menu_open = False
            self._menu_closing = False
            return

        closed_x, _ = self._menu_positions()
        self._menu_anim.stop()
        self._menu_anim.setStartValue(self.side_menu.pos())
        self._menu_anim.setEndValue(QPoint(closed_x, 0))
        self._menu_closing = True
        self._menu_open = False
        self._menu_anim.start()

        # سوپاپ اطمینان: اگر انیمیشن به هر دلیلی تمام نشد، منو حتماً مخفی شود
        QTimer.singleShot(400, self._ensure_menu_hidden)

    def _ensure_menu_hidden(self):
        """
        اگر انیمیشن بسته شدن کامل نشد، منو را به زور مخفی می‌کند
        تا دیگر حالت «منو باز می‌ماند و بسته نمی‌شود» پیش نیاید.
        """
        if getattr(self, "_menu_closing", False) and not getattr(self, "_menu_open", False):
            if hasattr(self, "_menu_anim"):
                self._menu_anim.stop()
            if hasattr(self, "side_menu"):
                self.side_menu.hide()
            if hasattr(self, "overlay"):
                self.overlay.hide()
            self._menu_closing = False

    def _on_menu_anim_finished(self):
        if self._menu_closing:
            self.side_menu.hide()
            self.overlay.hide()
            self._menu_closing = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, "overlay"):
            return
        parent = self.centralWidget()
        self.overlay.setGeometry(parent.rect())
        self.side_menu.setFixedHeight(parent.height())
        if self._menu_open:
            _, open_x = self._menu_positions()
            self._menu_anim.stop()
            self.side_menu.move(open_x, 0)
        elif not self._menu_closing:
            self.side_menu.hide()
            self.overlay.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and getattr(self, "_menu_open", False):
            self.close_menu()
        else:
            super().keyPressEvent(event)

    # -----------------------------
    # رویدادها
    # -----------------------------
    def _schedule_rebuild(self, clear_results):
        # منو باز می‌ماند؛ فقط با دکمه ✕ بسته می‌شود
        idx = self.tabs.currentIndex()
        QTimer.singleShot(0, lambda: self._rebuild_now(clear_results, idx))

    def _rebuild_now(self, clear_results, tab_index):
        # به منو دست نمی‌زنیم تا کاربر خودش هر وقت خواست آن را ببندد
        self.rebuild_ui(clear_results=clear_results)
        self.tabs.setCurrentIndex(tab_index)

    def on_language(self, value):
        if value == self.lang:
            return
        self.lang = value
        # به‌روزرسانی زبان بخش دستچین
        if hasattr(self, "builder_widget"):
            self.builder_widget.set_lang(self.lang)
        self._schedule_rebuild(clear_results=False)

    def on_theme(self, value):
        if value == self.theme:
            return
        self.theme = value
        self.apply_theme()
        self.restore_results()
        self.clear_status()
        if hasattr(self, "builder_widget"):
            self.builder_widget.set_theme(self.theme)

    def on_input_mode(self, value):
        if value == self.input_mode:
            return
        self.input_mode = value
        self._schedule_rebuild(clear_results=True)

    def on_pdf_lang(self, value):
        self.pdf_lang = value

    def on_known_side(self, value):
        if value == self.known_side:
            return
        self.known_side = value
        self._schedule_rebuild(clear_results=True)
        
    def on_missing_company(self, value):
        self.missing_company = value

    def _filter_db_by_company(self, items, company):
        return glogic.filter_by_company(items, company)

    def _disable_company_options(self, combo):
        model = combo.model()
        for i in range(combo.count()):
            if combo.itemData(i) in glogic.DISABLED_COMPANIES:
                item = model.item(i)
                if item is not None:
                    item.setEnabled(False)

    # -----------------------------
    # نمایش نتیجه
    # -----------------------------
    def show_result(self, key, tone_name):
        self.result_tones[key] = tone_name
        label = self.result_labels.get(key)
        if not label:
            return
        text = self.result_texts.get(key, {}).get(self.lang, "")
        label.setText(text)
        label.setStyleSheet(f"color: {self.tone(tone_name)};")

    def show_error(self, key, message):
        self.result_texts[key] = {"en": "", "fa": ""}
        label = self.result_labels.get(key)
        if label:
            label.setText(message)
            label.setStyleSheet(f"color: {self.tone('error')};")

    # -----------------------------
    # محاسبات
    # -----------------------------
    def calculate_speed(self):
        try:
            result = logic.calculate_speed(self.values, self.input_mode)
            speed = result["speed"]
            self.result_texts["speed"] = {
                "en": f"{TRANSLATIONS['en']['speed_result']}: {speed:.2f} km/h",
                "fa": f"{TRANSLATIONS['fa']['speed_result']}: {speed:.2f} km/h",
            }
            self.show_result("speed", "success")
        except logic.CalcError as e:
            msg = self.t(e.key)
            self.show_error("speed", msg)

    def calculate_rpm(self):
        try:
            result = logic.calculate_rpm(self.values, self.input_mode)
            rpm = result["rpm"]
            self.result_texts["rpm"] = {
                "en": f"{TRANSLATIONS['en']['rpm_result']}: {rpm:.2f} RPM",
                "fa": f"{TRANSLATIONS['fa']['rpm_result']}: {rpm:.2f} RPM",
            }
            self.show_result("rpm", "info")
        except logic.CalcError as e:
            msg = self.t(e.key)
            self.show_error("rpm", msg)

    def calculate_missing(self):
        try:
            result = logic.calculate_missing(
                self.values, self.input_mode, self.known_side
            )
            total_ratio = result["total_ratio"]
            unknown_side = result["unknown_side"]
            unknown_ratio = result["unknown_ratio"]

            second_key = f"{unknown_side}_ratio_result"
            en_total = TRANSLATIONS["en"]["total_ratio_result"]
            fa_total = TRANSLATIONS["fa"]["total_ratio_result"]
            en_second = TRANSLATIONS["en"][second_key]
            fa_second = TRANSLATIONS["fa"][second_key]

            db_key = "gears" if unknown_side == "gear" else "diffs"
            db_list = self._filter_db_by_company(
                self.gear_db.get(db_key, []), self.missing_company
            )
            match = glogic.find_closest(unknown_ratio, db_list)
            sugg_fa = ""
            sugg_en = ""
            if match:
                name = match.get("name", "")
                name_part = f" ({name})" if name else ""
                err = match["error_percent"]
                sugg_fa = f"\n{TRANSLATIONS['fa']['suggested_code']}: {match.get('code','')}{name_part} — خطا {err:.2f}%"
                sugg_en = f"\n{TRANSLATIONS['en']['suggested_code']}: {match.get('code','')}{name_part} — error {err:.2f}%"

            self.result_texts["missing"] = {
                "en": f"{en_total}: {total_ratio:.4f}\n{en_second}: {unknown_ratio:.4f}{sugg_en}",
                "fa": f"{fa_total}: {total_ratio:.4f}\n{fa_second}: {unknown_ratio:.4f}{sugg_fa}",
            }
            self.show_result("missing", "missing")
        except logic.CalcError as e:
            msg = self.t(e.key)
            self.show_error("missing", msg)

    # -----------------------------
    # کپی نتیجه
    # -----------------------------
    def copy_result(self, result_key):
        text = self.result_texts.get(result_key, {}).get(self.lang, "")
        if not text:
            self.set_status(self.t("no_result"), "error")
            return
        QApplication.clipboard().setText(text)
        self.set_status(self.t("copied"), "success")

    # -----------------------------
    # PDF  (فقط fpdf2 نسخه ۲)
    # -----------------------------
    def pdf_lib_error_message(self):
        if self.lang == "fa":
            return (
                "کتابخانه PDF نسخه ۲ نیست.\n"
                f"نسخه فعلی: {FPDF2_VERSION_TEXT}\n\n"
                "این دو دستور را در cmd اجرا کنید:\n"
                "python -m pip uninstall -y fpdf fpdf2\n"
                'python -m pip install "fpdf2>=2.8,<3"'
            )
        return (
            "PDF library is not fpdf2.\n"
            f"Current version: {FPDF2_VERSION_TEXT}\n\n"
            "Run these in cmd:\n"
            "python -m pip uninstall -y fpdf fpdf2\n"
            'python -m pip install "fpdf2>=2.8,<3"'
        )

    def get_pdf_fields(self, lang, result_key):
        T = TRANSLATIONS[lang]
        fields = []
        keys = ["rpm", "speed", "gear_code", "gear_ratio",
                "diff_code", "diff_ratio", "ring", "sidewall", "pahna"]
        for key in keys:
            value = self.values.get(key, "")
            if str(value).strip():
                fields.append((T.get(key, key), value))
        fields.append((T["input_mode"], T[self.input_mode]))
        if result_key == "missing":
            known_key = "known_diff" if self.known_side == "diff" else "known_gear"
            fields.append((T["known_side"], T[known_key]))
        result = self.result_texts.get(result_key, {}).get(lang, "")
        fields.append((T["result"], result))
        return fields

    def find_pdf_font(self):
        if (self.pdf_font_path
                and os.path.isfile(self.pdf_font_path)
                and Path(self.pdf_font_path).suffix.lower() == ".ttf"):
            return self.pdf_font_path

        base = get_base_dir()
        candidates = [
            base / "fonts" / "Shabnam.ttf",
            base / "fonts" / "Shabnam-Regular.ttf",
            base / "fonts" / "Vazirmatn-Regular.ttf",
            base / "fonts" / "Vazirmatn.ttf",
            base / "fonts" / "Vazir.ttf",
            base / "fonts" / "IRANSans.ttf",
            base / "fonts" / "Tahoma.ttf",
            base / "Shabnam.ttf",
        ]
        if os.name == "nt":
            winfonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
            candidates.extend([winfonts / "tahoma.ttf", winfonts / "segoeui.ttf"])

        for path in candidates:
            if path.is_file():
                self.pdf_font_path = str(path)
                return self.pdf_font_path

        fonts_dir = base / "fonts"
        if fonts_dir.is_dir():
            for path in sorted(fonts_dir.iterdir()):
                if path.suffix.lower() == ".ttf":
                    self.pdf_font_path = str(path)
                    return self.pdf_font_path
        return None

    def ensure_pdf_font(self):
        path = self.find_pdf_font()
        if path:
            return path
        QMessageBox.information(
            self, self.t("pdf_font_missing_title"), self.t("pdf_font_missing")
        )
        path, _ = QFileDialog.getOpenFileName(
            self, self.t("choose_persian_font"),
            str(get_base_dir()), "TrueType Font (*.ttf)",
        )
        if path and os.path.isfile(path):
            self.pdf_font_path = path
            return path
        return None

    def find_bold_font(self, regular_font_path):
        if (self.pdf_bold_path
                and os.path.isfile(self.pdf_bold_path)
                and Path(self.pdf_bold_path).suffix.lower() == ".ttf"):
            return self.pdf_bold_path
        if not regular_font_path:
            return None
        folder = Path(regular_font_path).parent
        if folder.is_dir():
            for path in sorted(folder.iterdir()):
                if path.suffix.lower() == ".ttf" and "bold" in path.stem.lower():
                    return str(path)
        return None

    def add_persian_fonts(self, pdf, font_path):
        pdf.add_font("Fa", "", str(font_path))
        bold_path = self.find_bold_font(font_path)
        if bold_path:
            try:
                pdf.add_font("Fa", "B", str(bold_path))
                return True
            except Exception:
                return False
        return False

    def add_pdf_page(self, pdf, lang, result_key):
        pdf.add_page()
        T = TRANSLATIONS[lang]
        fields = self.get_pdf_fields(lang, result_key)

        if lang == "en":
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, logic.safe_ascii(T["app_title"]),
                     align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            pdf.set_font("Helvetica", "", 11)
            for label, value in fields:
                pdf.multi_cell(0, 8, logic.safe_ascii(f"{label}: {value}"))
                pdf.ln(1)
            return True

        font_path = self.ensure_pdf_font()
        if not font_path:
            return False

        has_bold = self.add_persian_fonts(pdf, font_path)
        pdf.set_font("Fa", "B" if has_bold else "", 14)
        pdf.cell(0, 10, shape_fa_text(T["app_title"]),
                 align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        pdf.set_font("Fa", "", 11)
        for label, value in fields:
            pdf.multi_cell(0, 8, shape_fa_text(f"{label}: {value}"), align="R")
            pdf.ln(1)
        return True

    def save_pdf(self, result_key):
        if not self.result_texts.get(result_key, {}).get(self.lang, ""):
            self.set_status(self.t("no_result"), "error")
            return

        if not FPDF2_OK:
            message = self.pdf_lib_error_message()
            write_log(f"Wrong PDF library version: {FPDF2_VERSION_TEXT}")
            QMessageBox.critical(self, self.t("error"), message)
            self.set_status(self.t("pdf_error"), "error")
            return

        mode = self.pdf_lang
        needs_fa = mode in ("fa", "both")
        if needs_fa and not self.ensure_pdf_font():
            return

        from datetime import datetime
        default_name = f"gearbox_{datetime.now():%Y%m%d_%H%M%S}.pdf"

        path, _ = QFileDialog.getSaveFileName(
            self, self.t("pdf_save_title"),
            default_name, self.t("pdf_filter"),
        )
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"

        try:
            pdf = FPDF()
            pdf.set_auto_page_break(True, 15)
            if mode in ("en", "both"):
                self.add_pdf_page(pdf, "en", result_key)
            if needs_fa:
                if not self.add_pdf_page(pdf, "fa", result_key):
                    return
            pdf.output(path)
            self.set_status(self.t("pdf_saved"), "success")
        except Exception:
            import traceback
            error_text = (
                f"fpdf version: {FPDF2_VERSION_TEXT}\n"
                f"pdf language: {mode}\n"
                f"font: {self.pdf_font_path}\n"
                + traceback.format_exc()
            )
            write_log(error_text)
            QMessageBox.critical(
                self, self.t("error"),
                self.t("pdf_error") + "\n\n" + error_text[-900:],
            )
            self.set_status(self.t("pdf_error"), "error")
