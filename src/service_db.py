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


def get_description(name):
    try:
        from locale_mgr import LANG
    except ImportError:
        try:
            from src.locale_mgr import LANG
        except ImportError:
            LANG = "tr"

    entry = DESCRIPTIONS.get(name)
    if entry:
        desc = entry.get("desc_" + LANG, entry.get("desc"))
        oneri = entry.get("oneri_" + LANG, entry.get("suggestion"))
        return desc, entry.get("tip"), oneri
    if "@" in name:
        base = name.split("@")[0] + "@"
        template_name = _BASE_NAMES.get(base)
        if template_name:
            entry = DESCRIPTIONS.get(template_name)
            if entry:
                desc = entry.get("desc_" + LANG, entry.get("desc"))
                oneri = entry.get("oneri_" + LANG, entry.get("suggestion"))
                return desc, entry.get("tip"), oneri
    return None, None, None
