"""
ویجت «دستچین گیربکس» — دوزبانه (فارسی/انگلیسی)
تم قرمز + دسته‌بندی شرکت + موقعیت دنده + پیشنهاد خودکار دیفرانسیل
+ پنجره پیشنهادات و پنجره نمودار با خروجی PDF و عکس
"""

import os
import math
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont
from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QGroupBox, QTabWidget,
    QScrollArea, QFrame, QSpinBox, QMessageBox, QInputDialog,
    QSizePolicy, QApplication, QFileDialog,
)

import calculator_logic as logic
import gearbox_logic as glogic
import preset_manager as presets


DIFF_AUTO = -1.0


# -------------------------------------------------
# ترجمه‌های بخش دستچین
# -------------------------------------------------
BUILDER_TRANSLATIONS = {
    "fa": {
        "builder_title": "🔧 دستچین گیربکس",
        "preset": "پریست:", "save": "ذخیره", "delete": "حذف", "new": "جدید",
        "select_preset_ph": "— انتخاب پریست —",
        "common_settings": "تنظیمات مشترک",
        "manufacturer": "شرکت سازنده:",
        "company_all": "همه شرکت‌ها", "company_saipa": "سایپا", "company_ikco": "ایران خودرو",
        "gear_count": "تعداد دنده:",
        "diff": "دیفرانسیل:",
        "diff_manual_ph": "یا ضریب دیفرانسیل دستی",
        "ring": "رینگ:", "sidewall": "فاق تایر:", "width": "پهنا:",
        "tab_mode1": "سرعت+دور → ضریب و پیشنهاد",
        "tab_mode2": "ضریب+سرعت → دور موتور",
        "tab_mode3": "ضریب+دور → سرعت",
        "fixed_speed": "سرعت ثابت (km/h):",
        "fixed_rpm": "دور موتور ثابت (RPM):",
        "gear": "دنده",
        "speed_ph": "سرعت (km/h)", "rpm_ph": "دور موتور (RPM)",
        "ratio_manual_ph": "یا ضریب دستی (مثلاً 0.745)",
        "select_code_ph": "— انتخاب کد یا تایپ ضریب —",
        "select_diff_ph": "— انتخاب دیفرانسیل —",
        "diff_auto": "🤷 نمیدانم (پیشنهاد خودکار)",
        "calculate": "محاسبه و رسم",
        "view_suggestions": "📋 مشاهده کامل پیشنهادات",
        "view_chart": "📈 مشاهده نمودار کامل",
        "manual_diff": "ضریب دستی",
        "err_tire": "⚠️ اطلاعات لاستیک (رینگ، فاق تایر، پهنا) را درست وارد کنید.",
        "err_diff": "⚠️ دیفرانسیل را انتخاب کنید یا گزینه «🤷 نمیدانم» را بزنید.",
        "err_mode2": "⚠️ سرعت ثابت، دیفرانسیل و اطلاعات لاستیک را کامل کنید.",
        "err_mode3": "⚠️ دور موتور ثابت، دیفرانسیل و اطلاعات لاستیک را کامل کنید.",
        "err_no_gear": "⚠️ حداقل برای یک دنده سرعت و دور موتور وارد کنید.",
        "err_no_suggest": "⚠️ پیشنهادی یافت نشد. داده‌های این شرکت کافی نیست.",
        "sugg_ready": "✅ پیشنهادات برای {n} دنده آماده شد.",
        "sugg_ready_hint": "برای مشاهده کامل، کپی یا PDF از دکمه «📋 مشاهده کامل پیشنهادات» استفاده کنید.",
        "m1_line": "دنده {n}: ضریب کل {t} | ضریب دنده {g}",
        "m2_line": "دنده {n} (ضریب {r}): دور موتور {v} RPM",
        "m3_line": "دنده {n} (ضریب {r}): سرعت {v} km/h",
        "sugg_line": "   پیشنهاد: کد {code}{name} — ضریب {ratio} — خطا {err}%",
        "no_sugg_line": "   پیشنهادی یافت نشد",
        "incomplete_line": "دنده {n}: — ورودی ناقص —",
        "notcalc_line": "دنده {n}: — قابل محاسبه نیست —",
        "no_sugg_gear_line": "دنده {n}: ضریب کل {t} | پیشنهادی یافت نشد",
        "sugg_diff_line": "⭐ دیفرانسیل پیشنهادی: کد {code}{name} — ضریب {ratio}",
        "diff_line": "دیفرانسیل: {label}",
        "ratio_unknown_line": "دنده {n}: — ضریب مشخص نیست —",
        "sugg_title": "پیشنهاد کد دنده",
        "suggestions": "پیشنهادات",
        "sugg_dialog_hint": "ابتدا در تب «سرعت+دور» محاسبه را انجام دهید.",
        "chart": "نمودار",
        "chart_dialog_hint": "ابتدا در یکی از تب‌های «ضریب+سرعت» یا «ضریب+دور» محاسبه را انجام دهید.",
        "preset_title": "پریست",
        "preset_not_found": "پریست پیدا نشد یا خراب است.",
        "save_preset_title": "ذخیره پریست",
        "preset_name": "نام پریست:",
        "error": "خطا",
        "save_preset_fail": "ذخیره پریست ناموفق بود:",
        "delete_preset_title": "حذف پریست",
        "delete_preset_q": "پریست «{name}» حذف شود؟",
        "restore_fail": "بازیابی کامل انجام نشد:",
        "close": "بستن",
        "chart_dialog_title": "نمودار دور موتور / سرعت",
        "save_png": "🖼️ ذخیره عکس (PNG)",
        "export_pdf": "📄 خروجی PDF",
        "fpdf_missing": "کتابخانه fpdf2 نصب نیست.",
        "save_chart_pdf": "ذخیره PDF نمودار",
        "chart_img_err": "خطا در آماده‌سازی تصویر نمودار.",
        "chart_pdf_saved": "نمودار در فایل PDF ذخیره شد.",
        "pdf_err": "خطا در ساخت PDF:",
        "save_chart_png": "ذخیره عکس نمودار",
        "chart_png_saved": "عکس نمودار ذخیره شد.",
        "img_err": "خطا در ذخیره عکس.",
        "copy": "📋 کپی",
        "copied": "کپی",
        "copied_msg": "متن پیشنهادات کپی شد.",
        "persian_font": "فونت فارسی",
        "persian_font_missing": "فونت فارسی (.ttf) پیدا نشد.",
        "save_pdf": "ذخیره PDF",
        "pdf_saved": "فایل PDF ذخیره شد.",
        "axis_speed": "سرعت (km/h)",
        "axis_rpm": "دور موتور (RPM)",
        "no_chart_data": "داده‌ای برای رسم نمودار نیست",
        "drop": "افت",
        "mechanic_note": "⚠️ بعضی از دنده‌ها یا دیفرانسیل‌ها ممکن است روی گیربکس شما نصب نشوند؛ در این مورد با مکانیک خود مشورت کنید.",
    },
    "en": {
        "builder_title": "🔧 Gearbox Builder",
        "preset": "Preset:", "save": "Save", "delete": "Delete", "new": "New",
        "select_preset_ph": "— Select preset —",
        "common_settings": "Common Settings",
        "manufacturer": "Manufacturer:",
        "company_all": "All companies", "company_saipa": "SAIPA", "company_ikco": "IKCO",
        "gear_count": "Gear count:",
        "diff": "Differential:",
        "diff_manual_ph": "Or manual diff ratio",
        "ring": "Ring:", "sidewall": "Tire sidewall:", "width": "Width:",
        "tab_mode1": "Speed+RPM → Ratio & Suggestion",
        "tab_mode2": "Ratio+Speed → RPM",
        "tab_mode3": "Ratio+RPM → Speed",
        "fixed_speed": "Fixed speed (km/h):",
        "fixed_rpm": "Fixed RPM:",
        "gear": "Gear",
        "speed_ph": "Speed (km/h)", "rpm_ph": "Engine RPM",
        "ratio_manual_ph": "Or manual ratio (e.g. 0.745)",
        "select_code_ph": "— Select code or type ratio —",
        "select_diff_ph": "— Select differential —",
        "diff_auto": "🤷 I don't know (auto suggest)",
        "calculate": "Calculate & Draw",
        "view_suggestions": "📋 View full suggestions",
        "view_chart": "📈 View full chart",
        "manual_diff": "Manual ratio",
        "err_tire": "⚠️ Please enter tire info (ring, sidewall, width) correctly.",
        "err_diff": "⚠️ Select a differential or choose '🤷 I don't know'.",
        "err_mode2": "⚠️ Complete fixed speed, differential and tire info.",
        "err_mode3": "⚠️ Complete fixed RPM, differential and tire info.",
        "err_no_gear": "⚠️ Enter speed and RPM for at least one gear.",
        "err_no_suggest": "⚠️ No suggestion found. Not enough data for this company.",
        "sugg_ready": "✅ Suggestions for {n} gears ready.",
        "sugg_ready_hint": "Use '📋 View full suggestions' for full view, copy or PDF.",
        "m1_line": "Gear {n}: total ratio {t} | gear ratio {g}",
        "m2_line": "Gear {n} (ratio {r}): {v} RPM",
        "m3_line": "Gear {n} (ratio {r}): {v} km/h",
        "sugg_line": "   Suggestion: code {code}{name} — ratio {ratio} — error {err}%",
        "no_sugg_line": "   No suggestion found",
        "incomplete_line": "Gear {n}: — incomplete input —",
        "notcalc_line": "Gear {n}: — cannot calculate —",
        "no_sugg_gear_line": "Gear {n}: total ratio {t} | no suggestion",
        "sugg_diff_line": "⭐ Suggested differential: code {code}{name} — ratio {ratio}",
        "diff_line": "Differential: {label}",
        "ratio_unknown_line": "Gear {n}: — ratio unknown —",
        "sugg_title": "Gear code suggestion",
        "suggestions": "Suggestions",
        "sugg_dialog_hint": "First calculate in the 'Speed+RPM' tab.",
        "chart": "Chart",
        "chart_dialog_hint": "First calculate in 'Ratio+Speed' or 'Ratio+RPM' tab.",
        "preset_title": "Preset",
        "preset_not_found": "Preset not found or corrupted.",
        "save_preset_title": "Save preset",
        "preset_name": "Preset name:",
        "error": "Error",
        "save_preset_fail": "Saving preset failed:",
        "delete_preset_title": "Delete preset",
        "delete_preset_q": "Delete preset '{name}'?",
        "restore_fail": "Restore not complete:",
        "close": "Close",
        "chart_dialog_title": "RPM / Speed Chart",
        "save_png": "🖼️ Save image (PNG)",
        "export_pdf": "📄 Export PDF",
        "fpdf_missing": "fpdf2 library not installed.",
        "save_chart_pdf": "Save chart PDF",
        "chart_img_err": "Error preparing chart image.",
        "chart_pdf_saved": "Chart saved as PDF.",
        "pdf_err": "Error creating PDF:",
        "save_chart_png": "Save chart image",
        "chart_png_saved": "Chart image saved.",
        "img_err": "Error saving image.",
        "copy": "📋 Copy",
        "copied": "Copy",
        "copied_msg": "Suggestions text copied.",
        "persian_font": "Persian font",
        "persian_font_missing": "Persian font (.ttf) not found.",
        "save_pdf": "Save PDF",
        "pdf_saved": "PDF file saved.",
        "axis_speed": "Speed (km/h)",
        "axis_rpm": "Engine RPM",
        "no_chart_data": "No data to draw chart",
        "drop": "Drop",
        "mechanic_note": "⚠️ Some gears or differentials may not fit your gearbox; please consult your mechanic.",
    },
}


