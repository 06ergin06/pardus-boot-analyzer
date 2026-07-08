import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import threading
from src.system_manager import SystemManager
from src.service_db import get_description


STATUS_COLORS = {
    "active": "#2e7d32",
    "inactive": "#c62828",
    "disabled": "#6a1b9a",
    "masked": "#795548",
    "static": "#1565c0",
    "activating": "#e65100",
    "deactivating": "#e65100",
}

STATUS_TR = {
    "active": "Aktif",
    "inactive": "Pasif",
    "disabled": "Devre Disi",
    "masked": "Maskeli",
    "static": "Statik",
    "activating": "Etkinlesiyor",
    "deactivating": "Devre Disi",
}

FILTER_MAP = {
    0: "all",
    1: "active",
    2: "inactive",
    3: "disabled",
    4: "masked",
}

TIP_MAP = {
    0: "all",
    1: "kritik",
    2: "oneri",
    3: "gerekli",
}

VIEW_MAP = {
    0: "services",
    1: "disabled",
    2: "devices",
}


def parse_blame_time(time_str):
    if not time_str:
        return 0
    time_str = time_str.strip()
    if "min" in time_str:
        import re
        m = re.match(r"([\d.]+)\s*min\s+([\d.]+)(ms|s)?", time_str)
        if m:
            minutes = float(m.group(1))
            val = float(m.group(2))
            unit = m.group(3) or "s"
            seconds = val / 1000 if unit == "ms" else val
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
    tr = STATUS_TR.get(status, status)
    color = STATUS_COLORS.get(status, "#000000")
    return f'<span foreground="{color}">\u25cf</span> {tr}'


def _is_dark_theme():
    try:
        s = Gtk.Settings.get_default()
        if s.get_property("gtk-application-prefer-dark-theme"):
            return True
        name = (s.get_property("gtk-theme-name") or "").lower()
        if any(w in name for w in ("dark", "black", "night", "adwaita")):
            if "adwaita" in name:
                return s.get_property("gtk-application-prefer-dark-theme")
            return True
    except Exception:
        pass
    return False


