import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import threading
import re
import os
import json
import cairo
import datetime
from src.system_manager import SystemManager
from src.service_db import get_description

STATUS_COLORS = {
    "active": "#198754",      # Green
    "inactive": "#dc3545",    # Red
    "disabled": "#6f42c1",    # Purple
    "masked": "#795548",      # Brown
    "static": "#0d6efd",      # Blue
    "activating": "#fd7e14",  # Orange
    "deactivating": "#fd7e14",
}

STATUS_TR = {
    "active": "Aktif / Çalışıyor",
    "inactive": "Pasif / Durmuş",
    "disabled": "Devre Dışı",
    "masked": "Maskeli",
    "static": "Statik",
    "activating": "Etkinleşiyor...",
    "deactivating": "Devre Dışı Bırakılıyor...",
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
    1: "other",
    2: "devices",
}

SAFE_TO_DISABLE_ONERI_SERVICES = {
    "NetworkManager-wait-online.service",
    "bluetooth.service",
    "cups.service",
    "cups-browsed.service",
    "avahi-daemon.service",
    "ModemManager.service",
    "colord.service",
    "lm-sensors.service",
    "smartmontools.service"
}

PROFILE_SERVICE_LABELS = {
    "cups.service": "Yazıcı Servisi (CUPS)",
    "bluetooth.service": "Bluetooth Desteği",
    "docker.service": "Docker Konteyner",
    "postgresql.service": "PostgreSQL Servisi",
    "ssh.service": "SSH Uzaktan Erişim",
}

def parse_blame_time(time_str):
    if not time_str:
        return 0
    time_str = time_str.strip()
    if "min" in time_str:
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
    color = STATUS_COLORS.get(status, "#6c757d")
    return f'<span foreground="{color}">\u25cf</span> <b>{tr}</b>'

def _is_dark_theme():
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

# --- Add Autostart Application Dialog ---
class AddAutostartDialog(Gtk.Dialog):
    def __init__(self, parent, manager):
        super().__init__(title="Başlangıç Uygulaması Ekle", parent=parent, flags=Gtk.DialogFlags.MODAL)
        self.set_default_size(520, 420)
        self.manager = manager
        
        self.add_button("İptal", Gtk.ResponseType.CANCEL)
        self.btn_ok = self.add_button("Ekle", Gtk.ResponseType.OK)
        self.btn_ok.get_style_context().add_class("primary")
        
        content = self.get_content_area()
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        
        notebook = Gtk.Notebook()
        content.pack_start(notebook, True, True, 0)
        
        # Tab 1: Installed Apps
        tab1_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        search_entry = Gtk.SearchEntry(placeholder_text="Uygulama ara...")
        tab1_box.pack_start(search_entry, False, False, 0)
        
        scrolled = Gtk.ScrolledWindow()
        tab1_box.pack_start(scrolled, True, True, 0)
        
        self.apps_liststore = Gtk.ListStore(str, str, str, object)
        
        self.apps_treeview = Gtk.TreeView()
        scrolled.add(self.apps_treeview)
        
        col_icon = Gtk.TreeViewColumn("")
        renderer_icon = Gtk.CellRendererPixbuf()
        col_icon.pack_start(renderer_icon, False)
        col_icon.add_attribute(renderer_icon, "icon_name", 2)
        self.apps_treeview.append_column(col_icon)
        
        col_name = Gtk.TreeViewColumn("Uygulama Adı")
        renderer_name = Gtk.CellRendererText()
        col_name.pack_start(renderer_name, True)
        col_name.add_attribute(renderer_name, "text", 0)
        self.apps_treeview.append_column(col_name)
        
        self.filter_model = self.apps_liststore.filter_new()
        self.filter_model.set_visible_func(self._visible_filter)
        self.apps_treeview.set_model(self.filter_model)
        
        self.search_text = ""
        search_entry.connect("changed", self._on_search_changed)
        
        self.apps = self.manager.get_installed_applications()
        for app in self.apps:
            self.apps_liststore.append([app["name"], app["exec"], app["icon"] or "system-run", app])
            
        notebook.append_page(tab1_box, Gtk.Label(label="Masaüstü Uygulamaları"))
        
        # Tab 2: Custom Command
        tab2_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tab2_box.set_margin_top(12)
        
        grid = Gtk.Grid(column_spacing=12, row_spacing=12)
        tab2_box.pack_start(grid, False, False, 0)
        
        lbl_name = Gtk.Label(label="Uygulama Adı:", xalign=1)
        self.entry_name = Gtk.Entry()
        grid.attach(lbl_name, 0, 0, 1, 1)
        grid.attach(self.entry_name, 1, 0, 1, 1)
        
        lbl_exec = Gtk.Label(label="Komut (Exec):", xalign=1)
        self.entry_exec = Gtk.Entry()
        grid.attach(lbl_exec, 0, 1, 1, 1)
        grid.attach(self.entry_exec, 1, 1, 1, 1)
        
        lbl_comment = Gtk.Label(label="Açıklama:", xalign=1)
        self.entry_comment = Gtk.Entry()
        grid.attach(lbl_comment, 0, 2, 1, 1)
        grid.attach(self.entry_comment, 1, 2, 1, 1)
        
        lbl_delay = Gtk.Label(label="Gecikme (Saniye):", xalign=1)
        self.spin_delay = Gtk.SpinButton.new_with_range(0, 120, 1)
        grid.attach(lbl_delay, 0, 3, 1, 1)
        grid.attach(self.spin_delay, 1, 3, 1, 1)
        
        notebook.append_page(tab2_box, Gtk.Label(label="Özel Komut Ekle"))
        
        self.notebook = notebook
        self.show_all()

    def _visible_filter(self, model, iter, data):
        if not self.search_text:
            return True
        val = model[iter][0]
        return self.search_text.lower() in val.lower()

    def _on_search_changed(self, entry):
        self.search_text = entry.get_text()
        self.filter_model.refilter()

    def get_result(self):
        page = self.notebook.get_current_page()
        if page == 0:
            sel = self.apps_treeview.get_selection()
            model, iter = sel.get_selected()
            if iter:
                app = model[iter][3]
                return {
                    "name": app["name"],
                    "exec": app["exec"],
                    "comment": app["comment"],
                    "icon": app["icon"],
                    "delay": 0
                }
        else:
            name = self.entry_name.get_text().strip()
            exec_cmd = self.entry_exec.get_text().strip()
            comment = self.entry_comment.get_text().strip()
            delay = int(self.spin_delay.get_value())
            if name and exec_cmd:
                return {
                    "name": name,
                    "exec": exec_cmd,
                    "comment": comment,
                    "icon": "system-run",
                    "delay": delay
                }
        return None


class PasswordDialog(Gtk.Dialog):
    def __init__(self, parent, manager):
        super().__init__(title="Yönetici Yetkilendirmesi", parent=parent, flags=Gtk.DialogFlags.MODAL)
        self.set_default_size(360, 200)
        self.manager = manager
        self.success = False
        self.entered_password = None
        
        self.get_style_context().add_class("auth-dialog")
        
        # Vazgeç button closes dialog with CANCEL response
        self.btn_cancel = self.add_button("Vazgeç", Gtk.ResponseType.CANCEL)
        
        # Yetkilendir button triggers click handler directly (doesn't auto-close)
        self.btn_auth = Gtk.Button(label="Yetkilendir")
        self.btn_auth.get_style_context().add_class("primary")
        self.btn_auth.connect("clicked", self._on_auth_clicked)
        self.get_action_area().pack_end(self.btn_auth, False, False, 0)
        
        content = self.get_content_area()
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.pack_start(vbox, True, True, 0)
        
        lbl_head = Gtk.Label(xalign=0)
        lbl_head.set_text("Yönetici Yetkisi Gerekiyor")
        lbl_head.get_style_context().add_class("auth-head")
        vbox.pack_start(lbl_head, False, False, 0)
        
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_text("Sistem hizmetlerini yönetmek için yönetici (sudo) şifrenizi girin.")
        lbl_sub.get_style_context().add_class("auth-sub")
        lbl_sub.set_line_wrap(True)
        vbox.pack_start(lbl_sub, False, False, 0)
        
        h_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(h_row, False, False, 0)
        
        self.entry_pwd = Gtk.Entry()
        self.entry_pwd.set_visibility(False)
        self.entry_pwd.set_placeholder_text("Yönetici şifresi")
        self.entry_pwd.connect("activate", lambda e: self._on_auth_clicked(None))
        h_row.pack_start(self.entry_pwd, True, True, 0)
        
        self.chk_show = Gtk.CheckButton(label="Şifreyi Göster")
        self.chk_show.connect("toggled", self._on_show_toggled)
        vbox.pack_start(self.chk_show, False, False, 0)
        
        self.lbl_error = Gtk.Label(xalign=0)
        self.lbl_error.get_style_context().add_class("error-text")
        vbox.pack_start(self.lbl_error, False, False, 0)
        
        self.show_all()

    def _on_show_toggled(self, widget):
        self.entry_pwd.set_visibility(widget.get_active())

    def _on_auth_clicked(self, button):
        pwd = self.entry_pwd.get_text()
        self.lbl_error.set_text("")
        
        self.set_sensitive(False)
        while Gtk.events_pending():
            Gtk.main_iteration()
            
        valid = self.manager.verify_sudo_password(pwd)
        self.set_sensitive(True)
        
        if valid:
            self.success = True
            self.entered_password = pwd
            self.response(Gtk.ResponseType.OK)
        else:
            self.lbl_error.set_markup("<span foreground='#dc3545'>Hatalı şifre! Lütfen tekrar deneyin.</span>")


