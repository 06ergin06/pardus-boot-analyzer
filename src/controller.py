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
try:
    from locale_mgr import tr
except ImportError:
    from src.locale_mgr import tr
from src.dialogs import AddAutostartDialog, PasswordDialog, ProfileCreatorDialog
from src.pages.analysis import AnalysisPage
from src.pages.autostart import AutostartPage
from src.pages.services import ServicesPage
from src.pages.profiles import ProfilesPage


from src.utils import (
    STATUS_COLORS, STATUS_TR, FILTER_MAP, TIP_MAP, VIEW_MAP,
    SAFE_TO_DISABLE_ONERI_SERVICES, PROFILE_SERVICE_LABELS,
    parse_blame_time, make_status_markup, _is_dark_theme, _config_data
)

# --- Add Autostart Application Dialog ---
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
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        def _load_file(path):
            provider = Gtk.CssProvider()
            try:
                provider.load_from_path(path)
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            except Exception:
                pass

        # 1. Always load the base stylesheet (light + neutral tokens)
        _load_file(os.path.join(base_dir, "ui", "style.css"))

        # 2. Layer dark overrides on top if a dark theme is active
        if _is_dark_theme():
            _load_file(os.path.join(base_dir, "ui", "style-dark.css"))

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
        lbl_sub.set_text(tr("side_title_sub"))
        lbl_sub.get_style_context().add_class("sidebar-subtitle")
        vbox_logo.pack_start(lbl_sub, False, False, 0)
        
        sidebar_box.pack_start(vbox_logo, False, False, 0)

        self.sidebar_listbox = Gtk.ListBox()
        self.sidebar_listbox.get_style_context().add_class("sidebar-list")
        self.sidebar_listbox.connect("row-selected", self._on_sidebar_row_selected)
        sidebar_box.pack_start(self.sidebar_listbox, False, False, 0)

        items = [
            ("dialog-information-symbolic", tr("side_analiz"), "analiz"),
            ("system-run-symbolic", tr("side_autostart"), "autostart"),
            ("preferences-system-symbolic", tr("side_hizmetler"), "hizmetler"),
            ("avatar-default-symbolic", tr("side_profiller"), "profiller")
        ]
        
        for icon_name, text, name in items:
            row = Gtk.ListBoxRow()
            row.get_style_context().add_class("sidebar-row")
            
            box_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            
            img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
            img.set_pixel_size(20)
            img.set_valign(Gtk.Align.CENTER)
            box_row.pack_start(img, False, False, 0)
            
            lbl = Gtk.Label(xalign=0)
            lbl.get_style_context().add_class("sidebar-item-label")
            lbl.set_text(text)
            lbl.set_valign(Gtk.Align.CENTER)
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

        self.analysis_page = AnalysisPage(self)
        self.stack.add_named(self.analysis_page.build_page_analysis(), "analiz")
        self.autostart_page = AutostartPage(self)
        self.stack.add_named(self.autostart_page.build_page_autostart(), "autostart")
        self.services_page = ServicesPage(self)
        self.stack.add_named(self.services_page.build_page_services(), "hizmetler")
        self.profiles_page = ProfilesPage(self)
        self.stack.add_named(self.profiles_page.build_page_profiles(), "profiller")

        self.sidebar_listbox.select_row(self.sidebar_listbox.get_row_at_index(0))

    # --- Page 1: Analiz (Dashboard) ---

    def rebuild_ui_for_language(self):
        # 1. Store current selected sidebar index
        selected_row = self.sidebar_listbox.get_selected_row()
        selected_index = selected_row.get_index() if selected_row else 0
        
        # 2. Clear old pages from Gtk.Stack
        for child in self.stack.get_children():
            self.stack.remove(child)
            child.destroy()
            
        # 3. Clear old sidebar items
        for child in self.sidebar_listbox.get_children():
            self.sidebar_listbox.remove(child)
            child.destroy()
            
        # 4. Rebuild sidebar rows with new translations
        items = [
            ("dialog-information-symbolic", tr("side_analiz"), "analiz"),
            ("system-run-symbolic", tr("side_autostart"), "autostart"),
            ("preferences-system-symbolic", tr("side_hizmetler"), "hizmetler"),
            ("avatar-default-symbolic", tr("side_profiller"), "profiller")
        ]
        
        for icon_name, text, name in items:
            row = Gtk.ListBoxRow()
            row.get_style_context().add_class("sidebar-row")
            box_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            
            img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
            img.set_pixel_size(20)
            img.set_valign(Gtk.Align.CENTER)
            box_row.pack_start(img, False, False, 0)
            
            lbl = Gtk.Label(xalign=0)
            lbl.get_style_context().add_class("sidebar-item-label")
            lbl.set_text(text)
            lbl.set_valign(Gtk.Align.CENTER)
            box_row.pack_start(lbl, True, True, 0)
            
            row.add(box_row)
            self.sidebar_listbox.add(row)
            
        self.sidebar_listbox.show_all()
        
        # 5. Rebuild pages
        self.analysis_page = AnalysisPage(self)
        self.stack.add_named(self.analysis_page.build_page_analysis(), "analiz")
        self.autostart_page = AutostartPage(self)
        self.stack.add_named(self.autostart_page.build_page_autostart(), "autostart")
        self.services_page = ServicesPage(self)
        self.stack.add_named(self.services_page.build_page_services(), "hizmetler")
        self.profiles_page = ProfilesPage(self)
        self.stack.add_named(self.profiles_page.build_page_profiles(), "profiller")
        
        # 6. Reload data to populate widgets
        self.load_all()
        
        # 7. Restore sidebar selection
        self.sidebar_listbox.select_row(self.sidebar_listbox.get_row_at_index(selected_index))
    def _on_sidebar_row_selected(self, listbox, row):
        if not row:
            return
        idx = row.get_index()
        if idx == 0:
            self.stack.set_visible_child_name("analiz")
            self.analysis_page.load_analysis_page()
        elif idx == 1:
            self.stack.set_visible_child_name("autostart")
            self.autostart_page.load_autostart_page()
        elif idx == 2:
            self.stack.set_visible_child_name("hizmetler")
        elif idx == 3:
            self.stack.set_visible_child_name("profiller")
            self.profiles_page.load_profiles_page()

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

    def load_all(self, *args):
        self.analysis_page.load_analysis_page()
        self.autostart_page.load_autostart_page()
        self.services_page.load_all()
        self.profiles_page.load_profiles_page()

    # Expose ServicesPage properties for backward compatibility
    @property
    def liststore(self):
        return self.services_page.liststore

    @property
    def selection(self):
        return self.services_page.selection

    @property
    def treeview(self):
        return self.services_page.treeview

    @property
    def view_combo(self):
        return self.services_page.view_combo

    @property
    def filter_combo(self):
        return self.services_page.filter_combo

    @property
    def tip_combo(self):
        return self.services_page.tip_combo

    @property
    def search_entry(self):
        return self.services_page.search_entry

try:
    from gi.repository import Pango
except ImportError:
    class PangoFallback:
        EllipsizeMode = type('EllipsizeMode', (), {'END': 3})
    Pango = PangoFallback()

