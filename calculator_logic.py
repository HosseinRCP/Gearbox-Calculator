"""
فایل منطق و محاسبات
این فایل هیچ ارتباطی به رابط کاربری ندارد.
"""

import math


class CalcError(Exception):
    """
    خطای محاسباتی.
    به جای متن، فقط یک کلید خطا می‌فرستد
    تا رابط کاربری آن را ترجمه و نمایش دهد.
    """

    def __init__(self, key):
        self.key = key
        super().__init__(key)


_DIGIT_MAP = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹" + "٠١٢٣٤٥٦٧٨٩",
    "0123456789" + "0123456789",
)


def normalize_text(value):
    """
    تبدیل اعداد فارسی/عربی به انگلیسی و یکدست‌سازی اعشار
    """
    s = str(value).strip().translate(_DIGIT_MAP)
    s = s.replace("٫", ".").replace(",", ".")
    return s


def safe_ascii(value):
    """
    برای خروجی PDF انگلیسی، کاراکترها را امن می‌کند.
    """
    return normalize_text(value).encode("latin-1", "ignore").decode("latin-1")


def _check_finite(value):
    """
    جلوگیری از نمایش نتیجه‌های بی‌نهایت (ورودی‌های نجومی)
    """
    if not math.isfinite(value):
        raise CalcError("invalid_number")
    return value


def parse_number(value):
    """
    تبدیل متن به عدد.
    اگر تبدیل نشود یا عدد نامعتبر باشد (nan/inf)، None برمی‌گرداند.
    """
    s = normalize_text(value)
    if not s:
        return None

    try:
        number = float(s)
    except ValueError:
        return None

    if not math.isfinite(number):
        return None

    return number


def parse_ratio_input(value):
    """
    تبدیل ورودی ضریب به عدد.

    مثال‌های قابل قبول:
    0.745
    35/47
    """
    s = normalize_text(value)
    if not s:
        return None

    if "/" in s:
        parts = s.split("/")
        if len(parts) != 2:
            return None

        numerator = parse_number(parts[0])
        denominator = parse_number(parts[1])

        if numerator is None or denominator is None or denominator == 0:
            return None

        ratio = numerator / denominator
    else:
        ratio = parse_number(s)
        if ratio is None:
            return None

    if not math.isfinite(ratio) or ratio <= 0:
        return None

    return ratio


def extract_ratio_from_code(value):
    """
    تبدیل کد ۴ رقمی به ضریب.

    مثال:
    4735 => 35 / 47
    """
    s = normalize_text(value)

    if len(s) != 4 or not s.isdigit():
        return None

    denominator = int(s[:2])   # 47
    numerator = int(s[2:])     # 35

    if denominator == 0 or numerator == 0:
        return None

    return numerator / denominator


def get_positive(values, key):
    """
    گرفتن یک عدد مثبت از دیکشنری ورودی‌ها.
    """
    value = parse_number(values.get(key, ""))

    if value is None or value <= 0:
        raise CalcError("invalid_number")

    return value


def get_ratio(values, side, input_mode):
    """
    گرفتن ضریب دنده یا دیفرانسیل.

    side:
        "gear" یا "diff"

    input_mode:
        "code" یا "ratio"
    """
    if input_mode == "code":
        value = values.get(f"{side}_code", "")
        ratio = extract_ratio_from_code(value)

        if ratio is None:
            raise CalcError("invalid_code")
    else:
        value = values.get(f"{side}_ratio", "")
        ratio = parse_ratio_input(value)

        if ratio is None:
            raise CalcError("invalid_ratio")

    return ratio


def get_tire_circumference_cm(values):
    """
    محاسبه محیط لاستیک بر حسب سانتی‌متر
    """
    ring = get_positive(values, "ring")
    sidewall = get_positive(values, "sidewall")
    pahna = get_positive(values, "pahna")

    b = (pahna / 10.0) * (sidewall / 100.0)
    a = ring * 2.54
    p = _check_finite((a + (b * 2)) * math.pi)

    if p <= 0:
        raise CalcError("invalid_number")

    return p


def calculate_speed(values, input_mode):
    """
    محاسبه سرعت از روی دور موتور
    """
    rpm = get_positive(values, "rpm")
    gear = get_ratio(values, "gear", input_mode)
    diff = get_ratio(values, "diff", input_mode)
    p = get_tire_circumference_cm(values)

    total_ratio = _check_finite(gear * diff)
    wheel_rpm = rpm / total_ratio
    speed = _check_finite((p / 100000.0 * 60.0) * wheel_rpm)

    return {
        "speed": speed,
        "total_ratio": total_ratio,
        "wheel_rpm": wheel_rpm,
        "tire_circumference_cm": p,
    }


def calculate_rpm(values, input_mode):
    """
    محاسبه دور موتور از روی سرعت
    """
    speed = get_positive(values, "speed")
    gear = get_ratio(values, "gear", input_mode)
    diff = get_ratio(values, "diff", input_mode)
    p = get_tire_circumference_cm(values)

    total_ratio = _check_finite(gear * diff)
    wheel_rpm = (speed * 100000.0 / 60.0) / p
    rpm = _check_finite(wheel_rpm * total_ratio)

    return {
        "rpm": rpm,
        "total_ratio": total_ratio,
        "wheel_rpm": wheel_rpm,
        "tire_circumference_cm": p,
    }


def calculate_missing(values, input_mode, known_side):
    """
    محاسبه ضریب گمشده از روی سرعت و دور موتور

    known_side:
        "diff"  → ضریب دیفرانسیل معلوم است
        "gear"  → ضریب دنده معلوم است
    """
    if known_side not in ("diff", "gear"):
        raise CalcError("invalid_number")

    speed = get_positive(values, "speed")
    rpm = get_positive(values, "rpm")
    p = get_tire_circumference_cm(values)

    wheel_rpm = _check_finite((speed * 100000.0 / 60.0) / p)
    total_ratio = _check_finite(rpm / wheel_rpm)

    known_ratio = get_ratio(values, known_side, input_mode)
    unknown_ratio = _check_finite(total_ratio / known_ratio)
    unknown_side = "gear" if known_side == "diff" else "diff"

    return {
        "total_ratio": total_ratio,
        "known_side": known_side,
        "known_ratio": known_ratio,
        "unknown_side": unknown_side,
        "unknown_ratio": unknown_ratio,
        "wheel_rpm": wheel_rpm,
    }