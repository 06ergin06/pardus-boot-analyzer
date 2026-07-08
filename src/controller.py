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
    elif time_str.endswith("us"):
        return float(time_str.rstrip("us")) / 1000000
    elif time_str.endswith("ms"):
        return float(time_str.rstrip("ms")) / 1000
    elif time_str.endswith("u"):
        return float(time_str.rstrip("u")) / 1000000
    elif time_str.endswith("s"):
        return float(time_str.rstrip("s"))
    elif time_str.endswith("m"):
        return float(time_str.rstrip("m")) * 60
    elif time_str.endswith("h"):
        return float(time_str.rstrip("h")) * 3600
    return 0


def format_time(seconds):
    if seconds >= 60:
        m = int(seconds // 60)
        s = seconds % 60
        return f"{m}dk {s:.1f}s"
    elif seconds >= 1:
        return f"{seconds:.3f}s"
    else:
        return f"{int(seconds * 1000)}ms"


def make_status_markup(status):
    tr = STATUS_TR.get(status, status)
    color = STATUS_COLORS.get(status, "#000000")
    return f'<span foreground="{color}">\u25cf</span> {tr}'


class Controller:
    def __init__(self, builder):
        self.builder = builder
        self.manager = SystemManager()

        self._all_data = []
        self._all_data_map = {}
        self._current_filter = "all"
        self._search_text = ""
        self._debounce_id = 0

        self.liststore = builder.get_object("service_liststore")
        self.treeview = builder.get_object("service_treeview")
        self.selection = builder.get_object("service_selection")
        self.boot_time_label = builder.get_object("boot_time_label")
        self.service_count_label = builder.get_object("service_count_label")
        self.search_entry = builder.get_object("search_entry")
        self.log_textview = builder.get_object("log_textview")
        self.detail_name = builder.get_object("detail_name")
        self.detail_desc = builder.get_object("detail_desc")
        self.detail_suggestion = builder.get_object("detail_suggestion")
        self.main_window = builder.get_object("main_window")

        self._load_css()
        self._connect_signals()
        self.load_all()

    def _load_css(self):
        provider = Gtk.CssProvider()
        try:
            provider.load_from_path("ui/style.css")
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception:
            pass

        try:
            settings = Gtk.Settings.get_default()
            settings.set_property("gtk-application-prefer-dark-theme", False)
        except Exception:
            pass

    def _connect_signals(self):
        self.builder.get_object("btn_refresh").connect("clicked", self.load_all)
        self.builder.get_object("btn_enable").connect("clicked", self._on_enable)
        self.builder.get_object("btn_disable").connect("clicked", self._on_disable)
        self.builder.get_object("btn_mask").connect("clicked", self._on_mask)
        self.builder.get_object("btn_unmask").connect("clicked", self._on_unmask)
        self.builder.get_object("btn_show_log").connect("clicked", self._on_show_log)
        self.search_entry.connect("changed", self._on_search_changed)
        self.selection.connect("changed", self._on_selection_changed)

        for btn_name, state in [
            ("filter_all", "all"),
            ("filter_active", "active"),
            ("filter_inactive", "inactive"),
            ("filter_disabled", "disabled"),
            ("filter_masked", "masked"),
        ]:
            self.builder.get_object(btn_name).connect(
                "toggled", self._on_filter_toggled, state
            )

    def load_all(self, *args):
        self.liststore.clear()
        self._all_data_map = {}
        self.detail_name.set_text("Servis secilmedi")
        self.detail_desc.set_text("Detaylar icin bir servis secin.")
        self.detail_suggestion.set_text("")
        self.service_count_label.set_text("0 servis")
        self.log_textview.get_buffer().set_text("Yukleniyor...")

        GLib.timeout_add(10, self._do_load)

    def _do_load(self):
        try:
            services = self.manager.get_services()
            blame_data = {}
            for item in self.manager.get_blame_data()[0]:
                blame_data[item["name"]] = {
                    "time_str": item["time"],
                    "seconds": parse_blame_time(item["time"]),
                }
            total_time, _ = self.manager.get_total_boot_time()
        except Exception as e:
            self.log_textview.get_buffer().set_text(f"Hata: {str(e)}")
            self.service_count_label.set_text("Hata")
            return False

        self.boot_time_label.set_text(f"Toplam Acilis Suresi: {total_time}")

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
                "time_str": blame_info["time_str"],
                "seconds": blame_info["seconds"],
                "desc": desc,
                "tip": tip or "",
                "oneri": oneri or "",
            })

        self._all_data.sort(key=lambda x: (-x["seconds"], x["name"]))
        self._all_data_map = {d["name"]: d for d in self._all_data}
        self._apply_filters()
        return False

    def _update_count_label(self):
        count = len(self.liststore)
        total = len(self._all_data)
        if count == total:
            self.service_count_label.set_text(f"{count} servis")
        else:
            self.service_count_label.set_text(f"{count}/{total} servis")

    def _apply_filters(self):
        self.liststore.clear()
        query = self._search_text.lower()

        for d in self._all_data:
            if query and query not in d["name"].lower():
                continue
            if not self._matches_filter(d["active"], d["sub"]):
                continue
            markup = make_status_markup(d["active"])
            self.liststore.append([
                d["name"],
                markup,
                d["sub"],
                d["time_str"],
                d["desc"],
                d["tip"],
                d["oneri"],
                "",
            ])

        self._update_count_label()

    def _matches_filter(self, active_state, sub_state):
        f = self._current_filter
        if f == "all":
            return True
        if f == "active":
            return active_state == "active"
        if f == "inactive":
            return active_state == "inactive"
        if f == "disabled":
            return sub_state == "disabled" or active_state == "disabled"
        if f == "masked":
            return sub_state == "masked"
        return True

    def _get_color(self, status):
        return STATUS_COLORS.get(status, "#000000")

    def _on_filter_toggled(self, button, state):
        if not button.get_active():
            return
        self._current_filter = state
        self._apply_filters()

    def _on_search_changed(self, *args):
        self._search_text = self.search_entry.get_text()
        if self._debounce_id:
            GLib.source_remove(self._debounce_id)
        self._debounce_id = GLib.timeout_add(250, self._apply_filters)

    def _get_selected_row(self):
        model, treeiter = self.selection.get_selected()
        if treeiter is not None:
            return model[treeiter]
        return None

    def _get_selected_name(self):
        row = self._get_selected_row()
        if row is not None:
            return row[0]
        return None

    def _on_selection_changed(self, *args):
        row = self._get_selected_row()
        if row is None:
            self.detail_name.set_text("Servis secilmedi")
            self.detail_desc.set_text("Detaylar icin bir servis secin.")
            self.detail_suggestion.set_text("")
            return

        name = row[0]
        d = self._all_data_map.get(name)
        active = d["active"] if d else ""
        color = self._get_color(active)

        self.detail_name.set_markup(
            f"<b>{name}</b>  \u2014  <span foreground='{color}'>{active}</span>"
        )
        self.detail_desc.set_text(row[4])

        tip = row[5]
        oneri = row[6]
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

    def _run_systemctl(self, action, name, on_success):
        buf = self.log_textview.get_buffer()
        buf.set_text(f"{action} islemi baslatildi...\nYetki girisi gerekebilir.")

        def _task():
            try:
                if action == "enable":
                    ok, msg = self.manager.enable_service(name)
                elif action == "disable":
                    ok, msg = self.manager.disable_service(name)
                elif action == "mask":
                    ok, msg = self.manager.mask_service(name)
                elif action == "unmask":
                    ok, msg = self.manager.unmask_service(name)
                else:
                    ok, msg = False, f"Bilinmeyen islem: {action}"

                GLib.idle_add(self._on_command_done, ok, msg, on_success)
            except Exception as e:
                GLib.idle_add(self._on_command_done, False, str(e), on_success)

        threading.Thread(target=_task, daemon=True).start()

    def _on_command_done(self, ok, msg, on_success):
        self.log_textview.get_buffer().set_text(msg)
        if ok and on_success:
            on_success()

    def _on_enable(self, *args):
        name = self._get_selected_name()
        if not name:
            self.log_textview.get_buffer().set_text("Lutfen bir servis secin.")
            return
        self._run_systemctl("enable", name, self.load_all)

    def _on_disable(self, *args):
        name = self._get_selected_name()
        if not name:
            self.log_textview.get_buffer().set_text("Lutfen bir servis secin.")
            return
        self._run_systemctl("disable", name, self.load_all)

    def _on_mask(self, *args):
        name = self._get_selected_name()
        if not name:
            self.log_textview.get_buffer().set_text("Lutfen bir servis secin.")
            return

        d = self._all_data_map.get(name)
        tip = d["tip"] if d else ""

        warning = ("\n\nBu servis sistem icin KRITIK olarak isaretlenmistir. "
                   "Kapatmaniz sorunlara yol acabilir!") if tip == "kritik" else ""

        dialog = Gtk.MessageDialog(
            parent=self.main_window,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.WARNING if tip == "kritik" else Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            message_format=f"'{name}' servisini maskelemek istediginize emin misiniz?"
        )
        if warning:
            dialog.format_secondary_text(warning)
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self._run_systemctl("mask", name, self.load_all)

    def _on_unmask(self, *args):
        name = self._get_selected_name()
        if not name:
            self.log_textview.get_buffer().set_text("Lutfen bir servis secin.")
            return
        self._run_systemctl("unmask", name, self.load_all)

    def _on_show_log(self, *args):
        name = self._get_selected_name()
        if not name:
            self.log_textview.get_buffer().set_text("Lutfen bir servis secin.")
            return

        self.log_textview.get_buffer().set_text("Log yukleniyor...")

        def _task():
            try:
                log = self.manager.get_journal_log(name)
                GLib.idle_add(self.log_textview.get_buffer().set_text, log or "Log bulunamadi.")
            except Exception as e:
                GLib.idle_add(self.log_textview.get_buffer().set_text, f"Hata: {e}")

        threading.Thread(target=_task, daemon=True).start()