def _t(lang, key):
    return BUILDER_TRANSLATIONS.get(lang, BUILDER_TRANSLATIONS["fa"]).get(key, key)


# -------------------------------------------------
# استایل (تم قرمز برای دستچین)
# -------------------------------------------------
def _colors(theme):
    if theme == "dark":
        return {
            "bg": "#0f172a", "card": "#111827", "input_bg": "#1e293b",
            "fg": "#f8fafc", "muted": "#94a3b8", "border": "#334155",
            "primary": "#ef4444", "primary_hover": "#dc2626",
            "success": "#22c55e", "info": "#38bdf8", "warning": "#f59e0b",
            "result_bg": "#1e293b",
        }
    return {
        "bg": "#f3f6fb", "card": "#ffffff", "input_bg": "#ffffff",
        "fg": "#0f172a", "muted": "#64748b", "border": "#dbe2ea",
        "primary": "#dc2626", "primary_hover": "#b91c1c",
        "success": "#16a34a", "info": "#0891b2", "warning": "#d97706",
        "result_bg": "#f8fafc",
    }


def _stylesheet(theme):
    c = _colors(theme)
    return f"""
    QWidget#BuilderRoot {{ background-color: {c['bg']}; color: {c['fg']}; font-size: 10pt; }}
    QGroupBox {{
        border: 1px solid {c['border']}; border-radius: 12px;
        margin-top: 14px; padding: 12px 10px 10px 10px;
        background-color: {c['card']}; font-weight: 700;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin; subcontrol-position: top center;
        padding: 0 8px; color: {c['primary']};
        background-color: {c['card']}; border: 1px solid {c['border']};
        border-radius: 8px;
    }}
    QTabWidget::pane {{ border: 1px solid {c['border']}; border-radius: 12px; background: {c['card']}; }}
    QTabBar::tab {{ padding: 7px 14px; margin: 2px 4px; color: {c['muted']};
        border-top-left-radius: 8px; border-top-right-radius: 8px; }}
    QTabBar::tab:selected {{ background: {c['card']}; color: {c['fg']};
        border: 1px solid {c['border']}; border-bottom: 2px solid {c['primary']}; }}
    QLineEdit, QComboBox, QSpinBox {{
        background: {c['input_bg']}; border: 1px solid {c['border']};
        border-radius: 8px; padding: 7px 10px; color: {c['fg']};
        min-height: 20px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ border: 1px solid {c['primary']}; }}
    QComboBox QAbstractItemView {{ background: {c['card']}; color: {c['fg']};
        selection-background-color: {c['primary']}; }}
    QPushButton {{ border: none; border-radius: 8px; padding: 8px 14px;
        font-weight: 700; background: {c['primary']}; color: white; }}
    QPushButton:hover {{ background: {c['primary_hover']}; }}
    QPushButton#SuccessButton {{ background: {c['success']}; }}
    QPushButton#InfoButton {{ background: {c['info']}; }}
    QPushButton#WarningButton {{ background: {c['warning']}; }}
    QFrame#ResultBox {{
        background: {c['result_bg']}; border: 1px solid {c['border']};
        border-radius: 10px; font-size: 11pt;
    }}
    QPushButton#CloseResultBtn {{
        background: transparent; color: {c['muted']}; border: none;
        border-radius: 8px; padding: 2px; font-weight: 700; font-size: 16pt;
    }}
    QPushButton#CloseResultBtn:hover {{ background: {c['border']}; color: {c['fg']}; }}
    QLabel#FieldLabel {{ color: {c['muted']}; }}
    QScrollArea {{ border: none; background: transparent; }}
    QScrollArea > QWidget > QWidget {{ background: transparent; }}
    QScrollBar:vertical {{ background: transparent; width: 10px; }}
    QScrollBar::handle:vertical {{ background: {c['border']}; border-radius: 5px; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; }}
    QScrollBar::handle:horizontal {{ background: {c['border']}; border-radius: 5px; }}
    """


