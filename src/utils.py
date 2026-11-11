import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os
import json
import re
from src import locale_mgr
from src.locale_mgr import tr

STATUS_COLORS = {
    "active": "#198754",      # Green
    "inactive": "#dc3545",    # Red
    "disabled": "#6f42c1",    # Purple
    "masked": "#795548",      # Brown
    "static": "#0d6efd",      # Blue
    "activating": "#fd7e14",  # Orange
    "deactivating": "#fd7e14",
}

STATUS_LABELS = {
    "active": tr("su_an_calisiyor"),
    "inactive": tr("su_an_durduruldu"),
    "disabled": tr("boot_calismayacak"),
    "masked": tr("maskelenmis_kapali"),
    "static": tr("statik_sabit"),
    "activating": tr("gecis_yapiyor") + "...",
    "deactivating": tr("gecis_yapiyor") + "...",
}

FILTER_MAP = {
    0: "all",
    1: "active",
    2: "inactive",
    3: "disabled",
    4: "masked",
}

SERVICE_TYPE_MAP = {
    0: "all",
    1: "critical",
    2: "suggestion",
    3: "required",
}

VIEW_MAP = {
    0: "services",
    1: "other",
    2: "devices",
}

_current_dir = os.path.dirname(os.path.abspath(__file__))
_json_path = os.path.join(_current_dir, "profiles_data.json")
try:
    with open(_json_path, "r", encoding="utf-8") as _f:
        _config_data = json.load(_f)
except Exception:
    _config_data = {
        "profiles": {},
        "safe_to_disable_services": [],
        "labels": {}
    }

SAFE_TO_DISABLE_SERVICES = set(_config_data.get("safe_to_disable_services", []))


def profile_service_labels():
    lang = locale_mgr.LANG
    return {
        name: values.get(lang, values.get("tr", name))
        for name, values in _config_data.get("labels", {}).items()
    }

def parse_blame_time(time_str):
    if not time_str:
        return 0
    time_str = time_str.strip()
    if "min" in time_str:
        m = re.match(r"([\d.]+)\s*min(?:\s+([\d.]+)(ms|s)?)?", time_str)
        if m:
            minutes = float(m.group(1))
            val_str = m.group(2)
            if val_str:
                val = float(val_str)
                unit = m.group(3) or "s"
                seconds = val / 1000 if unit == "ms" else val
            else:
                seconds = 0.0
            return minutes * 60 + seconds
        return 0
    if time_str.endswith("us"):
        return float(time_str.rstrip("us")) / 1000000
    if time_str.endswith("ms"):
        return float(time_str.rstrip("ms")) / 1000
    if time_str.endswith("u"):
        return float(time_str.rstrip("u")) / 1000000
    if time_str.endswith("s"):
        return float(time_str.rstrip("s"))
    if time_str.endswith("m"):
        return float(time_str.rstrip("m")) * 60
    if time_str.endswith("h"):
        return float(time_str.rstrip("h")) * 3600
    return 0

def make_status_markup(status):
    translation = STATUS_LABELS.get(status, status)
    color = STATUS_COLORS.get(status, "#6c757d")
    return f'<span foreground="{color}">\u25cf</span> <b>{translation}</b>'

def _is_dark_theme():
    val = (os.environ.get("GTK_THEME") or "").lower()
    if "dark" in val:
        return True
    try:
        s = Gtk.Settings.get_default()
        if s.get_property("gtk-application-prefer-dark-theme"):
            return True
        name = (s.get_property("gtk-theme-name") or "").lower()
        if any(w in name for w in ("dark", "black", "night", "adwaita", "tokyo", "dracula")):
            if "adwaita" in name:
                return s.get_property("gtk-application-prefer-dark-theme")
            return True
    except Exception:
        pass
    return False