class Controller:
    def __init__(self, window):
        self.window = window
        self.manager = SystemManager()

        self._all_data = []
        self._all_data_map = {}
        self._status_filter = "all"
        self._tip_filter = "all"
        self._search_text = ""
        self._debounce_id = 0
        self._updating_widgets = False

        self._load_css()
        self._build_ui()
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
        self.status_label.set_tooltip_text(text)

    def _ensure_auth(self):
        if self.manager.password is not None:
            return True
            
        dlg = PasswordDialog(self.window, self.manager)
        dlg.run()
        success = dlg.success
        pwd = dlg.entered_password
        dlg.hide()
        GLib.idle_add(dlg.destroy)
        
        if success and pwd is not None:
            self.manager.password = pwd
            return True
        return False

    def _format_time(self, time_str):
        if not time_str:
            return "--"
        match = re.match(r"([\d.]+)\s*([a-zA-Z]+)", time_str.strip())
        if match:
            try:
                val = float(match.group(1))
                unit = match.group(2)
                if unit == "s":
                    return f"{val:.1f}s"
                elif unit == "ms":
                    return f"{int(val)}ms"
                return f"{val:.1f}{unit}"
            except ValueError:
                pass
        return time_str

    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.window.add(main_box)

        # 1. Left Sidebar
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        sidebar_box.set_size_request(240, -1)
        sidebar_box.get_style_context().add_class("sidebar")
        main_box.pack_start(sidebar_box, False, False, 0)

        vbox_logo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        vbox_logo.set_margin_start(12)
        vbox_logo.set_margin_top(8)
        
        lbl_p = Gtk.Label(xalign=0)
        lbl_p.set_text("Pardus")
        lbl_p.get_style_context().add_class("sidebar-title")
        vbox_logo.pack_start(lbl_p, False, False, 0)
        
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_text("Başlangıç Yöneticisi")
        lbl_sub.get_style_context().add_class("sidebar-subtitle")
        vbox_logo.pack_start(lbl_sub, False, False, 0)
        
        sidebar_box.pack_start(vbox_logo, False, False, 0)

        self.sidebar_listbox = Gtk.ListBox()
        self.sidebar_listbox.get_style_context().add_class("sidebar-list")
        self.sidebar_listbox.connect("row-selected", self._on_sidebar_row_selected)
        sidebar_box.pack_start(self.sidebar_listbox, False, False, 0)

        items = [
            ("📊  Başlangıç Analizi", "analiz"),
            ("🚀  Otomatik Uygulamalar", "autostart"),
            ("⚙️  Sistem Hizmetleri", "hizmetler"),
            ("👤  Hizmet Profilleri", "profiller")
        ]
        
        for text, name in items:
            row = Gtk.ListBoxRow()
            row.get_style_context().add_class("sidebar-row")
            
            box_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            lbl = Gtk.Label(xalign=0)
            lbl.get_style_context().add_class("sidebar-item-label")
            lbl.set_text(text)
            
            box_row.pack_start(lbl, True, True, 0)
            row.add(box_row)
            self.sidebar_listbox.add(row)

        spacer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.pack_start(spacer, True, True, 0)

        self.status_label = Gtk.Label(xalign=0)
        self.status_label.get_style_context().add_class("status-label")
        self.status_label.set_margin_start(12)
        self.status_label.set_margin_end(12)
        self.status_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.status_label.set_max_width_chars(25)
        sidebar_box.pack_start(self.status_label, False, False, 8)

        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        main_box.pack_start(sep, False, False, 0)

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.content_box.set_margin_start(20)
        self.content_box.set_margin_end(20)
        self.content_box.set_margin_top(18)
        self.content_box.set_margin_bottom(18)
        main_box.pack_start(self.content_box, True, True, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(200)
        self.content_box.pack_start(self.stack, True, True, 0)

        self.stack.add_named(self.build_page_analiz(), "analiz")
        self.stack.add_named(self.build_page_autostart(), "autostart")
        self.stack.add_named(self.build_page_hizmetler(), "hizmetler")
        self.stack.add_named(self.build_page_profiller(), "profiller")

        self.sidebar_listbox.select_row(self.sidebar_listbox.get_row_at_index(0))

    # --- Page 1: Analiz (Dashboard) ---
    def build_page_analiz(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        lbl_title = Gtk.Label(xalign=0)
        lbl_title.set_text("Sistem Başlangıç Analizi")
        lbl_title.get_style_context().add_class("content-title")
        box.pack_start(lbl_title, False, False, 0)
        
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_text("Sisteminizin açılış süresini ve kapatılması güvenli olan önerilen hizmetleri yönetin.")
        lbl_sub.get_style_context().add_class("content-subtitle")
        box.pack_start(lbl_sub, False, False, 0)
        
        h_split = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        box.pack_start(h_split, True, True, 0)
        
        vbox_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox_left.set_size_request(340, -1)
        h_split.pack_start(vbox_left, False, False, 0)
        
        # Left Card 1 - Boot Time
        self.card_boot = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.card_boot.get_style_context().add_class("card")
        vbox_left.pack_start(self.card_boot, False, False, 0)
        
        lbl_boot_title = Gtk.Label(xalign=0)
        lbl_boot_title.set_text("Açılış Süresi Özeti")
        lbl_boot_title.get_style_context().add_class("card-title")
        self.card_boot.pack_start(lbl_boot_title, False, False, 0)
        
        vbox_circle = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_circle.get_style_context().add_class("boot-circle-container")
        vbox_circle.set_valign(Gtk.Align.CENTER)
        vbox_circle.set_halign(Gtk.Align.CENTER)
        
        vbox_inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox_inner.set_valign(Gtk.Align.CENTER)
        vbox_inner.set_halign(Gtk.Align.CENTER)
        vbox_circle.pack_start(vbox_inner, True, False, 0)
        
        self.lbl_boot_val = Gtk.Label()
        self.lbl_boot_val.get_style_context().add_class("boot-time-value")
        self.lbl_boot_val.set_text("--")
        self.lbl_boot_val.set_justify(Gtk.Justification.CENTER)
        vbox_inner.pack_start(self.lbl_boot_val, False, False, 0)
        
        lbl_circle_sub = Gtk.Label()
        lbl_circle_sub.get_style_context().add_class("boot-time-label")
        lbl_circle_sub.set_text("Toplam Açılış Süresi")
        lbl_circle_sub.set_justify(Gtk.Justification.CENTER)
        vbox_inner.pack_start(lbl_circle_sub, False, False, 0)
        
        self.card_boot.pack_start(vbox_circle, False, False, 8)
        
        self.breakdown_grid = Gtk.Grid(column_spacing=18, row_spacing=6)
        self.breakdown_grid.set_halign(Gtk.Align.CENTER)
        self.card_boot.pack_start(self.breakdown_grid, False, False, 4)
        
        # Left Card 2 - System Info & PDF Report
        self.card_sysinfo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.card_sysinfo.get_style_context().add_class("card")
        vbox_left.pack_start(self.card_sysinfo, False, False, 0)
        
        lbl_sys_title = Gtk.Label(xalign=0)
        lbl_sys_title.set_text("Sistem Bilgileri")
        lbl_sys_title.get_style_context().add_class("card-title")
        self.card_sysinfo.pack_start(lbl_sys_title, False, False, 0)
        
        self.sysinfo_grid = Gtk.Grid(column_spacing=12, row_spacing=6)
        self.sysinfo_grid.set_margin_start(6)
        self.card_sysinfo.pack_start(self.sysinfo_grid, False, False, 4)
        
        self.btn_pdf = Gtk.Button(label="PDF Raporu Oluştur")
        self.btn_pdf.get_style_context().add_class("primary")
        self.btn_pdf.connect("clicked", self._on_pdf_clicked)
        self.card_sysinfo.pack_start(self.btn_pdf, False, False, 4)
        
        # Right Card - Quick Optimization
        self.card_optimize = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.card_optimize.get_style_context().add_class("card")
        h_split.pack_start(self.card_optimize, True, True, 0)
        
        lbl_opt_title = Gtk.Label(xalign=0)
        lbl_opt_title.set_text("Başlangıç Optimizasyonu")
        lbl_opt_title.get_style_context().add_class("card-title")
        self.card_optimize.pack_start(lbl_opt_title, False, False, 0)
        
        lbl_opt_desc = Gtk.Label(xalign=0)
        lbl_opt_desc.set_markup("<span size='small' foreground='#565f89'>Açılışı geciktiren ve kapatılması güvenli olan hizmetleri tek tıkla kapatarak hız kazanın.</span>")
        lbl_opt_desc.set_line_wrap(True)
        self.card_optimize.pack_start(lbl_opt_desc, False, False, 0)
        
        self.opt_savings_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.opt_savings_box.set_margin_top(4)
        self.opt_savings_box.set_margin_bottom(4)
        self.card_optimize.pack_start(self.opt_savings_box, False, False, 0)
        
        self.lbl_savings_val = Gtk.Label(xalign=0)
        self.lbl_savings_val.set_markup("Hızlandırma Potansiyeli: <b>-- saniye</b>")
        self.opt_savings_box.pack_start(self.lbl_savings_val, True, True, 0)
        
        self.btn_quick_optimize = Gtk.Button(label="Tüm Önerilenleri Kapat")
        self.btn_quick_optimize.get_style_context().add_class("success")
        self.btn_quick_optimize.connect("clicked", self._on_quick_optimize_clicked)
        self.card_optimize.pack_start(self.btn_quick_optimize, False, False, 4)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.card_optimize.pack_start(scrolled, True, True, 0)
        
        self.opt_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scrolled.add(self.opt_list_box)
        
        box.show_all()
        return box

    def load_analysis_page(self):
        for child in self.breakdown_grid.get_children():
            self.breakdown_grid.remove(child)
            
        for child in self.sysinfo_grid.get_children():
            self.sysinfo_grid.remove(child)
            
        for child in self.opt_list_box.get_children():
            self.opt_list_box.remove(child)
            
        try:
            total_time, full_text = self.manager.get_total_boot_time()
            self.lbl_boot_val.set_text(self._format_time(total_time))
            
            components = {
                "firmware": "Donanım (Firmware)",
                "loader": "Önyükleyici (Loader)",
                "kernel": "Çekirdek (Kernel)",
                "initrd": "Başlangıç Arayüzü (Initrd)",
                "userspace": "Kullanıcı Alanı (Userspace)"
            }
            
            row = 0
            for key, name in components.items():
                match = re.search(r"([\d.]+(?:s|ms|min))\s*\((Donanım|Önyükleyici|Çekirdek|Başlangıç Arayüzü|Kullanıcı Alanı|" + key + r")\)", full_text) or re.search(r"([\d.]+(?:s|ms|min))\s*\(" + key + r"\)", full_text)
                if match:
                    val = match.group(1)
                    
                    lbl_name = Gtk.Label(xalign=0)
                    lbl_name.set_markup(f"<b>{name}:</b>")
                    self.breakdown_grid.attach(lbl_name, 0, row, 1, 1)
                    
                    lbl_val = Gtk.Label(xalign=0, label=self._format_time(val))
                    self.breakdown_grid.attach(lbl_val, 1, row, 1, 1)
                    row += 1
            
            info = self.manager.get_system_info()
            sys_items = [
                ("Sistem:", info["os"]),
                ("Çekirdek:", info["kernel"]),
                ("Bellek:", info["ram"]),
                ("Çalışma:", info["uptime"])
            ]
            
            s_row = 0
            for label, value in sys_items:
                lbl_l = Gtk.Label(xalign=1)
                lbl_l.set_markup(f"<b>{label}</b>")
                self.sysinfo_grid.attach(lbl_l, 0, s_row, 1, 1)
                
                lbl_v = Gtk.Label(xalign=0, label=value)
                lbl_v.set_ellipsize(Pango.EllipsizeMode.END if hasattr(Pango, 'EllipsizeMode') else 3)
                self.sysinfo_grid.attach(lbl_v, 1, s_row, 1, 1)
                s_row += 1
                
            enabled_map = self.manager.get_unit_file_states()
            blame_list, _ = self.manager.get_blame_data()
            
            optimizable_services = []
            total_savings_sec = 0.0
            
            for item in blame_list:
                name = item["name"]
                time_str = item["time"]
                sec = parse_blame_time(time_str)
                
                enabled_state = enabled_map.get(name, "unknown")
                is_enabled = enabled_state in ("enabled", "enabled-runtime")
                
                if name in SAFE_TO_DISABLE_ONERI_SERVICES and is_enabled:
                    desc, tip, oneri = get_description(name)
                    optimizable_services.append({
                        "name": name,
                        "time_str": time_str,
                        "seconds": sec,
                        "oneri": oneri or desc or "Kapatılması önerilen gereksiz hizmet."
                    })
                    total_savings_sec += sec
            
            if total_savings_sec > 0:
                self.lbl_savings_val.set_markup(
                    f"Hızlandırma Potansiyeli: <span foreground='#198754' weight='bold'>~{total_savings_sec:.2f} saniye</span>"
                )
                self.btn_quick_optimize.set_label(f"Tüm Önerilenleri Kapat (+{total_savings_sec:.1f} sn Kazan)")
                self.btn_quick_optimize.set_sensitive(True)
            else:
                self.lbl_savings_val.set_markup("Hızlandırma Potansiyeli: <span color='#6c757d'><b>0.00 saniye</b></span>")
                self.btn_quick_optimize.set_label("Sisteminiz Zaten Optimize Edilmiş")
                self.btn_quick_optimize.set_sensitive(False)
                
            if optimizable_services:
                for item in optimizable_services:
                    name = item["name"]
                    time_str = item["time_str"]
                    oneri_text = item["oneri"]
                    
                    row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                    row_box.get_style_context().add_class("blame-row")
                    
                    vbox_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                    row_box.pack_start(vbox_info, True, True, 0)
                    
                    btn_go = Gtk.Button(label=name)
                    btn_go.set_relief(Gtk.ReliefStyle.NONE)
                    btn_go.set_halign(Gtk.Align.START)
                    btn_go.connect("clicked", lambda b, n=name: self._go_to_service(n))
                    vbox_info.pack_start(btn_go, False, False, 0)
                    
                    lbl_oneri = Gtk.Label(xalign=0)
                    lbl_oneri.set_markup(f"<span size='small' foreground='#888888'>{oneri_text}</span>")
                    lbl_oneri.set_line_wrap(True)
                    vbox_info.pack_start(lbl_oneri, False, False, 0)
                    
                    lbl_time = Gtk.Label(label=time_str)
                    lbl_time.get_style_context().add_class("badge-slow")
                    row_box.pack_start(lbl_time, False, False, 0)
                    
                    btn_disable_one = Gtk.Button()
                    img_dis = Gtk.Image.new_from_icon_name("media-playback-stop", Gtk.IconSize.BUTTON)
                    btn_disable_one.set_image(img_dis)
                    btn_disable_one.get_style_context().add_class("danger")
                    btn_disable_one.set_tooltip_text("Sadece bu hizmeti devre dışı bırak ve durdur")
                    btn_disable_one.connect("clicked", lambda b, n=name: self._disable_single_service(n))
                    row_box.pack_start(btn_disable_one, False, False, 0)
                    
                    self.opt_list_box.pack_start(row_box, False, False, 0)
            else:
                lbl_empty = Gtk.Label()
                lbl_empty.set_markup("<span foreground='#6c757d'>Kapatılması önerilen aktif bir hizmet bulunamadı. Sisteminiz en iyi durumda!</span>")
                lbl_empty.set_line_wrap(True)
                lbl_empty.set_margin_top(16)
                self.opt_list_box.pack_start(lbl_empty, False, False, 0)
                
        except Exception as e:
            self.lbl_boot_val.set_text("Hata")
            lbl = Gtk.Label(label=f"Analiz yüklenirken hata oluştu:\n{e}")
            self.opt_list_box.pack_start(lbl, False, False, 0)
            
        self.card_boot.show_all()
        self.card_sysinfo.show_all()
        self.opt_list_box.show_all()

    def _go_to_service(self, service_name):
        self.sidebar_listbox.select_row(self.sidebar_listbox.get_row_at_index(2))
        self.view_combo.set_active(0)
        self.filter_combo.set_active(0)
        self.tip_combo.set_active(0)
        self.search_entry.set_text("")
        
        def select_row():
            for i in range(len(self.liststore)):
                if self.liststore[i][0] == service_name:
                    self.selection.select_path(Gtk.TreePath(i))
                    self.treeview.scroll_to_cell(Gtk.TreePath(i), None, False, 0.5, 0.5)
                    break
            return False
            
        GLib.timeout_add(100, select_row)

    def _disable_single_service(self, name):
        dlg = Gtk.MessageDialog(
            parent=self.window, flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO,
            message_format=f"'{name}' hizmetini kapatmak istiyor musunuz?"
        )
        dlg.format_secondary_text("Bu işlem hizmeti devre dışı bırakacak (disable) ve durduracaktır (stop).")
        resp = dlg.run()
        dlg.destroy()
        
        if resp == Gtk.ResponseType.YES:
            if not self._ensure_auth():
                self.set_status("Yetkilendirme iptal edildi.")
                return
            self.set_status(f"'{name}' hizmeti kapatılıyor...")
            def task():
                ok1, msg1 = self.manager.disable_service(name)
                ok2, msg2 = self.manager.stop_service(name)
                GLib.idle_add(done, ok1 and ok2, f"'{name}' başarıyla kapatıldı." if ok1 and ok2 else f"Hata: {msg1} {msg2}")
                
            def done(ok, msg):
                self.set_status(msg)
                self.load_all()
                self.load_analysis_page()
                
            threading.Thread(target=task, daemon=True).start()

    def _on_quick_optimize_clicked(self, button):
        try:
            enabled_map = self.manager.get_unit_file_states()
            blame_list, _ = self.manager.get_blame_data()
        except Exception as e:
            self.set_status(f"Hata: {e}")
            return
            
        services_to_disable = []
        for item in blame_list:
            name = item["name"]
            if name in SAFE_TO_DISABLE_ONERI_SERVICES:
                enabled_state = enabled_map.get(name, "unknown")
                if enabled_state in ("enabled", "enabled-runtime"):
                    services_to_disable.append(name)
                    
        if not services_to_disable:
            self.set_status("Kapatılacak hizmet bulunamadı.")
            return
            
        dlg = Gtk.MessageDialog(
            parent=self.window, flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO,
            message_format="Önerilen Tüm Hizmetleri Kapatmak İstiyor musunuz?"
        )
        
        svc_list_str = "\n".join(f"- {s}" for s in services_to_disable)
        dlg.format_secondary_text(
            "Aşağıdaki gereksiz hizmetler devre dışı bırakılacak ve durdurulacaktır:\n\n"
            f"{svc_list_str}\n\n"
            "Bu işlem sisteminizin açılışını hızlandıracaktır. Yetkilendirme şifresi istenecektir."
        )
        
        resp = dlg.run()
        dlg.destroy()
        
        if resp != Gtk.ResponseType.YES:
            return
            
        if not self._ensure_auth():
            self.set_status("Yetkilendirme iptal edildi.")
            return
            
        self._run_quick_optimize_batch(services_to_disable)

    def _run_quick_optimize_batch(self, services_to_disable):
        loader = Gtk.Dialog(title="Sistem Optimize Ediliyor", parent=self.window, flags=Gtk.DialogFlags.MODAL)
        loader.set_default_size(320, 140)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(18)
        box.set_margin_end(18)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        loader.get_content_area().add(box)
        
        lbl = Gtk.Label(label="Önerilen hizmetler kapatılıyor, lütfen bekleyin...")
        box.pack_start(lbl, False, False, 0)
        
        spinner = Gtk.Spinner()
        box.pack_start(spinner, True, True, 0)
        spinner.start()
        
        loader.show_all()
        
        def task():
            self.manager.create_backup()
            ok, msg = self.manager.apply_profile_batch(enable_list=[], disable_list=services_to_disable)
            GLib.idle_add(done, ok, msg)
            
        def done(ok, msg):
            spinner.stop()
            loader.destroy()
            self.set_status(msg)
            if ok:
                info = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK,
                    message_format="Optimizasyon Tamamlandı!"
                )
                info.format_secondary_text("Önerilen tüm gereksiz hizmetler başarıyla kapatıldı.")
                info.run()
                info.destroy()
                self.load_all()
                self.load_analysis_page()
            else:
                err = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
                    message_format="Optimizasyon Sırasında Hata Oluştu",
                )
                err.format_secondary_text(msg)
                err.run()
                err.destroy()
                
        threading.Thread(target=task, daemon=True).start()

    # --- PDF Report Generation (Cairo) ---
    def _on_pdf_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="PDF Raporu Kaydet", parent=self.window,
            action=Gtk.FileChooserAction.SAVE,
            buttons=("İptal", Gtk.ResponseType.CANCEL, "Kaydet", Gtk.ResponseType.ACCEPT)
        )
        dialog.get_widget_for_response(Gtk.ResponseType.ACCEPT).get_style_context().add_class("primary")
        
        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("PDF Dosyaları")
        filter_pdf.add_mime_type("application/pdf")
        filter_pdf.add_pattern("*.pdf")
        dialog.add_filter(filter_pdf)
        
        dialog.set_current_name("Pardus_Baslangic_Raporu.pdf")
        
        resp = dialog.run()
        path = dialog.get_filename()
        dialog.destroy()
        
        if resp == Gtk.ResponseType.ACCEPT and path:
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            self.set_status("PDF Raporu oluşturuluyor...")
            
            def task():
                try:
                    print_op = Gtk.PrintOperation()
                    print_op.set_export_filename(path)
                    print_op.connect("draw-page", self._draw_pdf_page)
                    print_op.set_n_pages(1)
                    GLib.idle_add(run_print_op, print_op)
                except Exception as e:
                    GLib.idle_add(self.set_status, f"PDF Hatası: {e}")
                    
            def run_print_op(print_op):
                try:
                    result = print_op.run(Gtk.PrintOperationAction.EXPORT, self.window)
                    if result == Gtk.PrintOperationResult.APPLY:
                        self.set_status(f"PDF Raporu kaydedildi: {path}")
                        info = Gtk.MessageDialog(
                            parent=self.window, flags=Gtk.DialogFlags.MODAL,
                            type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK,
                            message_format="PDF Raporu Oluşturuldu!"
                        )
                        info.format_secondary_text(f"Sistem başlangıç raporunuz başarıyla kaydedildi:\n\n{path}")
                        info.run()
                        info.destroy()
                    else:
                        self.set_status("PDF oluşturma işlemi tamamlanamadı.")
                except Exception as e:
                    self.set_status(f"PDF Hatası: {e}")
                    
            threading.Thread(target=task, daemon=True).start()

    def _draw_pdf_page(self, operation, context, page_nr):
        cr = context.get_cairo_context()
        
        cr.set_source_rgb(0.05, 0.5, 0.7)
        cr.rectangle(50, 50, 495, 45)
        cr.fill()
        
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(14)
        cr.move_to(70, 78)
        cr.show_text("PARDUS BAŞLANGIÇ YÖNETİCİSİ — ANALİZ RAPORU")
        
        date_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        cr.set_font_size(9)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.move_to(430, 75)
        cr.show_text(date_str)
        
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        cr.move_to(50, 125)
        cr.show_text("1. Sistem Özeti")
        
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.set_line_width(1)
        cr.move_to(50, 132)
        cr.line_to(545, 132)
        cr.stroke()
        
        info = self.manager.get_system_info()
        total_time, full_text = self.manager.get_total_boot_time()
        
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(10)
        
        y = 150
        cr.move_to(60, y); cr.show_text(f"İşletim Sistemi: {info['os']}")
        cr.move_to(300, y); cr.show_text(f"Çekirdek (Kernel): {info['kernel']}")
        
        y = 170
        cr.move_to(60, y); cr.show_text(f"Bellek (RAM): {info['ram']}")
        cr.move_to(300, y); cr.show_text(f"Çalısma Süresi: {info['uptime']}")
        
        y = 190
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.move_to(60, y); cr.show_text(f"Toplam Açılış Süresi: {total_time}")
        
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        cr.move_to(50, 230)
        cr.show_text("2. Açılış Aşamaları Dağılımı")
        
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.move_to(50, 237)
        cr.line_to(545, 237)
        cr.stroke()
        
        components = {
            "firmware": "Donanım (Firmware)",
            "loader": "Önyükleyici (Loader)",
            "kernel": "Çekirdek (Kernel)",
            "initrd": "Başlangıç Arayüzü (Initrd)",
            "userspace": "Kullanıcı Alanı (Userspace)"
        }
        
        y = 255
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(10)
        
        for key, name in components.items():
            match = re.search(r"([\d.]+(?:s|ms|min))\s*\((Donanım|Önyükleyici|Çekirdek|Başlangıç Arayüzü|Kullanıcı Alanı|" + key + r")\)", full_text) or re.search(r"([\d.]+(?:s|ms|min))\s*\(" + key + r"\)", full_text)
            if match:
                val = match.group(1)
                cr.move_to(70, y); cr.show_text(f"•  {name}:")
                cr.move_to(250, y); cr.show_text(val)
                y += 18
                
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        cr.move_to(50, y + 15)
        cr.show_text("3. En Yavaş Başlayan 5 Hizmet")
        
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.move_to(50, y + 22)
        cr.line_to(545, y + 22)
        cr.stroke()
        
        enabled_map = self.manager.get_unit_file_states()
        blame_list, _ = self.manager.get_blame_data()
        
        y += 38
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(10)
        
        for item in blame_list[:5]:
            cr.move_to(70, y); cr.show_text(f"•  {item['name']}:")
            cr.move_to(350, y); cr.show_text(item['time'])
            y += 16
            
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        cr.move_to(50, y + 15)
        cr.show_text("4. Başlangıç Optimizasyonu Önerileri")
        
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.move_to(50, y + 22)
        cr.line_to(545, y + 22)
        cr.stroke()
        
        optimizable_services = []
        total_savings_sec = 0.0
        
        for item in blame_list:
            name = item["name"]
            if name in SAFE_TO_DISABLE_ONERI_SERVICES:
                enabled_state = enabled_map.get(name, "unknown")
                if enabled_state in ("enabled", "enabled-runtime"):
                    sec = parse_blame_time(item["time"])
                    desc, tip, oneri = get_description(name)
                    optimizable_services.append({
                        "name": name,
                        "time_str": item["time"],
                        "oneri": oneri or desc or "Kapatılması önerilen gereksiz hizmet."
                    })
                    total_savings_sec += sec
                    
        y += 40
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(10)
        
        if total_savings_sec > 0:
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_source_rgb(0.1, 0.5, 0.3)
            cr.move_to(60, y)
            cr.show_text(f"Hızlandırma Potansiyeli: ~{total_savings_sec:.2f} saniye kazanılabilir!")
            cr.set_source_rgb(0.3, 0.3, 0.3)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            
            y += 20
            for item in optimizable_services[:4]:
                cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                cr.move_to(70, y); cr.show_text(f"- {item['name']} ({item['time_str']})")
                cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                y += 15
                cr.move_to(85, y); cr.show_text(item['oneri'])
                y += 20
        else:
            cr.move_to(60, y)
            cr.show_text("Aktif olarak kapatılması önerilen gereksiz hizmet bulunamadı. Sisteminiz en iyi durumda!")
            y += 20
            
        cr.set_source_rgb(0.6, 0.6, 0.6)
        cr.set_font_size(8)
        cr.move_to(50, 780)
        cr.line_to(545, 780)
        cr.stroke()
        cr.move_to(50, 792)
        cr.show_text("Pardus Başlangıç Yöneticisi — Pardus Ekosistemine Katkı Raporu")
        cr.move_to(480, 792)
        cr.show_text("Sayfa 1 / 1")

    # --- Page 2: Autostart ---
    def build_page_autostart(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        h_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(h_title, False, False, 0)
        
        lbl_title = Gtk.Label(xalign=0)
        lbl_title.set_text("Başlangıç Uygulamaları")
        lbl_title.get_style_context().add_class("content-title")
        h_title.pack_start(lbl_title, True, True, 0)
        
        btn_add = Gtk.Button(label="+ Uygulama Ekle")
        btn_add.get_style_context().add_class("primary")
        btn_add.connect("clicked", self._on_add_autostart_clicked)
        h_title.pack_start(btn_add, False, False, 0)
        
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_text("Kullanıcı oturumu başladığında otomatik olarak çalışacak uygulamaları yönetin.")
        lbl_sub.get_style_context().add_class("content-subtitle")
        box.pack_start(lbl_sub, False, False, 0)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box.pack_start(scrolled, True, True, 0)
        
        self.autostart_listbox = Gtk.ListBox()
        self.autostart_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.autostart_listbox)
        
        box.show_all()
        return box

    def load_autostart_page(self):
        for child in self.autostart_listbox.get_children():
            self.autostart_listbox.remove(child)
            
        entries = self.manager.get_autostart_entries()
        if not entries:
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label()
            lbl.set_markup("<span foreground='#888888'>Otomatik başlatılan uygulama bulunamadı.</span>")
            lbl.set_margin_top(24)
            lbl.set_margin_bottom(24)
            row.add(lbl)
            self.autostart_listbox.add(row)
        else:
            for entry in entries:
                row = Gtk.ListBoxRow()
                row.get_style_context().add_class("autostart-row")
                
                h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                row.add(h_box)
                
                img = Gtk.Image.new_from_icon_name(entry["icon"], Gtk.IconSize.LARGE_TOOLBAR)
                img.set_pixel_size(32)
                h_box.pack_start(img, False, False, 0)
                
                v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                lbl_name = Gtk.Label(xalign=0)
                lbl_name.set_markup(f"<b>{entry['name']}</b>")
                v_box.pack_start(lbl_name, False, False, 0)
                
                lbl_cmd = Gtk.Label(xalign=0)
                lbl_cmd.set_markup(f"<span size='small' foreground='#666666'>{entry['exec']}</span>")
                lbl_cmd.set_ellipsize(Pango.EllipsizeMode.END if hasattr(Pango, 'EllipsizeMode') else 3)
                v_box.pack_start(lbl_cmd, False, False, 0)
                
                h_box.pack_start(v_box, True, True, 0)
                
                lbl_delay = Gtk.Label(label="Gecikme:")
                h_box.pack_start(lbl_delay, False, False, 6)
                
                spin = Gtk.SpinButton.new_with_range(0, 120, 1)
                spin.set_value(entry["delay"])
                spin.connect("value-changed", self._on_autostart_delay_changed, entry["filepath"])
                h_box.pack_start(spin, False, False, 0)
                
                switch = Gtk.Switch()
                switch.set_active(entry["enabled"])
                switch.connect("state-set", self._on_autostart_toggle, entry["filepath"])
                h_box.pack_start(switch, False, False, 12)
                
                btn_delete = Gtk.Button()
                img_del = Gtk.Image.new_from_icon_name("user-trash", Gtk.IconSize.BUTTON)
                btn_delete.set_image(img_del)
                btn_delete.get_style_context().add_class("danger")
                btn_delete.connect("clicked", self._on_autostart_delete_clicked, entry["filepath"])
                h_box.pack_start(btn_delete, False, False, 0)
                
                self.autostart_listbox.add(row)
                
        self.autostart_listbox.show_all()

    def _on_autostart_delay_changed(self, spin, filepath):
        delay = int(spin.get_value())
        self.manager.update_autostart_delay(filepath, delay)
        self.set_status("Gecikme süresi güncellendi.")

    def _on_autostart_toggle(self, switch, state, filepath):
        self.manager.toggle_autostart_entry(filepath, state)
        self.set_status("Uygulama aktiflik durumu güncellendi.")
        return False

    def _on_autostart_delete_clicked(self, button, filepath):
        self.manager.remove_autostart_entry(filepath)
        self.load_autostart_page()
        self.set_status("Uygulama listeden kaldırıldı.")

    def _on_add_autostart_clicked(self, button):
        dlg = AddAutostartDialog(self.window, self.manager)
        resp = dlg.run()
        res = dlg.get_result()
        dlg.destroy()
        
        if resp == Gtk.ResponseType.OK and res:
            self.manager.add_autostart_entry(
                name=res["name"],
                command=res["exec"],
                comment=res["comment"],
                icon=res["icon"],
                delay=res["delay"]
            )
            self.set_status(f"'{res['name']}' başlangıç uygulamalarına eklendi.")
            self.load_autostart_page()

    # --- Page 3: Hizmetler ---
    def build_page_hizmetler(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        lbl_title = Gtk.Label(xalign=0)
        lbl_title.set_text("Sistem Hizmetleri")
        lbl_title.get_style_context().add_class("content-title")
        box.pack_start(lbl_title, False, False, 0)
        
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_text("Sistem servislerini ve donanım birimlerini yönetin, etkinleştirin veya devre dışı bırakın.")
        lbl_sub.get_style_context().add_class("content-subtitle")
        box.pack_start(lbl_sub, False, False, 0)
        
        f_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.pack_start(f_box, False, False, 0)
        
        self.view_combo = Gtk.ComboBoxText()
        self.view_combo.append_text("Servisler (.service)")
        self.view_combo.append_text("Diğerleri (Socket, Target, Mount)")
        self.view_combo.append_text("Aygıt Birimleri (.device)")
        self.view_combo.set_active(0)
        f_box.pack_start(self.view_combo, False, False, 0)
        
        self.filter_combo = Gtk.ComboBoxText()
        self.filter_combo.append_text("Tüm Durumlar")
        self.filter_combo.append_text("Aktif")
        self.filter_combo.append_text("Pasif")
        self.filter_combo.append_text("Devre Dışı")
        self.filter_combo.append_text("Maskeli")
        self.filter_combo.set_active(0)
        f_box.pack_start(self.filter_combo, False, False, 0)
        
        self.tip_combo = Gtk.ComboBoxText()
        self.tip_combo.append_text("Tüm Kategoriler")
        self.tip_combo.append_text("Kapatılmamalı")
        self.tip_combo.append_text("Kapatılabilir")
        self.tip_combo.append_text("Gerekli")
        self.tip_combo.set_active(0)
        f_box.pack_start(self.tip_combo, False, False, 0)
        
        self.search_entry = Gtk.SearchEntry(placeholder_text="Ara...")
        f_box.pack_start(self.search_entry, True, True, 0)
        
        self.service_count_label = Gtk.Label(label="0 servis")
        self.service_count_label.get_style_context().add_class("badge-slow")
        f_box.pack_start(self.service_count_label, False, False, 4)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        box.pack_start(scrolled, True, True, 0)
        
        self.liststore = Gtk.ListStore(str, str, str, str, str, str, str, str)
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.set_rules_hint(True)
        scrolled.add(self.treeview)
        
        col_name = Gtk.TreeViewColumn("Servis Adı")
        col_name.set_resizable(True)
        col_name.set_expand(True)
        col_name.set_min_width(200)
        renderer_name = Gtk.CellRendererText()
        col_name.pack_start(renderer_name, True)
        col_name.add_attribute(renderer_name, "text", 0)
        self.treeview.append_column(col_name)
        
        col_status = Gtk.TreeViewColumn("Durum")
        col_status.set_resizable(True)
        col_status.set_fixed_width(120)
        renderer_status = Gtk.CellRendererText()
        col_status.pack_start(renderer_status, True)
        col_status.add_attribute(renderer_status, "markup", 1)
        self.treeview.append_column(col_status)
        
        col_sub = Gtk.TreeViewColumn("Alt Durum")
        col_sub.set_resizable(True)
        col_sub.set_fixed_width(100)
        renderer_sub = Gtk.CellRendererText()
        col_sub.pack_start(renderer_sub, True)
        col_sub.add_attribute(renderer_sub, "text", 2)
        self.treeview.append_column(col_sub)
        
        col_blame = Gtk.TreeViewColumn("Süre")
        col_blame.set_resizable(True)
        col_blame.set_fixed_width(90)
        renderer_blame = Gtk.CellRendererText()
        col_blame.pack_start(renderer_blame, True)
        col_blame.add_attribute(renderer_blame, "text", 3)
        self.treeview.append_column(col_blame)
        
        self.selection = self.treeview.get_selection()
        
        self.detail_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.detail_area.get_style_context().add_class("card")
        self.detail_area.set_margin_top(8)
        box.pack_start(self.detail_area, False, False, 0)
        
        h_detail = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.detail_area.pack_start(h_detail, True, True, 0)
        
        v_detail_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        h_detail.pack_start(v_detail_text, True, True, 0)
        
        self.detail_name = Gtk.Label(xalign=0)
        self.detail_name.set_markup("<b>Servis seçilmedi</b>")
        self.detail_name.set_ellipsize(Pango.EllipsizeMode.END)
        v_detail_text.pack_start(self.detail_name, False, False, 0)
        
        self.detail_desc = Gtk.Label(xalign=0)
        self.detail_desc.set_text("Detayları görmek için listeden bir hizmet seçin.")
        self.detail_desc.set_line_wrap(True)
        v_detail_text.pack_start(self.detail_desc, False, False, 0)
        
        self.detail_suggestion = Gtk.Label(xalign=0)
        self.detail_suggestion.set_text("")
        self.detail_suggestion.set_line_wrap(True)
        v_detail_text.pack_start(self.detail_suggestion, False, False, 0)
        
        v_actions = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        v_actions.set_size_request(160, -1)
        h_detail.pack_start(v_actions, False, False, 0)
        
        self.btn_enable = Gtk.Button(label="Etkinleştir")
        v_actions.pack_start(self.btn_enable, False, False, 0)
        
        self.btn_run = Gtk.Button(label="Başlat")
        v_actions.pack_start(self.btn_run, False, False, 0)
        
        self.btn_mask = Gtk.Button(label="Maskele")
        v_actions.pack_start(self.btn_mask, False, False, 0)
        
        h_bottom_actions1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        v_actions.pack_start(h_bottom_actions1, False, False, 0)
        
        self.btn_log = Gtk.Button(label="Günlük Kaydı")
        h_bottom_actions1.pack_start(self.btn_log, True, True, 0)
        
        self.btn_dep = Gtk.Button(label="Bağımlılıklar")
        h_bottom_actions1.pack_start(self.btn_dep, True, True, 0)
        
        self.btn_refresh = Gtk.Button(label="Yenile")
        v_actions.pack_start(self.btn_refresh, False, False, 0)
        
        self.view_combo.connect("changed", self._on_view_changed)
        self.filter_combo.connect("changed", self._on_filter_changed)
        self.tip_combo.connect("changed", self._on_tip_changed)
        self.search_entry.connect("changed", self._on_search_changed)
        self.selection.connect("changed", self._on_selection_changed)
        
        self.btn_enable.connect("clicked", self._on_service_enable_clicked)
        self.btn_run.connect("clicked", self._on_service_run_clicked)
        self.btn_mask.connect("clicked", self._on_service_mask_clicked)
        self.btn_log.connect("clicked", self._on_show_log)
        self.btn_dep.connect("clicked", self._on_show_dependencies)
        self.btn_refresh.connect("clicked", self.load_all)
        
        box.show_all()
        return box

    def load_all(self, *args):
        self.manager.clear_cache()
        self._updating_widgets = True
        self.liststore.clear()
        self._all_data_map = {}
        self.detail_name.set_markup("<b>Servis seçilmedi</b>")
        self.detail_desc.set_text("Detayları görmek için listeden bir hizmet seçin.")
        self.detail_suggestion.set_text("")
        self.service_count_label.set_text("0 servis")
        self.set_status("Hizmetler yükleniyor...")
        self.btn_enable.set_sensitive(False)
        self.btn_run.set_sensitive(False)
        self.btn_mask.set_sensitive(False)
        self.btn_log.set_sensitive(False)
        self.btn_dep.set_sensitive(False)
        self._updating_widgets = False
        
        GLib.timeout_add(10, self._do_load)

    def _do_load(self):
        try:
            services = self.manager.get_services()
            enabled_map = self.manager.get_unit_file_states()
            
            blame_data = {}
            raw_blame, _ = self.manager.get_blame_data()
            for item in raw_blame:
                blame_data[item["name"]] = {
                    "time_str": item["time"],
                    "seconds": parse_blame_time(item["time"]),
                }
        except Exception as e:
            self.set_status(f"Yükleme hatası: {str(e)}")
            self.service_count_label.set_text("Hata")
            return False

        self._all_data = []
        for svc in services:
            name = svc["name"]
            if svc["load"] == "not-found":
                continue
            if not any(name.endswith(s) for s in (".service", ".mount", ".device", ".swap", ".socket", ".target")):
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
        self.set_status("Hizmet listesi güncellendi.")
        return False

    def _update_count_label(self):
        view = VIEW_MAP.get(self.view_combo.get_active(), "services")
        n = len(self.liststore)
        t = len(self._all_data)
        self.service_count_label.set_text(f"{n} servis" if n == t else f"{n}/{t} servis")

    def _apply_filters(self):
        old_selection = self._get_selected_name()
        self._updating_widgets = True
        self.liststore.clear()
        
        view = VIEW_MAP.get(self.view_combo.get_active(), "services")

        q = self._search_text.lower()
        for d in self._all_data:
            name = d["name"]
            
            # Filter by unit type
            if view == "services":
                if not name.endswith(".service"):
                    continue
            elif view == "devices":
                if not name.endswith(".device"):
                    continue
            elif view == "other":
                if name.endswith(".service") or name.endswith(".device"):
                    continue
            
            if q and q not in name.lower() and q not in d["desc"].lower():
                continue
            if not self._matches_status(d["active"], d["sub"], d.get("enabled", "")):
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
                d["active"]
            ])

        self._update_count_label()

        if old_selection:
            for i in range(len(self.liststore)):
                if self.liststore[i][0] == old_selection:
                    self.selection.select_path(Gtk.TreePath(i))
                    break
                    
        self._updating_widgets = False
        self._on_selection_changed()

    def _matches_status(self, active, sub, enabled=""):
        f = self._status_filter
        if f == "all":
            return True
        if f == "active":
            return active == "active"
        if f == "inactive":
            return active == "inactive"
        if f == "disabled":
            return sub == "disabled" or enabled == "disabled"
        if f == "masked":
            return sub == "masked" or enabled == "masked"
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
        if self._updating_widgets:
            return
            
        r = self._get_selected_row()
        if r is None:
            self.detail_name.set_markup("<b>Servis seçilmedi</b>")
            self.detail_desc.set_text("Detayları görmek için listeden bir hizmet seçin.")
            self.detail_suggestion.set_text("")
            self.btn_enable.set_sensitive(False)
            self.btn_run.set_sensitive(False)
            self.btn_mask.set_sensitive(False)
            self.btn_log.set_sensitive(False)
            self.btn_dep.set_sensitive(False)
            return

        name = r[0]
        d = self._all_data_map.get(name)
        active = d["active"] if d else r[7]
        color = STATUS_COLORS.get(active, "#6c757d")
        
        self.detail_name.set_markup(
            f"<b>{name}</b>  \u2014  <span foreground='{color}'><b>{STATUS_TR.get(active, active)}</b></span>"
        )
        self.detail_desc.set_text(r[4] or "Açıklama mevcut değil.")
        
        tip = r[5]
        oneri = r[6]
        if oneri:
            if tip == "kritik":
                self.detail_suggestion.set_markup(
                    "<span foreground='#dc3545' weight='bold'>⚠ KRİTİK HİZMET: </span>"
                    f"<span>{oneri}</span>"
                )
            elif tip == "oneri":
                self.detail_suggestion.set_markup(
                    "<span foreground='#198754' weight='bold'>💡 KULLANICI ÖNERİSİ: </span>"
                    f"<span>{oneri}</span>"
                )
            else:
                self.detail_suggestion.set_markup(f"<b>Öneri:</b> {oneri}")
        else:
            self.detail_suggestion.set_text("")

        self._update_service_buttons(name, d)

    def _update_service_buttons(self, name, d=None):
        if d is None:
            d = self._all_data_map.get(name)
        if d is None:
            self.btn_enable.set_sensitive(False)
            self.btn_run.set_sensitive(False)
            self.btn_mask.set_sensitive(False)
            self.btn_log.set_sensitive(False)
            self.btn_dep.set_sensitive(False)
            return

        if name.endswith(".device"):
            self.btn_enable.set_sensitive(False)
            self.btn_run.set_sensitive(False)
            self.btn_mask.set_sensitive(False)
            self.btn_log.set_sensitive(False)
            self.btn_dep.set_sensitive(False)
            return

        self.btn_enable.set_sensitive(True)
        self.btn_run.set_sensitive(True)
        self.btn_mask.set_sensitive(True)
        self.btn_log.set_sensitive(True)
        self.btn_dep.set_sensitive(True)

        sub = d["sub"]
        active_state = d["active"]
        enabled_state = d.get("enabled", "unknown")

        is_enabled = enabled_state in ("enabled", "enabled-runtime", "generated")
        is_running = active_state == "active"
        is_masked = sub == "masked" or enabled_state == "masked"

        if is_enabled:
            self.btn_enable.set_label("Devre Dışı Bırak")
            self.btn_enable.get_style_context().remove_class("success")
            self.btn_enable.get_style_context().add_class("danger")
        else:
            self.btn_enable.set_label("Etkinleştir")
            self.btn_enable.get_style_context().remove_class("danger")
            self.btn_enable.get_style_context().add_class("success")

        if is_running:
            self.btn_run.set_label("Durdur")
            self.btn_run.get_style_context().remove_class("primary")
            self.btn_run.get_style_context().add_class("danger")
        else:
            self.btn_run.set_label("Başlat")
            self.btn_run.get_style_context().remove_class("danger")
            self.btn_run.get_style_context().add_class("primary")

        if is_masked:
            self.btn_mask.set_label("Maskeyi Kaldır")
            self.btn_mask.get_style_context().remove_class("danger")
            self.btn_mask.get_style_context().add_class("warning")
        else:
            self.btn_mask.set_label("Maskele")
            self.btn_mask.get_style_context().remove_class("warning")
            self.btn_mask.get_style_context().add_class("danger")

        if enabled_state in ("static", "indirect", "masked", "generated"):
            self.btn_enable.set_sensitive(False)
        if sub == "masked" or enabled_state == "masked":
            self.btn_run.set_sensitive(False)
        if active_state in ("activating", "deactivating"):
            self.btn_run.set_sensitive(False)

    def _on_service_enable_clicked(self, button):
        name = self._get_selected_name()
        if not name:
            return
        d = self._all_data_map.get(name)
        if not d:
            return
        is_enabled = d.get("enabled", "unknown") in ("enabled", "enabled-runtime", "generated")
        action = "disable" if is_enabled else "enable"
        
        if action == "disable":
            deps = self.manager.get_reverse_dependencies(name)
            if deps:
                dlg = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.YES_NO,
                    message_format=f"'{name}' Hizmetini Kapatmak İstiyor musunuz?"
                )
                dep_list_str = "\n".join(f"- {dep}" for dep in deps[:8])
                if len(deps) > 8:
                    dep_list_str += f"\n- ve {len(deps) - 8} hizmet daha..."
                dlg.format_secondary_text(
                    f"Bu hizmeti kapatmak, ona bağımlı çalışan şu hizmetleri etkileyebilir:\n\n{dep_list_str}\n\nDevam etmek istiyor musunuz?"
                )
                resp = dlg.run()
                dlg.destroy()
                if resp != Gtk.ResponseType.YES:
                    return
                    
        self._run_systemctl(action, name, self.load_all)

    def _on_service_run_clicked(self, button):
        name = self._get_selected_name()
        if not name:
            return
        d = self._all_data_map.get(name)
        if not d:
            return
        is_running = d["active"] == "active"
        action = "stop" if is_running else "start"
        self._run_systemctl(action, name, self.load_all)

    def _on_service_mask_clicked(self, button):
        name = self._get_selected_name()
        if not name:
            return
        d = self._all_data_map.get(name)
        if not d:
            return
        is_masked = d["sub"] == "masked" or d.get("enabled", "unknown") == "masked"
        action = "unmask" if is_masked else "mask"

        if action == "mask":
            tip = d["tip"]
            warn = ("\n\nBu hizmet sistem için KRİTİK olarak işaretlenmiştir. "
                    "Maskelemeniz sistemin kararsız çalışmasına veya açılmamasına yol açabilir!") if tip == "kritik" else ""
            
            dlg = Gtk.MessageDialog(
                parent=self.window, flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.WARNING if tip == "kritik" else Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                message_format=f"'{name}' hizmetini maskelemek istiyor musunuz?"
            )
            if warn:
                dlg.format_secondary_text(warn)
            resp = dlg.run()
            dlg.destroy()
            if resp != Gtk.ResponseType.YES:
                return

        self._run_systemctl(action, name, self.load_all)

    def _run_systemctl(self, action, name, cb):
        action_tr = {"enable": "Etkinleştirme", "disable": "Devre dışı bırakma",
                     "start": "Başlatma", "stop": "Durdurma",
                     "mask": "Maskeleme", "unmask": "Maske kaldırma"}.get(action, action)
                     
        if not self._ensure_auth():
            self.set_status("Yetkilendirme iptal edildi.")
            return
            
        self.set_status(f"'{name}' için {action_tr} eylemi başlatıldı...")
        
        def task():
            try:
                m = {
                    "enable": self.manager.enable_service,
                    "disable": self.manager.disable_service,
                    "start": self.manager.start_service,
                    "stop": self.manager.stop_service,
                    "mask": self.manager.mask_service,
                    "unmask": self.manager.unmask_service
                }
                fn = m.get(action)
                ok, msg = fn(name) if fn else (False, f"Bilinmeyen eylem: {action}")
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
            self.set_status("Bir servis seçin.")
            return
            
        dialog = Gtk.Dialog(title=f"Log: {n}", parent=self.window, flags=Gtk.DialogFlags.MODAL)
        dialog.set_default_size(750, 480)
        dialog.add_button("Kapat", Gtk.ResponseType.CLOSE)
        
        content = dialog.get_content_area()
        content.set_margin_start(10)
        content.set_margin_end(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        
        scrolled = Gtk.ScrolledWindow()
        content.pack_start(scrolled, True, True, 0)
        
        txt_view = Gtk.TextView()
        txt_view.set_editable(False)
        txt_view.set_cursor_visible(False)
        txt_view.get_style_context().add_class("monospaced-log")
        scrolled.add(txt_view)
        
        buf = txt_view.get_buffer()
        buf.set_text("Loglar yükleniyor, lütfen bekleyin...")
        
        dialog.show_all()
        
        def task():
            try:
                log = self.manager.get_journal_log(n)
                GLib.idle_add(buf.set_text, log or "Log kaydı bulunamadı.")
            except Exception as e:
                GLib.idle_add(buf.set_text, f"Hata: {e}")
                
        threading.Thread(target=task, daemon=True).start()
        
        dialog.run()
        dialog.destroy()

    # --- Dependency Viewer ---
    def _on_show_dependencies(self, button):
        n = self._get_selected_name()
        if not n:
            self.set_status("Bir servis seçin.")
            return
            
        dialog = Gtk.Dialog(title=f"Bağımlılıklar: {n}", parent=self.window, flags=Gtk.DialogFlags.MODAL)
        dialog.set_default_size(550, 450)
        dialog.add_button("Kapat", Gtk.ResponseType.CLOSE)
        
        content = dialog.get_content_area()
        content.set_margin_start(10)
        content.set_margin_end(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        
        lbl_info = Gtk.Label(xalign=0)
        lbl_info.set_markup(f"<b>{n}</b> hizmetinin diğer sistem birimleriyle olan bağımlılık ilişkileri:")
        content.pack_start(lbl_info, False, False, 6)
        
        scrolled = Gtk.ScrolledWindow()
        content.pack_start(scrolled, True, True, 0)
        
        txt_view = Gtk.TextView()
        txt_view.set_editable(False)
        txt_view.set_cursor_visible(False)
        txt_view.get_style_context().add_class("monospaced-log")
        scrolled.add(txt_view)
        
        buf = txt_view.get_buffer()
        buf.set_text("Bağımlılık ağacı yükleniyor...")
        
        dialog.show_all()
        
        def task():
            try:
                deps = self.manager.get_dependencies(n)
                GLib.idle_add(buf.set_text, deps or "Bağımlılık bilgisi bulunamadı.")
            except Exception as e:
                GLib.idle_add(buf.set_text, f"Hata: {e}")
                
        threading.Thread(target=task, daemon=True).start()
        
        dialog.run()
        dialog.destroy()

    def _calculate_profile_savings(self, p_info):
        try:
            blame_list, _ = self.manager.get_blame_data()
            blame_map = {item["name"]: parse_blame_time(item["time"]) for item in blame_list}
            current_states = self.manager.get_unit_file_states()
        except Exception:
            return 0.0
            
        savings = 0.0
        for svc, action in p_info.get("services", {}).items():
            if action == "disable":
                state = current_states.get(svc)
                if state in ("enabled", "enabled-runtime") and svc in blame_map:
                    savings += blame_map[svc]
        return savings

    # --- Page 4: Profiller ---
    def build_page_profiller(self):
        main_scrolled = Gtk.ScrolledWindow()
        main_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        main_scrolled.add(box)
        
        lbl_title = Gtk.Label(xalign=0)
        lbl_title.set_text("Sistem Başlangıç Profilleri")
        lbl_title.get_style_context().add_class("content-title")
        box.pack_start(lbl_title, False, False, 0)
        
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_text("Sisteminizi tek tıkla belirli kullanım senaryolarına göre optimize edebilirsiniz.")
        lbl_sub.get_style_context().add_class("content-subtitle")
        box.pack_start(lbl_sub, False, False, 0)
        
        grid = Gtk.Grid(column_spacing=16, row_spacing=16)
        box.pack_start(grid, False, False, 0)
        
        self.profiles_data = {
            "ofis": {
                "name": "Ofis Modu",
                "icon": "document-open",
                "desc": "Günlük ofis işleri için ideal. Yazıcı ve ağ servisleri etkinleştirilirken; Docker ve veritabanı servisleri kapatılarak açılış hızlandırılır.",
                "services": {
                    "cups.service": "enable",
                    "cups-browsed.service": "enable",
                    "bluetooth.service": "enable",
                    "docker.service": "disable",
                    "postgresql.service": "disable",
                    "mysql.service": "disable",
                    "ssh.service": "disable",
                    "sshd.service": "disable",
                    "avahi-daemon.service": "enable",
                    "ModemManager.service": "disable",
                    "NetworkManager-wait-online.service": "disable"
                }
            },
            "yazilimci": {
                "name": "Yazılımcı Modu",
                "icon": "utilities-terminal",
                "desc": "Yazılım geliştiriciler için hazırlandı. Docker, SSH ve veritabanı servisleri otomatik olarak etkinleştirilir. Yazıcı gibi gereksiz servisler kapatılır.",
                "services": {
                    "cups.service": "disable",
                    "cups-browsed.service": "disable",
                    "bluetooth.service": "enable",
                    "docker.service": "enable",
                    "postgresql.service": "enable",
                    "mysql.service": "enable",
                    "ssh.service": "enable",
                    "sshd.service": "enable",
                    "avahi-daemon.service": "disable",
                    "ModemManager.service": "disable",
                    "NetworkManager-wait-online.service": "disable"
                }
            },
            "minimum": {
                "name": "Minimum Mod",
                "icon": "battery",
                "desc": "Sistemi en hızlı ve hafif şekilde başlatmak için. Ağ ve temel sistem güvenliği dışındaki tüm ek servisler kapatılır. Pil tasarrufu sağlar.",
                "services": {
                    "cups.service": "disable",
                    "cups-browsed.service": "disable",
                    "bluetooth.service": "disable",
                    "docker.service": "disable",
                    "postgresql.service": "disable",
                    "mysql.service": "disable",
                    "ssh.service": "disable",
                    "sshd.service": "disable",
                    "avahi-daemon.service": "disable",
                    "ModemManager.service": "disable",
                    "NetworkManager-wait-online.service": "disable",
                    "colord.service": "disable",
                    "lm-sensors.service": "disable",
                    "smartmontools.service": "disable"
                }
            }
        }
        
        col = 0
        for p_id, p_info in self.profiles_data.items():
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            card.get_style_context().add_class("profile-card")
            card.set_size_request(240, 240)
            
            h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            img = Gtk.Image.new_from_icon_name(p_info["icon"], Gtk.IconSize.DND)
            img.set_pixel_size(40)
            h_box.pack_start(img, False, False, 0)
            
            lbl_pname = Gtk.Label(xalign=0)
            lbl_pname.set_text(p_info["name"])
            lbl_pname.get_style_context().add_class("profile-title")
            h_box.pack_start(lbl_pname, True, True, 0)
            card.pack_start(h_box, False, False, 0)
            
            vbox_checklist = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            vbox_checklist.set_margin_top(6)
            vbox_checklist.set_margin_bottom(6)
            
            for svc_name, friendly_name in PROFILE_SERVICE_LABELS.items():
                action = p_info["services"].get(svc_name)
                if action is not None:
                    lbl_item = Gtk.Label(xalign=0)
                    lbl_item.get_style_context().add_class("profile-desc")
                    if action == "enable":
                        lbl_item.set_markup(f"<span foreground='#2ec27e'>✔</span>  {friendly_name}")
                    else:
                        lbl_item.set_markup(f"<span foreground='#e01b24'>✘</span>  {friendly_name}")
                    vbox_checklist.pack_start(lbl_item, False, False, 0)
            
            card.pack_start(vbox_checklist, True, True, 0)
            
            # Calculate and display estimated savings
            savings = self._calculate_profile_savings(p_info)
            lbl_saving = Gtk.Label()
            lbl_saving.get_style_context().add_class("dim-label")
            if savings > 0.05:
                lbl_saving.set_markup(f"<span foreground='#2ec27e'><b>Tahmini Kazanç: ~{savings:.1f}s</b></span>")
            else:
                lbl_saving.set_markup(f"<span foreground='#888888'>Tahmini Kazanç: &lt; 0.1s</span>")
            lbl_saving.set_margin_bottom(4)
            card.pack_start(lbl_saving, False, False, 0)
            
            btn_apply = Gtk.Button(label="Profili Uygula")
            btn_apply.get_style_context().add_class("primary")
            btn_apply.connect("clicked", self._on_apply_profile_clicked, p_id)
            card.pack_start(btn_apply, False, False, 0)
            
            grid.attach(card, col, 0, 1, 1)
            col += 1
            
        lbl_custom_title = Gtk.Label(xalign=0)
        lbl_custom_title.set_text("Kullanıcı Özel Profilleri")
        lbl_custom_title.get_style_context().add_class("card-title")
        lbl_custom_title.set_margin_top(16)
        box.pack_start(lbl_custom_title, False, False, 8)
        
        h_custom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.pack_start(h_custom_bar, False, False, 0)
        
        btn_save_curr = Gtk.Button(label="Mevcut Durumu Profil Olarak Kaydet")
        btn_save_curr.get_style_context().add_class("success")
        btn_save_curr.connect("clicked", self._on_save_custom_profile_clicked)
        h_custom_bar.pack_start(btn_save_curr, False, False, 0)
        
        btn_create_custom = Gtk.Button(label="Yeni Özel Profil Oluştur")
        btn_create_custom.get_style_context().add_class("primary")
        btn_create_custom.connect("clicked", self._on_create_custom_profile_clicked)
        h_custom_bar.pack_start(btn_create_custom, False, False, 0)
        
        self.custom_profiles_listbox = Gtk.ListBox()
        self.custom_profiles_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        box.pack_start(self.custom_profiles_listbox, False, False, 0)
        
        # Geri Yükleme Noktaları (Yedekler)
        lbl_backup_title = Gtk.Label(xalign=0)
        lbl_backup_title.set_text("Sistem Geri Yükleme Noktaları")
        lbl_backup_title.get_style_context().add_class("card-title")
        lbl_backup_title.set_margin_top(24)
        box.pack_start(lbl_backup_title, False, False, 8)
        
        h_backup_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.pack_start(h_backup_bar, False, False, 0)
        
        btn_create_backup = Gtk.Button(label="Yeni Geri Yükleme Noktası Oluştur")
        btn_create_backup.get_style_context().add_class("warning")
        btn_create_backup.connect("clicked", self._on_create_backup_clicked)
        h_backup_bar.pack_start(btn_create_backup, False, False, 0)
        
        self.backups_listbox = Gtk.ListBox()
        self.backups_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        box.pack_start(self.backups_listbox, False, False, 0)
        
        main_scrolled.show_all()
        return main_scrolled

    def get_custom_profiles_dir(self):
        path = os.path.expanduser("~/.config/boot-manager-profiles")
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return path

    def load_profiles_page(self):
        for child in self.custom_profiles_listbox.get_children():
            self.custom_profiles_listbox.remove(child)
            
        p_dir = self.get_custom_profiles_dir()
        files = [f for f in os.listdir(p_dir) if f.endswith(".json")]
        
        if not files:
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label()
            lbl.set_markup("<span foreground='#888888'>Kayıtlı özel profil bulunamadı.</span>")
            lbl.set_margin_top(16)
            lbl.set_margin_bottom(16)
            row.add(lbl)
            self.custom_profiles_listbox.add(row)
        else:
            for fname in files:
                fpath = os.path.join(p_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        p_info = json.load(f)
                    
                    row = Gtk.ListBoxRow()
                    row.get_style_context().add_class("autostart-row")
                    
                    h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                    row.add(h_box)
                    
                    img = Gtk.Image.new_from_icon_name("avatar-default", Gtk.IconSize.LARGE_TOOLBAR)
                    h_box.pack_start(img, False, False, 0)
                    
                    v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                    lbl_name = Gtk.Label(xalign=0)
                    lbl_name.set_markup(f"<b>{p_info['name']}</b>")
                    v_box.pack_start(lbl_name, False, False, 0)
                    
                    count = len(p_info["services"])
                    lbl_desc = Gtk.Label(xalign=0)
                    lbl_desc.set_markup(f"<span size='small' foreground='#666666'>{count} hizmet kuralı</span>")
                    v_box.pack_start(lbl_desc, False, False, 0)
                    
                    h_box.pack_start(v_box, True, True, 0)
                    
                    btn_apply = Gtk.Button(label="Uygula")
                    btn_apply.get_style_context().add_class("primary")
                    btn_apply.connect("clicked", self._on_apply_custom_profile_clicked, fpath)
                    h_box.pack_start(btn_apply, False, False, 6)
                    
                    btn_del = Gtk.Button()
                    img_del = Gtk.Image.new_from_icon_name("user-trash", Gtk.IconSize.BUTTON)
                    btn_del.set_image(img_del)
                    btn_del.get_style_context().add_class("danger")
                    btn_del.connect("clicked", self._on_delete_custom_profile_clicked, fpath)
                    h_box.pack_start(btn_del, False, False, 0)
                    
                    self.custom_profiles_listbox.add(row)
                except Exception:
                    pass
        self.custom_profiles_listbox.show_all()
        
        # Load backups
        for child in self.backups_listbox.get_children():
            self.backups_listbox.remove(child)
            
        backups = self.manager.get_backups()
        if not backups:
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label()
            lbl.set_markup("<span foreground='#888888'>Oluşturulmuş geri yükleme noktası bulunamadı.</span>")
            lbl.set_margin_top(16)
            lbl.set_margin_bottom(16)
            row.add(lbl)
            self.backups_listbox.add(row)
        else:
            for b in backups:
                fpath = b["filepath"]
                row = Gtk.ListBoxRow()
                row.get_style_context().add_class("autostart-row")
                
                h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                row.add(h_box)
                
                img = Gtk.Image.new_from_icon_name("system-run", Gtk.IconSize.LARGE_TOOLBAR)
                h_box.pack_start(img, False, False, 0)
                
                v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                lbl_name = Gtk.Label(xalign=0)
                lbl_name.set_markup(f"<b>{b['name']}</b>")
                v_box.pack_start(lbl_name, False, False, 0)
                
                count = len(b["services"])
                lbl_desc = Gtk.Label(xalign=0)
                lbl_desc.set_markup(f"<span size='small' foreground='#666666'>{count} hizmetin yedeği</span>")
                v_box.pack_start(lbl_desc, False, False, 0)
                
                h_box.pack_start(v_box, True, True, 0)
                
                btn_restore = Gtk.Button(label="Geri Yükle")
                btn_restore.get_style_context().add_class("warning")
                btn_restore.connect("clicked", self._on_restore_backup_clicked, fpath)
                h_box.pack_start(btn_restore, False, False, 6)
                
                btn_del = Gtk.Button()
                img_del = Gtk.Image.new_from_icon_name("user-trash", Gtk.IconSize.BUTTON)
                btn_del.set_image(img_del)
                btn_del.get_style_context().add_class("danger")
                btn_del.connect("clicked", self._on_delete_backup_clicked, fpath)
                h_box.pack_start(btn_del, False, False, 0)
                
                self.backups_listbox.add(row)
        self.backups_listbox.show_all()

    def _on_create_backup_clicked(self, button):
        ok, msg = self.manager.create_backup()
        if ok:
            self.set_status("Geri yükleme noktası oluşturuldu.")
            self.load_profiles_page()
        else:
            self.set_status(f"Hata: {msg}")

    def _on_restore_backup_clicked(self, button, fpath):
        dlg = Gtk.MessageDialog(
            parent=self.window, flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO,
            message_format="Yedek Noktasına Dönmek İstiyor musunuz?"
        )
        dlg.format_secondary_text("Bu işlem sistem servislerinin başlangıç durumlarını yedeğin alındığı tarihteki durumuna geri yükleyecektir.")
        resp = dlg.run()
        dlg.destroy()
        if resp != Gtk.ResponseType.YES:
            return
            
        if not self._ensure_auth():
            self.set_status("Yetkilendirme iptal edildi.")
            return
            
        loader = Gtk.Dialog(title="Yedek Geri Yükleniyor", parent=self.window, flags=Gtk.DialogFlags.MODAL)
        loader.set_default_size(320, 140)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(18)
        box.set_margin_end(18)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        loader.get_content_area().add(box)
        
        lbl = Gtk.Label(label="Sistem yedeği geri yükleniyor, lütfen bekleyin...")
        box.pack_start(lbl, False, False, 0)
        
        spinner = Gtk.Spinner()
        box.pack_start(spinner, True, True, 0)
        spinner.start()
        loader.show_all()
        
        def task():
            ok, msg = self.manager.restore_backup(fpath)
            GLib.idle_add(done, ok, msg)
            
        def done(ok, msg):
            spinner.stop()
            loader.destroy()
            self.set_status(msg)
            if ok:
                self.load_all()
                self.load_profiles_page()
                
        threading.Thread(target=task, daemon=True).start()

    def _on_delete_backup_clicked(self, button, fpath):
        dlg = Gtk.MessageDialog(
            parent=self.window, flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO,
            message_format="Yedek Noktasını Silmek İstiyor musunuz?"
        )
        resp = dlg.run()
        dlg.destroy()
        if resp == Gtk.ResponseType.YES:
            try:
                os.remove(fpath)
                self.set_status("Yedek noktası silindi.")
                self.load_profiles_page()
            except Exception as e:
                self.set_status(f"Hata: {e}")

    def _on_apply_profile_clicked(self, button, p_id):
        p_info = self.profiles_data.get(p_id)
        if not p_info:
            return
            
        dlg = Gtk.MessageDialog(
            parent=self.window, flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            message_format=f"'{p_info['name']}' profilini uygulamak istiyor musunuz?"
        )
        dlg.format_secondary_text("Bu işlem sistem servislerinin başlangıç durumlarını toplu olarak düzenleyecektir.")
        resp = dlg.run()
        dlg.destroy()
        if resp != Gtk.ResponseType.YES:
            return
            
        try:
            enabled_map = self.manager.get_unit_file_states()
        except Exception as e:
            self.set_status(f"Hata: {e}")
            return
            
        enable_list = []
        disable_list = []
        
        for svc, action in p_info.get("services", {}).items():
            if svc not in enabled_map:
                continue
            curr = enabled_map[svc]
            if action == "enable" and curr not in ("enabled", "enabled-runtime"):
                enable_list.append(svc)
            elif action == "disable" and curr in ("enabled", "enabled-runtime", "static", "indirect"):
                disable_list.append(svc)
                
        if not enable_list and not disable_list:
            self.set_status("Sistem zaten bu profile uygun durumda.")
            info = Gtk.MessageDialog(
                parent=self.window, flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK,
                message_format="Profil Zaten Uygulanmış"
            )
            info.format_secondary_text("Hizmetlerin başlangıç durumları zaten bu profile uygun.")
            info.run()
            info.destroy()
            return
            
        all_deps = {}
        for svc in disable_list:
            deps = self.manager.get_reverse_dependencies(svc)
            filtered_deps = [d for d in deps if d not in disable_list]
            if filtered_deps:
                all_deps[svc] = filtered_deps

        if all_deps:
            dep_msg = "Bu profili uygulamak aşağıdaki aktif hizmetleri ve onlara bağlı servisleri etkileyebilir:\n\n"
            for parent, kids in list(all_deps.items())[:5]:
                dep_msg += f"• {parent} ➔ {', '.join(kids[:3])}\n"
            if len(all_deps) > 5:
                dep_msg += f"• ve {len(all_deps) - 5} hizmet daha...\n"
                
            dep_dlg = Gtk.MessageDialog(
                parent=self.window, flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.YES_NO,
                message_format="Profil Uygulama Bağımlılık Uyarısı"
            )
            dep_dlg.format_secondary_text(dep_msg + "\nDevam etmek istiyor musunuz?")
            dep_resp = dep_dlg.run()
            dep_dlg.destroy()
            if dep_resp != Gtk.ResponseType.YES:
                return
            
        if not self._ensure_auth():
            self.set_status("Yetkilendirme iptal edildi.")
            return
            
        self._run_profile_batch(enable_list, disable_list)

    def _on_apply_custom_profile_clicked(self, button, fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                p_info = json.load(f)
        except Exception as e:
            self.set_status(f"Profil okuma hatası: {e}")
            return
            
        dlg = Gtk.MessageDialog(
            parent=self.window, flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            message_format=f"'{p_info['name']}' özel profilini uygulamak istiyor musunuz?"
        )
        resp = dlg.run()
        dlg.destroy()
        if resp != Gtk.ResponseType.YES:
            return
            
        try:
            enabled_map = self.manager.get_unit_file_states()
        except Exception as e:
            self.set_status(f"Hata: {e}")
            return
            
        enable_list = []
        disable_list = []
        
        for svc, action in p_info.get("services", {}).items():
            if svc not in enabled_map:
                continue
            curr = enabled_map[svc]
            if action == "enable" and curr not in ("enabled", "enabled-runtime"):
                enable_list.append(svc)
            elif action == "disable" and curr in ("enabled", "enabled-runtime", "static", "indirect"):
                disable_list.append(svc)
                
        if not enable_list and not disable_list:
            self.set_status("Sistem zaten bu profile uygun durumda.")
            return
            
        all_deps = {}
        for svc in disable_list:
            deps = self.manager.get_reverse_dependencies(svc)
            filtered_deps = [d for d in deps if d not in disable_list]
            if filtered_deps:
                all_deps[svc] = filtered_deps

        if all_deps:
            dep_msg = "Bu profili uygulamak aşağıdaki aktif hizmetleri ve onlara bağlı servisleri etkileyebilir:\n\n"
            for parent, kids in list(all_deps.items())[:5]:
                dep_msg += f"• {parent} ➔ {', '.join(kids[:3])}\n"
            if len(all_deps) > 5:
                dep_msg += f"• ve {len(all_deps) - 5} hizmet daha...\n"
                
            dep_dlg = Gtk.MessageDialog(
                parent=self.window, flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.YES_NO,
                message_format="Profil Uygulama Bağımlılık Uyarısı"
            )
            dep_dlg.format_secondary_text(dep_msg + "\nDevam etmek istiyor musunuz?")
            dep_resp = dep_dlg.run()
            dep_dlg.destroy()
            if dep_resp != Gtk.ResponseType.YES:
                return
            
        if not self._ensure_auth():
            self.set_status("Yetkilendirme iptal edildi.")
            return
            
        self._run_profile_batch(enable_list, disable_list)

    def _run_profile_batch(self, enable_list, disable_list):
        loader = Gtk.Dialog(title="Profil Uygulanıyor", parent=self.window, flags=Gtk.DialogFlags.MODAL)
        loader.set_default_size(320, 140)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(18)
        box.set_margin_end(18)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        loader.get_content_area().add(box)
        
        lbl = Gtk.Label(label="Hizmet profili uygulanıyor, lütfen bekleyin...")
        box.pack_start(lbl, False, False, 0)
        
        spinner = Gtk.Spinner()
        box.pack_start(spinner, True, True, 0)
        spinner.start()
        
        loader.show_all()
        
        def task():
            self.manager.create_backup()
            ok, msg = self.manager.apply_profile_batch(enable_list, disable_list)
            GLib.idle_add(done, ok, msg)
            
        def done(ok, msg):
            spinner.stop()
            loader.destroy()
            self.set_status(msg)
            if ok:
                info = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK,
                    message_format="Profil Başarıyla Uygulandı!"
                )
                info.run()
                info.destroy()
                self.load_all()
            else:
                err = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
                    message_format="Profil Uygulanırken Hata Oluştu",
                )
                err.format_secondary_text(msg)
                err.run()
                err.destroy()
                
        threading.Thread(target=task, daemon=True).start()

    def _on_save_custom_profile_clicked(self, button):
        dialog = Gtk.Dialog(title="Profili Kaydet", parent=self.window, flags=Gtk.DialogFlags.MODAL)
        dialog.add_button("İptal", Gtk.ResponseType.CANCEL)
        btn_save = dialog.add_button("Kaydet", Gtk.ResponseType.OK)
        btn_save.get_style_context().add_class("primary")
        
        content = dialog.get_content_area()
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.pack_start(vbox, True, True, 0)
        
        lbl = Gtk.Label(label="Yeni profil adı girin:", xalign=0)
        vbox.pack_start(lbl, False, False, 0)
        
        entry = Gtk.Entry()
        entry.set_text("Özel Profilim")
        vbox.pack_start(entry, False, False, 0)
        
        dialog.show_all()
        resp = dialog.run()
        p_name = entry.get_text().strip()
        dialog.destroy()
        
        if resp != Gtk.ResponseType.OK or not p_name:
            return
            
        try:
            enabled_map = self.manager.get_unit_file_states()
        except Exception as e:
            self.set_status(f"Hata: {e}")
            return
            
        from src.service_db import DESCRIPTIONS
        profile_services = {}
        for name, state in enabled_map.items():
            if name in DESCRIPTIONS:
                if state in ("enabled", "enabled-runtime"):
                    profile_services[name] = "enable"
                elif state in ("disabled", "disabled-runtime"):
                    profile_services[name] = "disable"
                    
        p_dir = self.get_custom_profiles_dir()
        safe_fname = "".join(c for c in p_name if c.isalnum() or c in ("-", "_")).lower()
        if not safe_fname:
            safe_fname = "custom"
            
        fpath = os.path.join(p_dir, f"{safe_fname}.json")
        counter = 1
        while os.path.exists(fpath):
            fpath = os.path.join(p_dir, f"{safe_fname}-{counter}.json")
            counter += 1
            
        profile_data = {
            "name": p_name,
            "services": profile_services
        }
        
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            self.set_status(f"'{p_name}' profili kaydedildi.")
            self.load_profiles_page()
        except Exception as e:
            self.set_status(f"Kaydetme hatası: {e}")

    def _on_delete_custom_profile_clicked(self, button, fpath):
        try:
            if os.path.exists(fpath):
                os.remove(fpath)
                self.set_status("Özel profil silindi.")
                self.load_profiles_page()
        except Exception as e:
            self.set_status(f"Silme hatası: {e}")

    def _on_create_custom_profile_clicked(self, button):
        dlg = ProfileCreatorDialog(self.window)
        response = dlg.run()
        
        if response == Gtk.ResponseType.OK:
            data, err = dlg.get_profile_data()
            dlg.hide()
            GLib.idle_add(dlg.destroy)
            
            if err:
                self.set_status(f"Hata: {err}")
                return
                
            p_dir = self.get_custom_profiles_dir()
            clean_name = "".join(c for c in data["name"] if c.isalnum() or c in (" ", "_", "-")).rstrip()
            filename = clean_name.replace(" ", "_").lower() + ".json"
            fpath = os.path.join(p_dir, filename)
            
            try:
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                self.set_status(f"Özel profil '{data['name']}' başarıyla oluşturuldu.")
                self.load_profiles_page()
            except Exception as e:
                self.set_status(f"Hata: {e}")
        else:
            dlg.hide()
            GLib.idle_add(dlg.destroy)

    # --- Sidebar Row Selected ---
    def _on_sidebar_row_selected(self, listbox, row):
        if not row:
            return
        idx = row.get_index()
        if idx == 0:
            self.stack.set_visible_child_name("analiz")
            self.load_analysis_page()
        elif idx == 1:
            self.stack.set_visible_child_name("autostart")
            self.load_autostart_page()
        elif idx == 2:
            self.stack.set_visible_child_name("hizmetler")
        elif idx == 3:
            self.stack.set_visible_child_name("profiller")
            self.load_profiles_page()

try:
    from gi.repository import Pango
except ImportError:
    class PangoFallback:
        EllipsizeMode = type('EllipsizeMode', (), {'END': 3})
    Pango = PangoFallback()

class ProfileCreatorDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Yeni Özel Profil Oluştur", parent=parent, flags=Gtk.DialogFlags.MODAL)
        self.set_default_size(420, 480)
        
        # Add buttons
        self.add_button("İptal", Gtk.ResponseType.CANCEL)
        btn_save = self.add_button("Kaydet", Gtk.ResponseType.OK)
        btn_save.get_style_context().add_class("primary")
        
        # Main layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        self.get_content_area().add(box)
        
        # Name Entry
        lbl_name = Gtk.Label(xalign=0)
        lbl_name.set_markup("<b>Profil Adı:</b>")
        box.pack_start(lbl_name, False, False, 0)
        
        self.entry_name = Gtk.Entry()
        self.entry_name.set_placeholder_text("Örn: Yazılım & Ofis Karışık")
        box.pack_start(self.entry_name, False, False, 0)
        
        # Services label
        lbl_services = Gtk.Label(xalign=0)
        lbl_services.set_markup("<b>Hizmet Kuralları:</b>\n<span size='small' foreground='#666666'>Açık = Etkinleştirilir, Kapalı = Devre dışı bırakılır</span>")
        lbl_services.set_margin_top(8)
        box.pack_start(lbl_services, False, False, 0)
        
        # Scrolled window for services list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(250)
        box.pack_start(scrolled, True, True, 0)
        
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(listbox)
        
        # List of candidate services to configure
        self.candidate_services = {
            "cups.service": "Yazıcı Servisi (CUPS)",
            "cups-browsed.service": "Ağ Yazıcısı Bulucu",
            "bluetooth.service": "Bluetooth Desteği",
            "docker.service": "Docker Konteyner",
            "postgresql.service": "PostgreSQL Veritabanı",
            "mysql.service": "MySQL / MariaDB Veritabanı",
            "ssh.service": "SSH Uzaktan Erişim",
            "avahi-daemon.service": "Yerel Ağ Keşfi (Avahi)",
            "ModemManager.service": "Hücresel Modem Kontrolü",
        }
        
        self.switches = {}
        for svc, label in self.candidate_services.items():
            row = Gtk.ListBoxRow()
            row.set_margin_bottom(2)
            
            h_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            h_row.set_margin_start(8)
            h_row.set_margin_end(8)
            h_row.set_margin_top(6)
            h_row.set_margin_bottom(6)
            row.add(h_row)
            
            lbl_svc = Gtk.Label(label=label, xalign=0)
            h_row.pack_start(lbl_svc, True, True, 0)
            
            switch = Gtk.Switch()
            switch.set_active(False)
            h_row.pack_start(switch, False, False, 0)
            self.switches[svc] = switch
            
            listbox.add(row)
            
        self.show_all()
        
    def get_profile_data(self):
        name = self.entry_name.get_text().strip()
        if not name:
            return None, "Lütfen profil adı girin."
            
        services = {}
        for svc, switch in self.switches.items():
            services[svc] = "enable" if switch.get_active() else "disable"
            
        return {
            "name": name,
            "services": services
        }, None