# -------------------------------------------------
# توابع کمکی خروجی PDF متنی
# -------------------------------------------------
_PDF_CHAR_MAP = {
    "⭐": "", "🤷": "", "📋": "", "📄": "", "✅": "",
    "⚠️": "", "🔧": "", "📈": "", "🖼️": "",
    "—": "-", "–": "-",
}


def _pdf_safe(text):
    for old, new in _PDF_CHAR_MAP.items():
        text = text.replace(old, new)
    return text


def _shape(text):
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return str(text)


def _find_persian_font():
    base = Path(__file__).resolve().parent
    fonts_dir = base / "fonts"
    for name in ("Shabnam.ttf", "Shabnam-Regular.ttf",
                 "Vazirmatn-Regular.ttf", "Vazirmatn.ttf", "Vazir.ttf"):
        p = fonts_dir / name
        if p.is_file():
            return str(p)
    if fonts_dir.is_dir():
        for p in sorted(fonts_dir.iterdir()):
            if p.suffix.lower() == ".ttf":
                return str(p)
    if os.name == "nt":
        winfonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
        for name in ("tahoma.ttf", "segoeui.ttf"):
            p = winfonts / name
            if p.is_file():
                return str(p)
    return None


def export_text_to_pdf(text, title, parent=None, lang="fa"):
    try:
        from fpdf import FPDF
    except Exception:
        QMessageBox.critical(parent, _t(lang, "error"), _t(lang, "fpdf_missing"))
        return False

    is_fa = (lang == "fa")
    font_path = None
    if is_fa:
        font_path = _find_persian_font()
        if not font_path:
            QMessageBox.warning(parent, _t(lang, "persian_font"), _t(lang, "persian_font_missing"))
            return False

    path, _ = QFileDialog.getSaveFileName(
        parent, _t(lang, "save_pdf"), "gearbox_suggestions.pdf", "PDF files (*.pdf)"
    )
    if not path:
        return False
    if not path.lower().endswith(".pdf"):
        path += ".pdf"

    try:
        pdf = FPDF()
        pdf.set_auto_page_break(True, 15)
        pdf.add_page()
        if is_fa:
            pdf.add_font("Fa", "", font_path)
            pdf.set_font("Fa", "", 14)
            pdf.multi_cell(w=0, h=10, text=_shape(_pdf_safe(title)),
                           align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            pdf.set_font("Fa", "", 11)
            for line in text.split("\n"):
                content = line if line.strip() else " "
                pdf.multi_cell(w=0, h=7, text=_shape(_pdf_safe(content)),
                               align="R", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "B", 14)
            pdf.multi_cell(w=0, h=10, text=_pdf_safe(title),
                           align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            pdf.set_font("Helvetica", "", 11)
            for line in text.split("\n"):
                content = line if line.strip() else " "
                pdf.multi_cell(w=0, h=7, text=_pdf_safe(content),
                               align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.output(path)
        QMessageBox.information(parent, _t(lang, "save_pdf"), _t(lang, "pdf_saved"))
        return True
    except Exception:
        import traceback
        QMessageBox.critical(
            parent, _t(lang, "error"),
            _t(lang, "pdf_err") + "\n\n" + traceback.format_exc()[-900:],
        )
        return False


# -------------------------------------------------
# پنجره پیشنهادات (اسکرول + کپی + PDF)
# -------------------------------------------------
class SuggestionDialog(QDialog):
    def __init__(self, title, text, theme="light", lang="fa", parent=None):
        super().__init__(parent)
        self._title = title
        self._text = text
        self._theme = theme
        self._lang = lang

        self.setWindowTitle(title)
        self.setLayoutDirection(Qt.RightToLeft if lang == "fa" else Qt.LeftToRight)
        self.setMinimumSize(560, 460)
        self.resize(640, 560)

        self._build()
        self.setStyleSheet(self._style())

    def _style(self):
        c = _colors(self._theme)
        return f"""
        QDialog {{ background-color: {c['bg']}; color: {c['fg']}; font-size: 10pt; }}
        QLabel#SugText {{
            background-color: {c['result_bg']};
            border: 1px solid {c['border']};
            border-radius: 10px;
            padding: 12px;
            font-size: 11pt;
        }}
        QPushButton {{ border: none; border-radius: 8px; padding: 8px 14px;
            font-weight: 700; background: {c['primary']}; color: white; }}
        QPushButton:hover {{ background: {c['primary_hover']}; }}
        QPushButton#InfoButton {{ background: {c['info']}; }}
        QPushButton#WarningButton {{ background: {c['warning']}; }}
        QScrollArea {{ border: none; background: transparent; }}
        QScrollBar:vertical {{ background: transparent; width: 10px; }}
        QScrollBar::handle:vertical {{ background: {c['border']}; border-radius: 5px; }}
        """

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QLabel(self._text)
        content.setObjectName("SugText")
        content.setWordWrap(True)
        content.setTextInteractionFlags(Qt.TextSelectableByMouse)
        align = Qt.AlignRight if self._lang == "fa" else Qt.AlignLeft
        content.setAlignment(align | Qt.AlignTop)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        btns = QHBoxLayout()
        copy_btn = QPushButton(_t(self._lang, "copy"))
        copy_btn.setObjectName("InfoButton")
        copy_btn.clicked.connect(self._copy)
        pdf_btn = QPushButton(_t(self._lang, "export_pdf"))
        pdf_btn.setObjectName("WarningButton")
        pdf_btn.clicked.connect(self._save_pdf)
        close_btn = QPushButton(_t(self._lang, "close"))
        close_btn.clicked.connect(self.accept)

        btns.addWidget(copy_btn)
        btns.addWidget(pdf_btn)
        btns.addStretch(1)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

    def _copy(self):
        QApplication.clipboard().setText(self._text)
        QMessageBox.information(self, _t(self._lang, "copied"), _t(self._lang, "copied_msg"))

    def _save_pdf(self):
        export_text_to_pdf(self._text, self._title, self, self._lang)


# -------------------------------------------------
# نمودار دور موتور / سرعت
# -------------------------------------------------
class RpmSpeedChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.spec = None
        self.dark = False
        self.x_label = "Speed (km/h)"
        self.y_label = "Engine RPM"
        self.no_data_text = "No data to draw chart"

    def set_spec(self, spec, dark=False):
        self.spec = spec
        self.dark = dark
        self.update()

    def set_labels(self, x_label, y_label, no_data):
        self.x_label = x_label
        self.y_label = y_label
        self.no_data_text = no_data
        self.update()

    def _nice_step(self, x):
        if x <= 0:
            return 1.0
        exp = math.floor(math.log10(x))
        f = x / (10 ** exp)
        if f <= 1:
            nf = 1
        elif f <= 2:
            nf = 2
        elif f <= 5:
            nf = 5
        else:
            nf = 10
        return nf * (10 ** exp)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        bg = "#0f172a" if self.dark else "#ffffff"
        p.fillRect(0, 0, w, h, QColor(bg))
        if not self.spec:
            p.setPen(QColor("#94a3b8"))
            p.drawText(self.rect(), Qt.AlignCenter, self.no_data_text)
            return
        self._draw(p, w, h)

    def _draw(self, p, w, h):
        spec = self.spec
        ml, mr, mt, mb = 58, 16, 16, 44
        pw, ph = w - ml - mr, h - mt - mb
        if pw <= 20 or ph <= 20:
            return
        max_speed = max(spec.get("max_speed", 1), 1)
        max_rpm = max(spec.get("max_rpm", 1), 1)

        def X(s):
            return ml + (s / max_speed) * pw

        def Y(r):
            return mt + ph - (r / max_rpm) * ph

        fg = "#e2e8f0" if self.dark else "#0f172a"
        grid = "#334155" if self.dark else "#e5e7eb"
        axis = "#94a3b8" if self.dark else "#64748b"
        bg = "#0f172a" if self.dark else "#ffffff"

        font = QFont()
        font.setPointSize(8)
        p.setFont(font)

        xstep = self._nice_step(max_speed / 6)
        ystep = self._nice_step(max_rpm / 6)

        p.setBrush(Qt.NoBrush)
        s = 0.0
        while s <= max_speed + 0.001:
            x = X(s)
            p.setPen(QPen(QColor(grid), 1))
            p.drawLine(int(x), mt, int(x), mt + ph)
            p.setPen(QColor(axis))
            p.drawText(int(x) - 20, mt + ph + 4, 40, 16,
                       Qt.AlignHCenter | Qt.AlignTop, f"{s:.0f}")
            s += xstep

        r = 0.0
        while r <= max_rpm + 0.001:
            y = Y(r)
            p.setPen(QPen(QColor(grid), 1))
            p.drawLine(ml, int(y), ml + pw, int(y))
            p.setPen(QColor(axis))
            p.drawText(2, int(y) - 8, ml - 10, 16,
                       Qt.AlignRight | Qt.AlignVCenter, f"{r:.0f}")
            r += ystep

        p.setPen(QPen(QColor(axis), 2))
        p.drawLine(ml, mt, ml, mt + ph)
        p.drawLine(ml, mt + ph, ml + pw, mt + ph)

        p.setPen(QColor(fg))
        p.drawText(ml, h - 16, pw, 14, Qt.AlignHCenter, self.x_label)
        p.save()
        p.translate(14, mt + ph)
        p.rotate(-90)
        p.drawText(0, 0, ph, 14, Qt.AlignHCenter, self.y_label)
        p.restore()

        for line in spec.get("lines", []):
            slope = line["slope"]
            vmax = line.get("vmax") or max_speed
            p.setPen(QPen(QColor(line["color"]), 2))
            p.drawLine(int(X(0)), int(Y(0)), int(X(vmax)), int(Y(slope * vmax)))

        # افت‌های دور با برچسب خوانا (یکی‌درمیان بالا/پایین)
        for didx, d in enumerate(spec.get("drops", [])):
            x = X(d["x"])
            p.setPen(QPen(QColor("#ef4444"), 2, Qt.DashLine))
            p.drawLine(int(x), int(Y(d["y_top"])), int(x), int(Y(d["y_bottom"])))
            mid = (Y(d["y_top"]) + Y(d["y_bottom"])) / 2
            self._draw_label(p, d["label"], int(x) + 6, mid,
                             "#ef4444", bg, above=(didx % 2 == 0))

        # نقطه‌ها با برچسب خوانا (یکی‌درمیان بالا/پایین تا تداخل نکنند)
        for idx, pt in enumerate(spec.get("points", [])):
            x, y = X(pt["x"]), Y(pt["y"])
            p.setPen(QPen(QColor(pt["color"]), 2))
            p.setBrush(QBrush(QColor(pt["color"])))
            p.drawEllipse(int(x) - 4, int(y) - 4, 8, 8)
            p.setBrush(Qt.NoBrush)
            self._draw_label(p, pt["label"], int(x) + 8, y,
                             pt["color"], bg, above=(idx % 2 == 0))

    def _draw_label(self, p, text, x, y_center, color, bg, above=True):
        """
        برچسب با پس‌زمینه نیمه‌شفاف برای خوانایی بهتر.
        برچسب‌ها یکی‌درمیان بالا یا پایین نقطه قرار می‌گیرند
        تا وقتی دنده‌ها به هم نزدیک هستند، اعداد در هم نروند.
        """
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(text)
        th = fm.height()
        pad = 4
        if above:
            top = int(y_center) - th - 10
        else:
            top = int(y_center) + 10
        # پس‌زمینه نیمه‌شفاف
        p.setPen(Qt.NoPen)
        box = QColor(bg)
        box.setAlpha(215)
        p.setBrush(QBrush(box))
        p.drawRoundedRect(x - pad, top - pad, tw + 2 * pad, th + pad, 4, 4)
        # متن
        p.setPen(QColor(color))
        p.drawText(x, top, tw, th, Qt.AlignLeft | Qt.AlignTop, text)
        p.setBrush(Qt.NoBrush)


# -------------------------------------------------
# پنجره نمودار (بزرگ + خروجی عکس و PDF)
# -------------------------------------------------
class ChartDialog(QDialog):
    def __init__(self, spec, dark, theme="light", lang="fa", parent=None):
        super().__init__(parent)
        self._spec = spec
        self._dark = dark
        self._theme = theme
        self._lang = lang

        self.setWindowTitle(_t(lang, "chart_dialog_title"))
        self.setLayoutDirection(Qt.RightToLeft if lang == "fa" else Qt.LeftToRight)
        self.setMinimumSize(700, 520)
        self.resize(900, 660)

        self._build()
        self.setStyleSheet(self._style())

    def _style(self):
        c = _colors(self._theme)
        return f"""
        QDialog {{ background-color: {c['bg']}; color: {c['fg']}; font-size: 10pt; }}
        QPushButton {{ border: none; border-radius: 8px; padding: 8px 14px;
            font-weight: 700; background: {c['primary']}; color: white; }}
        QPushButton:hover {{ background: {c['primary_hover']}; }}
        QPushButton#InfoButton {{ background: {c['info']}; }}
        QPushButton#WarningButton {{ background: {c['warning']}; }}
        QScrollArea {{ border: none; background: transparent; }}
        QScrollBar:vertical {{ background: transparent; width: 10px; }}
        QScrollBar::handle:vertical {{ background: {c['border']}; border-radius: 5px; }}
        QScrollBar:horizontal {{ background: transparent; height: 10px; }}
        QScrollBar::handle:horizontal {{ background: {c['border']}; border-radius: 5px; }}
        """

    def _chart_labels(self):
        return (_t(self._lang, "axis_speed"),
                _t(self._lang, "axis_rpm"),
                _t(self._lang, "no_chart_data"))

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.chart = RpmSpeedChart()
        self.chart.set_labels(*self._chart_labels())
        # اندازه حداقلی بر اساس تعداد دنده‌ها تا نمودار جا بشه و اسکرول بخورد
        num = len(self._spec.get("points", [])) if self._spec else 1
        min_w = 860
        min_h = max(460, 300 + num * 45)
        self.chart.setMinimumSize(min_w, min_h)
        self.chart.set_spec(self._spec, self._dark)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.chart)
        layout.addWidget(scroll, 1)

        btns = QHBoxLayout()
        png_btn = QPushButton(_t(self._lang, "save_png"))
        png_btn.setObjectName("InfoButton")
        png_btn.clicked.connect(self._save_png)
        pdf_btn = QPushButton(_t(self._lang, "export_pdf"))
        pdf_btn.setObjectName("WarningButton")
        pdf_btn.clicked.connect(self._save_pdf)
        close_btn = QPushButton(_t(self._lang, "close"))
        close_btn.clicked.connect(self.accept)

        btns.addWidget(png_btn)
        btns.addWidget(pdf_btn)
        btns.addStretch(1)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

    def _render_chart_image(self, width=1600, height=1000):
        chart = RpmSpeedChart()
        chart.set_labels(*self._chart_labels())
        chart.set_spec(self._spec, self._dark)
        chart.resize(width, height)
        return chart.grab()

    def _save_png(self):
        path, _ = QFileDialog.getSaveFileName(
            self, _t(self._lang, "save_chart_png"), "gearbox_chart.png", "PNG images (*.png)"
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        pixmap = self._render_chart_image()
        if pixmap.save(path, "PNG"):
            QMessageBox.information(self, _t(self._lang, "chart"), _t(self._lang, "chart_png_saved"))
        else:
            QMessageBox.critical(self, _t(self._lang, "error"), _t(self._lang, "img_err"))

    def _save_pdf(self):
        try:
            from fpdf import FPDF
        except Exception:
            QMessageBox.critical(self, _t(self._lang, "error"), _t(self._lang, "fpdf_missing"))
            return

        path, _ = QFileDialog.getSaveFileName(
            self, _t(self._lang, "save_chart_pdf"), "gearbox_chart.pdf", "PDF files (*.pdf)"
        )
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"

        pixmap = self._render_chart_image()
        tmp_png = os.path.join(tempfile.gettempdir(), "gearbox_chart_export.png")
        if not pixmap.save(tmp_png, "PNG"):
            QMessageBox.critical(self, _t(self._lang, "error"), _t(self._lang, "chart_img_err"))
            return

        try:
            pdf = FPDF(orientation="L")
            pdf.set_auto_page_break(False)
            pdf.add_page()
            img_w = pixmap.width()
            img_h = pixmap.height()
            scale = min(pdf.epw / img_w, pdf.eph / img_h)
            w = img_w * scale
            h = img_h * scale
            x = (pdf.w - w) / 2
            y = (pdf.h - h) / 2
            pdf.image(tmp_png, x=x, y=y, w=w, h=h)
            pdf.output(path)
            QMessageBox.information(self, _t(self._lang, "chart"), _t(self._lang, "chart_pdf_saved"))
        except Exception as e:
            QMessageBox.critical(self, _t(self._lang, "error"), _t(self._lang, "pdf_err") + f"\n{e}")
        finally:
            try:
                os.remove(tmp_png)
            except Exception:
                pass


# -------------------------------------------------
# ویجت اصلی دستچین گیربکس
# -------------------------------------------------
class GearboxBuilderWidget(QWidget):
    def __init__(self, font_family, theme="light", lang="fa", parent=None):
        super().__init__(parent)

        self.theme = theme
        self.lang = lang
        self.dark = (theme == "dark")
        self.db = glogic.load_gear_db()
        self.company = "all"
        self.gear_rows = []
        self._pending_gears = None
        self._last_suggestions = None
        self._last_chart_spec = None

        self.setObjectName("BuilderRoot")
        self.setFont(QFont(font_family, 10))
        self.setLayoutDirection(Qt.RightToLeft if lang == "fa" else Qt.LeftToRight)

        self._outer = QVBoxLayout(self)
        self._build_ui()
        self.apply_theme()
        self.rebuild_gear_rows()

    # -----------------------------
    # ترجمه و تم
    # -----------------------------
    def t(self, key):
        return _t(self.lang, key)

    def apply_theme(self):
        self.setStyleSheet(_stylesheet(self.theme))
        self.dark = (self.theme == "dark")

    def set_theme(self, theme):
        if theme == self.theme:
            return
        self.theme = theme
        self.apply_theme()

    def set_lang(self, lang):
        """
        تغییر زبان: وضعیت فعلی را نگه می‌دارد، رابط را بازسازی
        و وضعیت را دوباره اعمال می‌کند.
        """
        if lang == self.lang:
            return
        state = self._collect_state()
        self.lang = lang
        self.setLayoutDirection(Qt.RightToLeft if lang == "fa" else Qt.LeftToRight)
        self._clear_layout(self._outer)
        self._build_ui()
        self.apply_theme()
        self._apply_state(state)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            elif item.layout() is not None:
                self._clear_layout(item.layout())

    # -----------------------------
    # فیلتر شرکت / موقعیت دنده
    # -----------------------------
    def _filtered(self, items):
        return glogic.filter_by_company(items, self.company)

    def _filtered_gears(self, position=None):
        gears = self._filtered(self.db.get("gears", []))
        if position is not None:
            gears = [g for g in gears if g.get("position") == position]
        return gears

    def _on_company_activated(self, idx):
        self.company = self.company_combo.itemData(idx) or "all"
        self._fill_diff_combo()
        self._refresh_code_combos()

    def _disable_company_items(self):
        model = self.company_combo.model()
        for i in range(self.company_combo.count()):
            if self.company_combo.itemData(i) in glogic.DISABLED_COMPANIES:
                item = model.item(i)
                if item is not None:
                    item.setEnabled(False)

    # -----------------------------
    # ساخت رابط کاربری
    # -----------------------------
    def _build_ui(self):
        outer = self._outer
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel(self.t("builder_title"))
        f = title.font(); f.setPointSize(13); f.setBold(True)
        title.setFont(f)
        header.addWidget(title)
        header.addStretch(1)

        header.addWidget(QLabel(self.t("preset")))
        self.preset_combo = QComboBox()
        self.preset_combo.activated.connect(self._on_preset_selected)
        header.addWidget(self.preset_combo, 1)

        save_btn = QPushButton(self.t("save"))
        save_btn.setObjectName("SuccessButton")
        save_btn.clicked.connect(self.save_preset)
        del_btn = QPushButton(self.t("delete"))
        del_btn.setObjectName("WarningButton")
        del_btn.clicked.connect(self.delete_preset)
        new_btn = QPushButton(self.t("new"))
        new_btn.clicked.connect(self.new_preset)

        header.addWidget(save_btn)
        header.addWidget(del_btn)
        header.addWidget(new_btn)
        outer.addLayout(header)

        self.refresh_preset_list()

        common = QGroupBox(self.t("common_settings"))
        g = QGridLayout(common)
        g.setHorizontalSpacing(8)
        g.setVerticalSpacing(8)

        g.addWidget(QLabel(self.t("manufacturer")), 0, 0)
        self.company_combo = QComboBox()
        self.company_combo.addItem(self.t("company_all"), "all")
        self.company_combo.addItem(self.t("company_saipa"), "saipa")
        self.company_combo.addItem(self.t("company_ikco"), "ikco")
        self.company_combo.activated.connect(self._on_company_activated)
        self._disable_company_items()
        # بازیابی شرکت انتخابی قبلی
        idx = self.company_combo.findData(self.company)
        if idx >= 0:
            self.company_combo.setCurrentIndex(idx)
        g.addWidget(self.company_combo, 0, 1)

        g.addWidget(QLabel(self.t("gear_count")), 0, 2)
        self.gear_count_spin = QSpinBox()
        self.gear_count_spin.setRange(1, 8)
        self.gear_count_spin.setValue(5)
        self.gear_count_spin.valueChanged.connect(self.rebuild_gear_rows)
        g.addWidget(self.gear_count_spin, 0, 3)

        g.addWidget(QLabel(self.t("diff")), 1, 0)
        self.diff_combo = QComboBox()
        self._fill_diff_combo()
        g.addWidget(self.diff_combo, 1, 1)
        self.diff_manual = QLineEdit()
        self.diff_manual.setPlaceholderText(self.t("diff_manual_ph"))
        g.addWidget(self.diff_manual, 1, 2, 1, 2)

        g.addWidget(QLabel(self.t("ring")), 2, 0)
        self.ring_edit = QLineEdit()
        g.addWidget(self.ring_edit, 2, 1)
        g.addWidget(QLabel(self.t("sidewall")), 2, 2)
        self.sidewall_edit = QLineEdit()
        g.addWidget(self.sidewall_edit, 2, 3)
        g.addWidget(QLabel(self.t("width")), 2, 4)
        self.pahna_edit = QLineEdit()
        g.addWidget(self.pahna_edit, 2, 5)

        g.setColumnStretch(1, 1)
        g.setColumnStretch(3, 1)
        g.setColumnStretch(5, 1)
        outer.addWidget(common)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_tab(mode=1), self.t("tab_mode1"))
        self.tabs.addTab(self._build_tab(mode=2), self.t("tab_mode2"))
        self.tabs.addTab(self._build_tab(mode=3), self.t("tab_mode3"))
        self.tabs.currentChanged.connect(lambda _idx: self.rebuild_gear_rows())
        outer.addWidget(self.tabs, 1)

    def _fill_diff_combo(self):
        self.diff_combo.blockSignals(True)
        self.diff_combo.clear()
        self.diff_combo.addItem(self.t("select_diff_ph"), 0.0)
        self.diff_combo.addItem(self.t("diff_auto"), DIFF_AUTO)
        for d in self._filtered(self.db.get("diffs", [])):
            label = f"{d.get('code','')} | {float(d.get('ratio',0)):g}"
            if d.get("name"):
                label += f" | {d['name']}"
            self.diff_combo.addItem(label, float(d.get("ratio", 0)))
        self.diff_combo.blockSignals(False)

    def _refresh_code_combos(self):
        for row in self.gear_rows:
            if "code_combo" not in row:
                continue
            combo = row["code_combo"]
            position = row.get("position")
            combo.blockSignals(True)
            combo.clear()
            combo.addItem(self.t("select_code_ph"), 0.0)
            for gitem in self._filtered_gears(position=position):
                glabel = f"{gitem.get('code','')} | {float(gitem.get('ratio',0)):g}"
                if gitem.get("name"):
                    glabel += f" | {gitem['name']}"
                combo.addItem(glabel, float(gitem.get("ratio", 0)))
            combo.blockSignals(False)

    def _build_tab(self, mode):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setSpacing(8)

        if mode == 2:
            row = QHBoxLayout()
            row.addWidget(QLabel(self.t("fixed_speed")))
            self.speed_edit = QLineEdit()
            row.addWidget(self.speed_edit, 1)
            row.addStretch(1)
            v.addLayout(row)
        elif mode == 3:
            row = QHBoxLayout()
            row.addWidget(QLabel(self.t("fixed_rpm")))
            self.rpm_edit = QLineEdit()
            row.addWidget(self.rpm_edit, 1)
            row.addStretch(1)
            v.addLayout(row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        rows_widget = QWidget()
        rows_layout = QVBoxLayout(rows_widget)
        rows_layout.setSpacing(6)
        rows_layout.addStretch(1)
        scroll.setWidget(rows_widget)
        v.addWidget(scroll, 1)

        # جعبه نتیجه با دکمه بستن (✕)
        result_box = QFrame()
        result_box.setObjectName("ResultBox")
        rb_layout = QVBoxLayout(result_box)
        rb_layout.setContentsMargins(12, 6, 12, 12)
        rb_layout.setSpacing(4)

        top_row = QHBoxLayout()
        top_row.addStretch(1)
        close_result_btn = QPushButton("✕")
        close_result_btn.setObjectName("CloseResultBtn")
        close_result_btn.setFixedSize(35, 35)
        close_result_btn.setCursor(Qt.PointingHandCursor)
        close_result_btn.setToolTip(self.t("close"))
        close_result_btn.clicked.connect(
            lambda checked=False, box=result_box: box.hide()
        )
        top_row.addWidget(close_result_btn)
        rb_layout.addLayout(top_row)

        result = QLabel("")
        result.setWordWrap(True)
        result.setTextInteractionFlags(Qt.TextSelectableByMouse)
        rb_layout.addWidget(result)

        result_box.hide()  # تا قبل از اولین محاسبه پنهان است
        v.addWidget(result_box)

        if mode in (2, 3):
            chart_btn = QPushButton(self.t("view_chart"))
            chart_btn.setObjectName("InfoButton")
            chart_btn.clicked.connect(self._open_chart_dialog)
            v.addWidget(chart_btn)

        if mode == 1:
            sug_btn = QPushButton(self.t("view_suggestions"))
            sug_btn.setObjectName("InfoButton")
            sug_btn.clicked.connect(self.show_suggestions_dialog)
            v.addWidget(sug_btn)

        v.addSpacing(8)
        btn = QPushButton(self.t("calculate"))
        btn.setObjectName("SuccessButton")
        btn.setMinimumHeight(44)
        btn.clicked.connect(self._recompute)
        v.addWidget(btn)

        page.setProperty("mode", mode)
        page.setProperty("rows_layout", rows_layout)
        page.setProperty("result_box", result_box)
        page.setProperty("result_label", result)
        return page

    # -----------------------------
    # ساخت ردیف‌های دنده
    # -----------------------------
    def rebuild_gear_rows(self):
        page = self.tabs.currentWidget()
        if page is None:
            return
        mode = page.property("mode")
        rows_layout = page.property("rows_layout")

        while rows_layout.count() > 1:
            item = rows_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.gear_rows = []
        count = self.gear_count_spin.value()

        for i in range(count):
            frame = QFrame()
            hl = QHBoxLayout(frame)
            hl.setSpacing(8)

            lbl = QLabel(f"{self.t('gear')} {i + 1}")
            lbl.setObjectName("FieldLabel")
            lbl.setMinimumWidth(52)
            hl.addWidget(lbl)

            row = {"position": i + 1}
            if mode == 1:
                speed_e = QLineEdit()
                speed_e.setPlaceholderText(self.t("speed_ph"))
                rpm_e = QLineEdit()
                rpm_e.setPlaceholderText(self.t("rpm_ph"))
                hl.addWidget(speed_e, 1)
                hl.addWidget(rpm_e, 1)
                row["speed_edit"] = speed_e
                row["rpm_edit"] = rpm_e
            else:
                code_combo = QComboBox()
                code_combo.addItem(self.t("select_code_ph"), 0.0)
                for gitem in self._filtered_gears(position=i + 1):
                    glabel = f"{gitem.get('code','')} | {float(gitem.get('ratio',0)):g}"
                    if gitem.get("name"):
                        glabel += f" | {gitem['name']}"
                    code_combo.addItem(glabel, float(gitem.get("ratio", 0)))
                ratio_e = QLineEdit()
                ratio_e.setPlaceholderText(self.t("ratio_manual_ph"))
                code_combo.activated.connect(
                    lambda idx, c=code_combo, r=ratio_e: self._on_code_selected(c, r)
                )
                hl.addWidget(code_combo, 2)
                hl.addWidget(ratio_e, 1)
                row["code_combo"] = code_combo
                row["ratio_edit"] = ratio_e

            rows_layout.insertWidget(i, frame)
            self.gear_rows.append(row)

        if self._pending_gears:
            self._apply_pending_gears()

    def _on_code_selected(self, combo, ratio_edit):
        data = combo.currentData()
        if isinstance(data, (int, float)) and data > 0:
            ratio_edit.setText(str(data))

    # -----------------------------
    # خواندن ورودی‌های مشترک
    # -----------------------------
    def _diff_selection(self):
        txt = self.diff_manual.text().strip()
        if txt:
            r = logic.parse_ratio_input(txt)
            if r:
                return ("known", r, f"{self.t('manual_diff')} {r:g}")
        data = self.diff_combo.currentData()
        if data == DIFF_AUTO:
            return ("auto", None, "")
        if isinstance(data, (int, float)) and data > 0:
            return ("known", float(data), self.diff_combo.currentText())
        return ("none", None, "")

    def _tire_cm(self):
        try:
            return logic.get_tire_circumference_cm({
                "ring": self.ring_edit.text(),
                "sidewall": self.sidewall_edit.text(),
                "pahna": self.pahna_edit.text(),
            })
        except logic.CalcError:
            return None

    def _row_ratio(self, row):
        txt = row.get("ratio_edit").text().strip()
        if txt:
            r = logic.parse_ratio_input(txt)
            if r:
                return r
        data = row.get("code_combo").currentData()
        if isinstance(data, (int, float)) and data > 0:
            return data
        return None

    # -----------------------------
    # محاسبه
    # -----------------------------
    def _recompute(self):
        page = self.tabs.currentWidget()
        if page is None:
            return
        mode = page.property("mode")
        if mode == 1:
            self._compute_mode1(page)
        elif mode == 2:
            self._compute_mode2(page)
        elif mode == 3:
            self._compute_mode3(page)

    def _compute_mode1(self, page):
        result = page.property("result_label")
        result_box = page.property("result_box")
        tire_cm = self._tire_cm()

        if tire_cm is None:
            result.setText(self.t("err_tire"))
            result_box.show()
            self._last_suggestions = None
            return

        diff_sel = self._diff_selection()
        if diff_sel[0] == "none":
            result.setText(self.t("err_diff"))
            result_box.show()
            self._last_suggestions = None
            return

        gear_data = []
        target_by_position = {}
        for i, row in enumerate(self.gear_rows):
            pos = i + 1
            speed = logic.parse_number(row["speed_edit"].text())
            rpm = logic.parse_number(row["rpm_edit"].text())
            if not speed or not rpm:
                gear_data.append({"pos": pos, "ok": False})
                continue
            wheel_rpm = (speed * 100000.0 / 60.0) / tire_cm
            if wheel_rpm <= 0:
                gear_data.append({"pos": pos, "ok": False})
                continue
            total = rpm / wheel_rpm
            target_by_position[pos] = total
            gear_data.append({"pos": pos, "ok": True, "total": total})

        if not target_by_position:
            result.setText(self.t("err_no_gear"))
            result_box.show()
            self._last_suggestions = None
            return

        gears_db = self._filtered(self.db.get("gears", []))
        diffs_db = self._filtered(self.db.get("diffs", []))

        lines = []
        if diff_sel[0] == "auto":
            suggestion = glogic.suggest_set_by_position(
                target_by_position, gears_db, diffs_db
            )
            if suggestion is None:
                result.setText(self.t("err_no_suggest"))
                result_box.show()
                self._last_suggestions = None
                return
            d = suggestion["diff"]
            dname = f" ({d['name']})" if d.get("name") else ""
            lines.append(self.t("sugg_diff_line").format(
                code=d.get('code', ''), name=dname, ratio=f"{float(d['ratio']):g}"))
            lines.append("")
            for gd in gear_data:
                pos = gd["pos"]
                if not gd["ok"]:
                    lines.append(self.t("incomplete_line").format(n=pos))
                    lines.append("")
                    continue
                total = gd["total"]
                pick = suggestion["picks"].get(pos)
                if pick:
                    m = pick["gear"]
                    mname = f" ({m['name']})" if m.get("name") else ""
                    gear_ratio_calc = total / float(d["ratio"])
                    lines.append(self.t("m1_line").format(
                        n=pos, t=f"{total:.4f}", g=f"{gear_ratio_calc:.4f}"))
                    lines.append(self.t("sugg_line").format(
                        code=m.get('code', ''), name=mname,
                        ratio=f"{float(m['ratio']):g}",
                        err=f"{m['error_percent']:.2f}"))
                else:
                    lines.append(self.t("no_sugg_gear_line").format(n=pos, t=f"{total:.4f}"))
                lines.append("")
        else:
            diff_ratio = diff_sel[1]
            lines.append(self.t("diff_line").format(label=diff_sel[2]))
            lines.append("")
            for gd in gear_data:
                pos = gd["pos"]
                if not gd["ok"]:
                    lines.append(self.t("incomplete_line").format(n=pos))
                    lines.append("")
                    continue
                total = gd["total"]
                gear_ratio_calc = total / diff_ratio
                candidates = [g for g in gears_db if g.get("position") == pos]
                match = glogic.find_closest(gear_ratio_calc, candidates)
                lines.append(self.t("m1_line").format(
                    n=pos, t=f"{total:.4f}", g=f"{gear_ratio_calc:.4f}"))
                if match:
                    mname = f" ({match['name']})" if match.get("name") else ""
                    lines.append(self.t("sugg_line").format(
                        code=match.get('code', ''), name=mname,
                        ratio=f"{float(match['ratio']):g}",
                        err=f"{match['error_percent']:.2f}"))
                else:
                    lines.append(self.t("no_sugg_line"))
                lines.append("")

        # پیام مشورت با مکانیک (به زبان فعلی برنامه)
        lines.append("")
        lines.append(self.t("mechanic_note"))

        report = "\n".join(lines).strip()
        comp_key = {"all": "company_all", "saipa": "company_saipa",
                    "ikco": "company_ikco"}.get(self.company, "company_all")
        title = f"{self.t('sugg_title')} — {self.t(comp_key)}"
        self._last_suggestions = {"title": title, "text": report}

        result.setText(
            self.t("sugg_ready").format(n=len(target_by_position)) +
            "\n" + self.t("sugg_ready_hint")
        )
        result_box.show()
        self.show_suggestions_dialog()

    def _compute_mode2(self, page):
        result = page.property("result_label")
        result_box = page.property("result_box")
        tire_cm = self._tire_cm()
        diff = self._effective_diff_simple()
        speed = logic.parse_number(self.speed_edit.text())

        if tire_cm is None or diff is None or not speed:
            result.setText(self.t("err_mode2"))
            result_box.show()
            return

        blocks = []
        totals = []
        for i, row in enumerate(self.gear_rows):
            ratio = self._row_ratio(row)
            if ratio is None:
                blocks.append(self.t("ratio_unknown_line").format(n=i + 1))
                continue
            total = ratio * diff
            totals.append(total)
            rpm = glogic.rpm_at_speed(speed, total, tire_cm)
            blocks.append(self.t("m2_line").format(n=i + 1, r=f"{ratio:.4f}", v=f"{rpm:.0f}"))
        result.setText("\n\n".join(blocks))
        result_box.show()

        self._show_chart(totals, tire_cm, fixed_speed=speed, fixed_rpm=None)

    def _compute_mode3(self, page):
        result = page.property("result_label")
        result_box = page.property("result_box")
        tire_cm = self._tire_cm()
        diff = self._effective_diff_simple()
        rpm = logic.parse_number(self.rpm_edit.text())

        if tire_cm is None or diff is None or not rpm:
            result.setText(self.t("err_mode3"))
            result_box.show()
            return

        blocks = []
        totals = []
        for i, row in enumerate(self.gear_rows):
            ratio = self._row_ratio(row)
            if ratio is None:
                blocks.append(self.t("ratio_unknown_line").format(n=i + 1))
                continue
            total = ratio * diff
            totals.append(total)
            speed = glogic.speed_at_rpm(rpm, total, tire_cm)
            blocks.append(self.t("m3_line").format(n=i + 1, r=f"{ratio:.4f}", v=f"{speed:.1f}"))
        result.setText("\n\n".join(blocks))
        result_box.show()

        self._show_chart(totals, tire_cm, fixed_speed=None, fixed_rpm=rpm)

    def _effective_diff_simple(self):
        sel = self._diff_selection()
        if sel[0] == "known":
            return sel[1]
        return None

    # -----------------------------
    # نمودار
    # -----------------------------
    def _build_chart_spec(self, totals, tire_cm, fixed_speed=None, fixed_rpm=None):
        if not totals:
            return None
        slopes = [glogic.line_slope(t, tire_cm) for t in totals]
        colors = glogic.GEAR_COLORS

        if fixed_rpm is not None:
            speeds = [(fixed_rpm / s) if s > 0 else 0.0 for s in slopes]
            max_speed = max(speeds) * 1.1 if speeds else 1
            max_rpm = fixed_rpm * 1.15
            lines, points, drops = [], [], []
            for i, (slope, spd) in enumerate(zip(slopes, speeds)):
                color = colors[i % len(colors)]
                lines.append({"slope": slope, "vmax": spd, "color": color})
                points.append({
                    "x": spd, "y": fixed_rpm,
                    "label": f"{self.t('gear')} {i + 1}: {spd:.0f} km/h",
                    "color": color,
                })
                if i > 0 and speeds[i - 1] > 0:
                    shift_speed = speeds[i - 1]
                    rpm_after = slope * shift_speed
                    drop = fixed_rpm - rpm_after
                    drops.append({
                        "x": shift_speed, "y_top": fixed_rpm,
                        "y_bottom": rpm_after,
                        "label": f"{self.t('drop')} {drop:.0f}",
                    })
            return {
                "max_speed": max_speed, "max_rpm": max_rpm,
                "lines": lines, "points": points, "drops": drops,
            }

        elif fixed_speed is not None:
            rpms = [s * fixed_speed for s in slopes]
            max_speed = fixed_speed * 1.4 if fixed_speed else 1
            max_rpm = max(rpms) * 1.15 if rpms else 1
            lines, points, drops = [], [], []
            for i, slope in enumerate(slopes):
                color = colors[i % len(colors)]
                lines.append({"slope": slope, "vmax": max_speed, "color": color})
                points.append({
                    "x": fixed_speed, "y": rpms[i],
                    "label": f"{self.t('gear')} {i + 1}: {rpms[i]:.0f} RPM",
                    "color": color,
                })
                if i > 0:
                    drop = rpms[i - 1] - rpms[i]
                    drops.append({
                        "x": fixed_speed, "y_top": rpms[i - 1],
                        "y_bottom": rpms[i],
                        "label": f"{self.t('drop')} {drop:.0f}",
                    })
            return {
                "max_speed": max_speed, "max_rpm": max_rpm,
                "lines": lines, "points": points, "drops": drops,
            }
        return None

    def _show_chart(self, totals, tire_cm, fixed_speed=None, fixed_rpm=None):
        spec = self._build_chart_spec(totals, tire_cm, fixed_speed, fixed_rpm)
        if spec is None:
            self._last_chart_spec = None
            return
        self._last_chart_spec = spec
        self._open_chart_dialog()

    def _open_chart_dialog(self):
        if not self._last_chart_spec:
            QMessageBox.information(self, self.t("chart"), self.t("chart_dialog_hint"))
            return
        dlg = ChartDialog(self._last_chart_spec, self.dark, self.theme, self.lang, self)
        dlg.exec()

    # -----------------------------
    # پنجره پیشنهادات
    # -----------------------------
    def show_suggestions_dialog(self):
        if not self._last_suggestions:
            QMessageBox.information(self, self.t("suggestions"), self.t("sugg_dialog_hint"))
            return
        dlg = SuggestionDialog(
            self._last_suggestions["title"],
            self._last_suggestions["text"],
            self.theme,
            self.lang,
            self,
        )
        dlg.exec()

    # -----------------------------
    # پریست‌ها
    # -----------------------------
    def refresh_preset_list(self):
        current = self.preset_combo.currentText()
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        self.preset_combo.addItem(self.t("select_preset_ph"))
        for name in presets.list_presets():
            self.preset_combo.addItem(name)
        idx = self.preset_combo.findText(current)
        if idx >= 0:
            self.preset_combo.setCurrentIndex(idx)
        self.preset_combo.blockSignals(False)

    def _on_preset_selected(self, index):
        if index <= 0:
            return
        name = self.preset_combo.itemText(index)
        data = presets.load_preset(name)
        if data is None:
            QMessageBox.warning(self, self.t("preset_title"), self.t("preset_not_found"))
            return
        self._apply_state(data)

    def _collect_state(self):
        gears = []
        for row in self.gear_rows:
            g = {"speed": "", "rpm": "", "code_index": 0, "ratio": ""}
            if "speed_edit" in row:
                g["speed"] = row["speed_edit"].text()
            if "rpm_edit" in row:
                g["rpm"] = row["rpm_edit"].text()
            if "code_combo" in row:
                g["code_index"] = row["code_combo"].currentIndex()
            if "ratio_edit" in row:
                g["ratio"] = row["ratio_edit"].text()
            gears.append(g)

        return {
            "sub_mode": self.tabs.currentIndex(),
            "gear_count": self.gear_count_spin.value(),
            "company_index": self.company_combo.currentIndex(),
            "diff_manual": self.diff_manual.text(),
            "diff_index": self.diff_combo.currentIndex(),
            "ring": self.ring_edit.text(),
            "sidewall": self.sidewall_edit.text(),
            "pahna": self.pahna_edit.text(),
            "fixed_speed": getattr(self, "speed_edit", QLineEdit()).text(),
            "fixed_rpm": getattr(self, "rpm_edit", QLineEdit()).text(),
            "gears": gears,
            "suggestions": self._last_suggestions,
        }

    def save_preset(self):
        if self.preset_combo.currentIndex() == 0:
            default = ""
        else:
            default = self.preset_combo.currentText()
        name, ok = QInputDialog.getText(
            self, self.t("save_preset_title"), self.t("preset_name"), text=default
        )
        if not ok or not name.strip():
            return
        state = self._collect_state()
        try:
            presets.save_preset(name.strip(), state)
            self.refresh_preset_list()
            idx = self.preset_combo.findText(name.strip())
            if idx >= 0:
                self.preset_combo.setCurrentIndex(idx)
        except Exception as e:
            QMessageBox.critical(self, self.t("error"), self.t("save_preset_fail") + f"\n{e}")

    def delete_preset(self):
        if self.preset_combo.currentIndex() == 0:
            return
        name = self.preset_combo.currentText()
        answer = QMessageBox.question(
            self, self.t("delete_preset_title"), self.t("delete_preset_q").format(name=name)
        )
        if answer == QMessageBox.Yes:
            presets.delete_preset(name)
            self.refresh_preset_list()

    def new_preset(self):
        self.diff_manual.clear()
        self.diff_combo.setCurrentIndex(0)
        self.ring_edit.clear()
        self.sidewall_edit.clear()
        self.pahna_edit.clear()
        self._last_suggestions = None
        self._last_chart_spec = None
        if hasattr(self, "speed_edit"):
            self.speed_edit.clear()
        if hasattr(self, "rpm_edit"):
            self.rpm_edit.clear()
        for row in self.gear_rows:
            for key in ("speed_edit", "rpm_edit", "ratio_edit"):
                if key in row:
                    row[key].clear()
            if "code_combo" in row:
                row["code_combo"].setCurrentIndex(0)

    def _apply_state(self, data):
        try:
            self._pending_gears = data.get("gears", [])
            self.gear_count_spin.setValue(int(data.get("gear_count", 5)))

            ci = int(data.get("company_index", 0))
            self.company_combo.setCurrentIndex(ci)
            self.company = self.company_combo.itemData(ci) or "all"

            self.diff_manual.setText(str(data.get("diff_manual", "")))
            self._fill_diff_combo()
            di = int(data.get("diff_index", 0))
            if di < self.diff_combo.count():
                self.diff_combo.setCurrentIndex(di)

            self.ring_edit.setText(str(data.get("ring", "")))
            self.sidewall_edit.setText(str(data.get("sidewall", "")))
            self.pahna_edit.setText(str(data.get("pahna", "")))
            if hasattr(self, "speed_edit"):
                self.speed_edit.setText(str(data.get("fixed_speed", "")))
            if hasattr(self, "rpm_edit"):
                self.rpm_edit.setText(str(data.get("fixed_rpm", "")))

            self._last_suggestions = data.get("suggestions")
            self._last_chart_spec = None

            self.tabs.setCurrentIndex(int(data.get("sub_mode", 0)))
            self.rebuild_gear_rows()
        except Exception as e:
            QMessageBox.warning(self, self.t("preset_title"), self.t("restore_fail") + f"\n{e}")

    def _apply_pending_gears(self):
        gears = self._pending_gears or []
        for i, row in enumerate(self.gear_rows):
            if i >= len(gears):
                break
            g = gears[i]
            if "speed_edit" in row:
                row["speed_edit"].setText(str(g.get("speed", "")))
            if "rpm_edit" in row:
                row["rpm_edit"].setText(str(g.get("rpm", "")))
            if "code_combo" in row:
                row["code_combo"].setCurrentIndex(int(g.get("code_index", 0)))
            if "ratio_edit" in row:
                row["ratio_edit"].setText(str(g.get("ratio", "")))
        self._pending_gears = None