class Controller:
    def __init__(self, builder):
        self.builder = builder
        self.manager = SystemManager()

        self._all_data = []
        self._all_data_map = {}
        self._all_device_data = []
        self._status_filter = "all"
        self._tip_filter = "all"
        self._search_text = ""
        self._debounce_id = 0
        self._updating_toggles = False

        self.liststore = builder.get_object("service_liststore")
        self.treeview = builder.get_object("service_treeview")
        self.selection = builder.get_object("service_selection")
        self.boot_time_label = builder.get_object("boot_time_label")
        self.service_count_label = builder.get_object("service_count_label")
        self.search_entry = builder.get_object("search_entry")
        self.status_label = builder.get_object("status_label")
        self.filter_combo = builder.get_object("filter_combo")
        self.tip_combo = builder.get_object("tip_combo")
        self.view_combo = builder.get_object("view_combo")
        self.detail_name = builder.get_object("detail_name")
        self.detail_desc = builder.get_object("detail_desc")
        self.detail_suggestion = builder.get_object("detail_suggestion")
        self.main_window = builder.get_object("main_window")
        self.btn_toggle_enable = builder.get_object("btn_toggle_enable")
        self.btn_toggle_run = builder.get_object("btn_toggle_run")
        self.btn_toggle_mask = builder.get_object("btn_toggle_mask")

        self._load_css()
        self._connect_signals()
        self.load_all()

    def _load_css(self):
        css_file = "ui/style-dark.css" if _is_dark_theme() else "ui/style.css"
        provider = Gtk.CssProvider()
        try:
            provider.load_from_path(css_file)
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception:
            pass

    def set_status(self, text):
        self.status_label.set_text(text)

    def _connect_signals(self):
        self.builder.get_object("btn_refresh").connect("clicked", self.load_all)
        self.btn_toggle_enable.connect("toggled", self._on_toggle_enable)
        self.btn_toggle_run.connect("toggled", self._on_toggle_run)
        self.btn_toggle_mask.connect("toggled", self._on_toggle_mask)
        self.builder.get_object("btn_show_log").connect("clicked", self._on_show_log)
        self.search_entry.connect("changed", self._on_search_changed)
        self.selection.connect("changed", self._on_selection_changed)
        self.filter_combo.connect("changed", self._on_filter_changed)
        self.tip_combo.connect("changed", self._on_tip_changed)
        self.view_combo.connect("changed", self._on_view_changed)

    def load_all(self, *args):
        self.liststore.clear()
        self._all_data_map = {}
        self.detail_name.set_text("Servis secilmedi")
        self.detail_desc.set_text("Bir servis secin.")
        self.detail_suggestion.set_text("")
        self.service_count_label.set_text("0 servis")
        self.set_status("Yukleniyor...")
        GLib.timeout_add(10, self._do_load)

    def _do_load(self):
        try:
            services = self.manager.get_services()
            enabled_map = self.manager.get_unit_file_states()
            blame_data = {}
            for item in self.manager.get_blame_data()[0]:
                blame_data[item["name"]] = {
                    "time_str": item["time"],
                    "seconds": parse_blame_time(item["time"]),
                }
            total_time, _ = self.manager.get_total_boot_time()
        except Exception as e:
            self.set_status(f"Hata: {str(e)}")
            self.service_count_label.set_text("Hata")
            return False

        self.boot_time_label.set_text(f"Acilis: {total_time}")

        self._all_data = []
        for svc in services:
            name = svc["name"]
            if svc["load"] == "not-found":
                continue
            if not any(name.endswith(s) for s in
                       (".service", ".mount", ".device", ".swap", ".socket", ".target")):
                continue
            blame_info = blame_data.get(name, {"time_str": "", "seconds": 0})
            desc, tip, oneri = get_description(name)
            if not desc:
                desc = svc.get("description", "")

            self._all_data.append({
                "name": name,
                "active": svc["active"],
                "sub": svc["sub"],
                "enabled": enabled_map.get(name, "unknown"),
                "time_str": blame_info["time_str"],
                "seconds": blame_info["seconds"],
                "desc": desc,
                "tip": tip or "",
                "oneri": oneri or "",
            })

        self._all_data.sort(key=lambda x: (-x["seconds"], x["name"]))
        self._all_data_map = {d["name"]: d for d in self._all_data}
        self._apply_filters()
        self.set_status("")
        return False

    def _update_count_label(self):
        view = VIEW_MAP.get(self.view_combo.get_active(), "services")
        n = len(self.liststore)
        if view == "devices":
            t = len(self._all_device_data)
        else:
            t = len(self._all_data)
        self.service_count_label.set_text(f"{n} servis" if n == t else f"{n}/{t} servis")

    def _apply_filters(self):
        old_selection = self._get_selected_name()
        self.liststore.clear()

        self._updating_toggles = True
        self.btn_toggle_enable.set_active(False)
        self.btn_toggle_run.set_active(False)
        self.btn_toggle_mask.set_active(False)
        self._updating_toggles = False

        view = VIEW_MAP.get(self.view_combo.get_active(), "services")

        if view == "devices":
            self._do_load_devices()
            return

        q = self._search_text.lower()
        for d in self._all_data:
            if q and q not in d["name"].lower():
                continue
            if not self._matches_status(d["active"], d["sub"], d.get("enabled", ""), view):
                continue
            if self._tip_filter != "all" and d["tip"] != self._tip_filter:
                continue
            self.liststore.append([
                d["name"],
                make_status_markup(d["active"]),
                d["sub"],
                d["time_str"],
                d["desc"],
                d["tip"],
                d["oneri"],
                "",
            ])

        self._update_count_label()

        # Restore selection and update toggle buttons
        if old_selection:
            for i in range(len(self.liststore)):
                if self.liststore[i][0] == old_selection:
                    self.selection.select_path(Gtk.TreePath(i))
                    break
        self._on_selection_changed()

    def _do_load_devices(self):
        try:
            devs = self.manager.get_device_units()
        except Exception as e:
            self.set_status(f"Aygit hatasi: {e}")
            self._update_count_label()
            return
        self._all_device_data = []
        for d in devs:
            desc = d.get("description", "")
            self._all_device_data.append({
                "name": d["name"],
                "active": d["active"],
                "sub": d["sub"],
                "enabled": "unknown",
                "time_str": "",
                "seconds": 0,
                "desc": desc,
                "tip": "",
                "oneri": "",
            })
        self.set_status("")
        for d in self._all_device_data:
            self.liststore.append([
                d["name"],
                make_status_markup(d["active"]),
                d["sub"],
                d["time_str"],
                d["desc"],
                d["tip"],
                d["oneri"],
                "",
            ])
        self._update_count_label()

    def _matches_status(self, active, sub, enabled="", view="services"):
        if view == "disabled":
            return enabled == "disabled" or sub == "disabled"
        f = self._status_filter
        if f == "all":
            return True
        if f == "active":
            return active == "active"
        if f == "inactive":
            return active == "inactive"
        if f == "disabled":
            return sub == "disabled" or active == "disabled"
        if f == "masked":
            return sub == "masked"
        return True

    def _on_view_changed(self, *args):
        self._apply_filters()

    def _on_filter_changed(self, *args):
        self._status_filter = FILTER_MAP.get(self.filter_combo.get_active(), "all")
        self._apply_filters()

    def _on_tip_changed(self, *args):
        self._tip_filter = TIP_MAP.get(self.tip_combo.get_active(), "all")
        self._apply_filters()

    def _on_search_changed(self, *args):
        self._search_text = self.search_entry.get_text()
        if self._debounce_id:
            GLib.source_remove(self._debounce_id)
        self._debounce_id = GLib.timeout_add(250, self._apply_filters)

    def _get_selected_row(self):
        m, i = self.selection.get_selected()
        return m[i] if i is not None else None

    def _get_selected_name(self):
        r = self._get_selected_row()
        return r[0] if r is not None else None

    def _on_selection_changed(self, *args):
        r = self._get_selected_row()
        if r is None:
            self.detail_name.set_text("Servis secilmedi")
            self.detail_desc.set_text("Bir servis secin.")
            self.detail_suggestion.set_text("")
            self._set_toggle_sensitive(False)
            return

        d = self._all_data_map.get(r[0])
        active = d["active"] if d else ""
        color = STATUS_COLORS.get(active, "#000000")
        self.detail_name.set_markup(
            f"<b>{r[0]}</b>  \u2014  <span foreground='{color}'>{active}</span>"
        )
        self.detail_desc.set_text(r[4])
        tip = r[5]
        oneri = r[6]
        if oneri:
            if tip == "kritik":
                self.detail_suggestion.set_markup(
                    "<span foreground='#c62828' weight='bold'>KRITIK: </span>"
                    f"<span foreground='#444746'>{oneri}</span>"
                )
            elif tip == "oneri":
                self.detail_suggestion.set_markup(
                    "<span foreground='#2e7d32'>ONERI: </span>"
                    f"<span foreground='#444746'>{oneri}</span>"
                )
            else:
                self.detail_suggestion.set_markup(
                    f"<span foreground='#444746'>{oneri}</span>"
                )
        else:
            self.detail_suggestion.set_text("")

        self._update_toggle_buttons(r[0], d)

    def _set_toggle_sensitive(self, sensitive):
        self.btn_toggle_enable.set_sensitive(sensitive)
        self.btn_toggle_run.set_sensitive(sensitive)
        self.btn_toggle_mask.set_sensitive(sensitive)

    def _update_toggle_buttons(self, name, d=None):
        if d is None:
            d = self._all_data_map.get(name)
        if d is None:
            self._set_toggle_sensitive(False)
            return

        view = VIEW_MAP.get(self.view_combo.get_active(), "services")
        if view == "devices":
            self._set_toggle_sensitive(False)
            return

        self._set_toggle_sensitive(True)
        sub = d["sub"]
        active_state = d["active"]
        enabled_state = d.get("enabled", "unknown")

        is_enabled = enabled_state in ("enabled", "enabled-runtime", "generated")
        is_running = active_state == "active"
        is_masked = sub == "masked" or enabled_state == "masked"

        self._updating_toggles = True
        self.btn_toggle_enable.set_active(is_enabled)
        self.btn_toggle_enable.set_label("Devre Disi" if is_enabled else "Etkinlestir")
        self.btn_toggle_run.set_active(is_running)
        self.btn_toggle_run.set_label("Durdur" if is_running else "Baslat")
        self.btn_toggle_mask.set_active(is_masked)
        self.btn_toggle_mask.set_label("Kaldir" if is_masked else "Maskele")
        self._updating_toggles = False

        if enabled_state in ("static", "indirect", "masked", "generated"):
            self.btn_toggle_enable.set_sensitive(False)
        if sub == "masked" or enabled_state == "masked":
            self.btn_toggle_run.set_sensitive(False)
        if active_state in ("activating", "deactivating"):
            self.btn_toggle_run.set_sensitive(False)

    def _get_toggle_action(self, toggle, active_true, active_false):
        if self._updating_toggles:
            return None
        action = active_true if toggle.get_active() else active_false
        n = self._get_selected_name()
        if not n:
            self.set_status("Bir servis secin.")
            toggle.set_active(not toggle.get_active())
            return None
        return (action, n)

    def _on_toggle_enable(self, toggle, *args):
        r = self._get_toggle_action(toggle, "enable", "disable")
        if r:
            self._run_systemctl(r[0], r[1], self.load_all)

    def _on_toggle_run(self, toggle, *args):
        r = self._get_toggle_action(toggle, "start", "stop")
        if r:
            self._run_systemctl(r[0], r[1], self.load_all)

    def _on_toggle_mask(self, toggle, *args):
        if self._updating_toggles:
            return
        action = "mask" if toggle.get_active() else "unmask"
        n = self._get_selected_name()
        if not n:
            self.set_status("Bir servis secin.")
            toggle.set_active(not toggle.get_active())
            return

        if action == "mask":
            d = self._all_data_map.get(n)
            tip = d["tip"] if d else ""
            warn = ("\n\nBu servis sistem icin KRITIK olarak isaretlenmistir. "
                    "Kapatmaniz sorunlara yol acabilir!") if tip == "kritik" else ""
            dlg = Gtk.MessageDialog(
                parent=self.main_window, flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.WARNING if tip == "kritik" else Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                message_format=f"'{n}' servisini maskelemek istiyor musunuz?"
            )
            if warn:
                dlg.format_secondary_text(warn)
            resp = dlg.run()
            dlg.destroy()
            if resp != Gtk.ResponseType.YES:
                toggle.set_active(False)
                return

        self._run_systemctl(action, n, self.load_all)

    def _run_systemctl(self, action, name, cb):
        self.set_status(f"{action} baslatildi...")
        def task():
            try:
                m = {"enable": self.manager.enable_service,
                     "disable": self.manager.disable_service,
                     "start": self.manager.start_service,
                     "stop": self.manager.stop_service,
                     "mask": self.manager.mask_service,
                     "unmask": self.manager.unmask_service}
                fn = m.get(action)
                ok, msg = fn(name) if fn else (False, f"Bilinmeyen: {action}")
                GLib.idle_add(self._on_cmd_done, ok, msg, cb)
            except Exception as e:
                GLib.idle_add(self._on_cmd_done, False, str(e), cb)
        threading.Thread(target=task, daemon=True).start()

    def _on_cmd_done(self, ok, msg, cb):
        self.set_status(msg)
        if ok and cb:
            cb()

    def _on_show_log(self, *args):
        n = self._get_selected_name()
        if not n:
            self.set_status("Bir servis secin.")
            return
        self.set_status("Log yukleniyor...")
        def task():
            try:
                log = self.manager.get_journal_log(n)
                GLib.idle_add(self.set_status, log or "Log bulunamadi.")
            except Exception as e:
                GLib.idle_add(self.set_status, f"Hata: {e}")
        threading.Thread(target=task, daemon=True).start()
