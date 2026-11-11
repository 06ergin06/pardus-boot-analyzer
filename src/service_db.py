import os
import json

_current_dir = os.path.dirname(os.path.abspath(__file__))
_json_path = os.path.join(_current_dir, "services_data.json")

try:
    with open(_json_path, "r", encoding="utf-8") as f:
        DESCRIPTIONS = json.load(f)
except Exception:
    DESCRIPTIONS = {}

_BASE_NAMES = {}
for key in list(DESCRIPTIONS.keys()):
    if "@" in key:
        base = key.split("@")[0] + "@"
        _BASE_NAMES[base] = key


def _lang():
    try:
        from locale_mgr import LANG
    except ImportError:
        try:
            from src.locale_mgr import LANG
        except ImportError:
            LANG = "tr"
    return LANG


def _service_type(entry):
    if entry.get("critical"):
        return "critical"
    if entry.get("required"):
        return "required"
    return "suggestion"


def _localized(entry, field, lang):
    return (
        entry.get(f"{field}_{lang}")
        or entry.get(f"{field}_tr")
        or entry.get(f"{field}_en")
        or ""
    )


def _parse_entry(entry, lang):
    return (
        _localized(entry, "description", lang),
        _service_type(entry),
        _localized(entry, "suggestion", lang),
    )


def get_description(name):
    lang = _lang()
    entry = DESCRIPTIONS.get(name)
    if entry:
        return _parse_entry(entry, lang)
    if "@" in name:
        base = name.split("@")[0] + "@"
        template_name = _BASE_NAMES.get(base)
        if template_name:
            entry = DESCRIPTIONS.get(template_name)
            if entry:
                return _parse_entry(entry, lang)
    return None, None, None
