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
from src.pages.analiz import AnalizPage
from src.pages.autostart import AutostartPage


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

        self.analiz_page = AnalizPage(self)
        self.stack.add_named(self.analiz_page.build_page_analiz(), "analiz")
        self.autostart_page = AutostartPage(self)
        self.stack.add_named(self.autostart_page.build_page_autostart(), "autostart")
        self.stack.add_named(self.build_page_hizmetler(), "hizmetler")
        self.stack.add_named(self.build_page_profiller(), "profiller")

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
        self.analiz_page = AnalizPage(self)
        self.stack.add_named(self.analiz_page.build_page_analiz(), "analiz")
        self.autostart_page = AutostartPage(self)
        self.stack.add_named(self.autostart_page.build_page_autostart(), "autostart")
        self.stack.add_named(self.build_page_hizmetler(), "hizmetler")
        self.stack.add_named(self.build_page_profiller(), "profiller")
        
        # 6. Reload data to populate widgets
        self.load_all()
        
        # 7. Restore sidebar selection
        self.sidebar_listbox.select_row(self.sidebar_listbox.get_row_at_index(selected_index))
    def build_page_hizmetler(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        lbl_title = Gtk.Label(xalign=0)
        lbl_title.set_text(tr("side_hizmetler"))
        lbl_title.get_style_context().add_class("content-title")
        box.pack_start(lbl_title, False, False, 0)
        
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_text(tr("hizmetler_subtitle"))
        lbl_sub.get_style_context().add_class("content-subtitle")
        box.pack_start(lbl_sub, False, False, 0)
        
        f_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.pack_start(f_box, False, False, 0)
        
        self.view_combo = Gtk.ComboBoxText()
        self.view_combo.append_text(tr("view_services"))
        self.view_combo.append_text(tr("view_others"))
        self.view_combo.append_text(tr("view_devices"))
        self.view_combo.set_active(0)
        f_box.pack_start(self.view_combo, False, False, 0)
        
        self.filter_combo = Gtk.ComboBoxText()
        self.filter_combo.append_text(tr("filter_all"))
        self.filter_combo.append_text(tr("filter_active"))
        self.filter_combo.append_text(tr("filter_inactive"))
        self.filter_combo.append_text(tr("filter_disabled"))
        self.filter_combo.append_text(tr("filter_masked"))
        self.filter_combo.set_active(0)
        f_box.pack_start(self.filter_combo, False, False, 0)
        
        self.tip_combo = Gtk.ComboBoxText()
        self.tip_combo.append_text(tr("tip_all"))
        self.tip_combo.append_text(tr("tip_critical"))
        self.tip_combo.append_text(tr("tip_suggestion"))
        self.tip_combo.append_text(tr("tip_required"))
        self.tip_combo.set_active(0)
        f_box.pack_start(self.tip_combo, False, False, 0)
        
        self.search_entry = Gtk.SearchEntry(placeholder_text=tr("search_placeholder"))
        f_box.pack_start(self.search_entry, True, True, 0)
        
        self.service_count_label = Gtk.Label(label=f"0 {tr('hizmet_sayisi')}")
        self.service_count_label.get_style_context().add_class("badge-slow")
        f_box.pack_start(self.service_count_label, False, False, 4)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        box.pack_start(scrolled, True, True, 0)
        
        from gi.repository import Pango
        
        self.liststore = Gtk.ListStore(str, str, str, str, str, str, str, str)
        
        # Define custom sort function for column 3 (Time column)
        def time_sort_func(model, iter1, iter2, user_data):
            val1 = model.get_value(iter1, 3)
            val2 = model.get_value(iter2, 3)
            
            def parse_to_ms(s):
                if not s or s == "--" or s == "":
                    return -1.0
                s = s.strip()
                try:
                    if s.endswith("ms"):
                        return float(s[:-2])
                    elif s.endswith("s"):
                        return float(s[:-1]) * 1000.0
                except ValueError:
                    pass
                return 0.0
                
            ms1 = parse_to_ms(val1)
            ms2 = parse_to_ms(val2)
            
            if ms1 < ms2:
                return -1
            elif ms1 > ms2:
                return 1
            return 0
            
        self.liststore.set_sort_func(3, time_sort_func)
        
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.set_rules_hint(True)
        scrolled.add(self.treeview)
        
        col_name = Gtk.TreeViewColumn(tr("hizmet_adi"))
        col_name.set_resizable(True)
        col_name.set_expand(True)
        col_name.set_min_width(220)
        col_name.set_sort_column_id(0)
        renderer_name = Gtk.CellRendererText()
        renderer_name.set_property("ellipsize", Pango.EllipsizeMode.END)
        col_name.pack_start(renderer_name, True)
        col_name.add_attribute(renderer_name, "text", 0)
        self.treeview.append_column(col_name)
        
        col_status = Gtk.TreeViewColumn(tr("durum"))
        col_status.set_resizable(True)
        col_status.set_min_width(110)
        col_status.set_expand(False)
        col_status.set_sort_column_id(7) # Sort by raw status string in column 7
        renderer_status = Gtk.CellRendererText()
        col_status.pack_start(renderer_status, True)
        col_status.add_attribute(renderer_status, "markup", 1)
        self.treeview.append_column(col_status)
        
        col_sub = Gtk.TreeViewColumn(tr("alt_durum"))
        col_sub.set_resizable(True)
        col_sub.set_min_width(110)
        col_sub.set_expand(False)
        col_sub.set_sort_column_id(2)
        renderer_sub = Gtk.CellRendererText()
        col_sub.pack_start(renderer_sub, True)
        col_sub.add_attribute(renderer_sub, "text", 2)
        self.treeview.append_column(col_sub)
        
        col_blame = Gtk.TreeViewColumn(tr("sure"))
        col_blame.set_resizable(True)
        col_blame.set_min_width(90)
        col_blame.set_expand(False)
        col_blame.set_sort_column_id(3)
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
        self.detail_name.set_markup(f"<b>{tr('hizmet_secilmedi')}</b>")
        self.detail_name.set_ellipsize(Pango.EllipsizeMode.END)
        v_detail_text.pack_start(self.detail_name, False, False, 0)
        
        self.detail_desc = Gtk.Label(xalign=0)
        self.detail_desc.set_text(tr("hizmet_secilmedi_desc"))
        self.detail_desc.set_line_wrap(True)
        v_detail_text.pack_start(self.detail_desc, False, False, 0)
        
        self.detail_suggestion = Gtk.Label(xalign=0)
        self.detail_suggestion.set_text("")
        self.detail_suggestion.set_line_wrap(True)
        v_detail_text.pack_start(self.detail_suggestion, False, False, 0)
        
        # Dikey ayırıcı çizgiler ve gruplandırılmış eylem kutuları
        sep1 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        h_detail.pack_start(sep1, False, False, 4)
        
        # 1. Açılış Ayarı Grubu
        v_boot_group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        v_boot_group.set_size_request(160, -1)
        h_detail.pack_start(v_boot_group, False, False, 0)
        
        lbl_boot_title = Gtk.Label()
        lbl_boot_title.set_markup(f"<span weight='bold' size='medium'>{tr('acilis_ayari')}</span>")
        v_boot_group.pack_start(lbl_boot_title, False, False, 0)
        
        self.btn_enable = Gtk.Button(label=tr("acilis_calistir"))
        v_boot_group.pack_start(self.btn_enable, False, False, 0)
        
        self.lbl_boot_state_status = Gtk.Label()
        self.lbl_boot_state_status.set_markup(f"<span size='small' color='#6c757d'>{tr('durum_bilinmiyor')}</span>")
        v_boot_group.pack_start(self.lbl_boot_state_status, False, False, 0)
        
        # Ayırıcı
        sep2 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        h_detail.pack_start(sep2, False, False, 4)
        
        # 2. Şimdiki Durum Grubu
        v_current_group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        v_current_group.set_size_request(160, -1)
        h_detail.pack_start(v_current_group, False, False, 0)
        
        lbl_current_title = Gtk.Label()
        lbl_current_title.set_markup(f"<span weight='bold' size='medium'>{tr('simdiki_durum')}</span>")
        v_current_group.pack_start(lbl_current_title, False, False, 0)
        
        self.btn_run = Gtk.Button(label=tr("simdi_baslat"))
        v_current_group.pack_start(self.btn_run, False, False, 0)
        
        self.lbl_current_state_status = Gtk.Label()
        self.lbl_current_state_status.set_markup(f"<span size='small' color='#6c757d'>{tr('durum_bilinmiyor')}</span>")
        v_current_group.pack_start(self.lbl_current_state_status, False, False, 0)
        
        # Ayırıcı
        sep3 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        h_detail.pack_start(sep3, False, False, 4)
        
        # 3. Diğer İşlemler Grubu
        v_utility_group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        v_utility_group.set_size_request(170, -1)
        h_detail.pack_start(v_utility_group, False, False, 0)
        
        lbl_utility_title = Gtk.Label()
        lbl_utility_title.set_markup(f"<span weight='bold' size='medium'>{tr('diger_islemler')}</span>")
        v_utility_group.pack_start(lbl_utility_title, False, False, 0)
        
        self.btn_mask = Gtk.Button(label=tr("maskele"))
        v_utility_group.pack_start(self.btn_mask, False, False, 0)
        
        h_bottom_actions1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        v_utility_group.pack_start(h_bottom_actions1, False, False, 0)
        
        self.btn_log = Gtk.Button(label=tr("gunluk_kaydi"))
        h_bottom_actions1.pack_start(self.btn_log, True, True, 0)
        
        self.btn_dep = Gtk.Button(label=tr("bagimliliklar"))
        h_bottom_actions1.pack_start(self.btn_dep, True, True, 0)
        
        self.btn_refresh = Gtk.Button(label=tr("yenile"))
        v_utility_group.pack_start(self.btn_refresh, False, False, 0)

        # En alta açıklayıcı İpucu/Bilgi Notu eklenmesi
        sep_help = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.detail_area.pack_start(sep_help, False, False, 2)
        
        h_help_note = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        h_help_note.set_margin_start(4)
        h_help_note.set_margin_end(4)
        self.detail_area.pack_start(h_help_note, False, False, 0)
        
        img_help = Gtk.Image.new_from_icon_name("dialog-information-symbolic", Gtk.IconSize.MENU)
        h_help_note.pack_start(img_help, False, False, 0)
        
        lbl_help = Gtk.Label(xalign=0)
        lbl_help.set_markup(
            f"<span size='small' style='italic' color='#555555'>{tr('bilgi_ipucu')}</span>"
        )
        lbl_help.set_line_wrap(True)
        h_help_note.pack_start(lbl_help, True, True, 0)
        
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
        self.detail_name.set_markup(f"<b>{tr('hizmet_secilmedi')}</b>")
        self.detail_desc.set_text(tr("hizmet_secilmedi_desc"))
        self.detail_suggestion.set_text("")
        self.service_count_label.set_text("0 " + tr("hizmet_sayisi"))
        self.set_status(tr("hizmetler_yukleniyor"))
        self.btn_enable.set_sensitive(False)
        self.btn_run.set_sensitive(False)
        self.btn_mask.set_sensitive(False)
        self.btn_log.set_sensitive(False)
        self.btn_dep.set_sensitive(False)
        self.lbl_boot_state_status.set_markup(f"<span size='small' color='#6c757d'>{tr('durum_bilinmiyor')}</span>")
        self.lbl_current_state_status.set_markup(f"<span size='small' color='#6c757d'>{tr('durum_bilinmiyor')}</span>")
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
        self.set_status(tr("hizmet_listesi_guncellendi"))
        return False

    def _update_count_label(self):
        view = VIEW_MAP.get(self.view_combo.get_active(), "services")
        n = len(self.liststore)
        t = len(self._all_data)
        self.service_count_label.set_text(f"{n} {tr('hizmet_sayisi')}" if n == t else f"{n}/{t} {tr('hizmet_sayisi')}")

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
            self.detail_name.set_markup(f"<b>{tr('hizmet_secilmedi')}</b>")
            self.detail_desc.set_text(tr("hizmet_secilmedi_desc"))
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
        self.detail_desc.set_text(r[4] or tr("aciklama_yok"))
        
        tip = r[5]
        oneri = r[6]
        if oneri:
            if tip == "kritik":
                self.detail_suggestion.set_markup(
                    f"<span foreground='#dc3545' weight='bold'>⚠ {tr('kritik_hizmet')}: </span>"
                    f"<span>{oneri}</span>"
                )
            elif tip == "oneri":
                self.detail_suggestion.set_markup(
                    f"<span foreground='#198754' weight='bold'>💡 {tr('kullanici_onerisi')}: </span>"
                    f"<span>{oneri}</span>"
                )
            else:
                self.detail_suggestion.set_markup(f"<b>{tr('oneri')}:</b> {oneri}")
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

        if enabled_state == "static":
            self.lbl_boot_state_status.set_markup(f"<span size='small' color='#6c757d'>● <b>{tr('statik_sabit')}</b></span>")
            self.btn_enable.set_label(tr("degistirilemez"))
            self.btn_enable.set_sensitive(False)
        elif enabled_state == "indirect":
            self.lbl_boot_state_status.set_markup(f"<span size='small' color='#6c757d'>● <b>{tr('dolayli_indirekt')}</b></span>")
            self.btn_enable.set_label(tr("degistirilemez"))
            self.btn_enable.set_sensitive(False)
        elif enabled_state == "masked":
            self.lbl_boot_state_status.set_markup(f"<span size='small' color='#6c757d'>🔒 <b>{tr('maskelenmis_kapali')}</b></span>")
            self.btn_enable.set_label(tr("degistirilemez"))
            self.btn_enable.set_sensitive(False)
        else:
            if is_enabled:
                self.btn_enable.set_label(tr("acilis_calistirma"))
                self.btn_enable.get_style_context().remove_class("success")
                self.btn_enable.get_style_context().add_class("danger")
                self.lbl_boot_state_status.set_markup(f"<span size='small' color='#198754'>● <b>{tr('acilis_calisacak')}</b></span>")
            else:
                self.btn_enable.set_label(tr("acilis_calistir"))
                self.btn_enable.get_style_context().remove_class("danger")
                self.btn_enable.get_style_context().add_class("success")
                self.lbl_boot_state_status.set_markup(f"<span size='small' color='#dc3545'>○ <b>{tr('acilis_calismayacak')}</b></span>")

        if is_running:
            self.btn_run.set_label(tr("simdi_durdur"))
            self.btn_run.get_style_context().remove_class("primary")
            self.btn_run.get_style_context().add_class("danger")
            self.lbl_current_state_status.set_markup(f"<span size='small' color='#198754'>● <b>{tr('su_an_calisiyor')}</b></span>")
        else:
            self.btn_run.set_label(tr("simdi_baslat"))
            self.btn_run.get_style_context().remove_class("danger")
            self.btn_run.get_style_context().add_class("primary")
            self.lbl_current_state_status.set_markup(f"<span size='small' color='#dc3545'>○ <b>{tr('su_an_durduruldu')}</b></span>")

        if active_state in ("activating", "deactivating"):
            self.lbl_current_state_status.set_markup(f"<span size='small' color='#ffc107'>⏳ <b>{tr('gecis_yapiyor')} ({active_state})</b></span>")
            self.btn_run.set_sensitive(False)

        if is_masked:
            self.btn_mask.set_label(tr("maskeyi_kaldir"))
            self.btn_mask.get_style_context().remove_class("danger")
            self.btn_mask.get_style_context().add_class("warning")
        else:
            self.btn_mask.set_label(tr("maskele"))
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
        is_running = d["active"] == "active"
        action = "disable" if is_enabled else "enable"
        
        if action == "disable":
            deps = self.manager.get_reverse_dependencies(name)
            if is_running:
                dlg = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.NONE,
                    message_format=tr("cift_yon_kapatma")
                )
                dlg.add_button(tr("ikisini_de_kapat"), 2)
                dlg.add_button(tr("sadece_baslangic_degistir"), 1)
                dlg.add_button(tr("iptal"), Gtk.ResponseType.CANCEL)
                
                sec_text = (
                    f"'{name}' hizmetinin açılışta otomatik başlamasını kapatıyorsunuz.\n"
                    "Bu hizmet şu an arka planda aktif/çalışır durumda.\n\n"
                    "Hem açılış ayarını kapatıp hem de çalışan süreci şimdi durdurmak ister misiniz?"
                )
                if deps:
                    dep_list_str = "\n".join(f"- {dep}" for dep in deps[:8])
                    if len(deps) > 8:
                        dep_list_str += f"\n- ve {len(deps) - 8} hizmet daha..."
                    sec_text += f"\n\n⚠️ DİKKAT: Bu hizmeti kapatmak, bağımlı çalışan şu hizmetleri etkileyebilir:\n{dep_list_str}"
                
                dlg.format_secondary_text(sec_text)
                resp = dlg.run()
                dlg.destroy()
                
                if resp == 2:
                    self._run_systemctl_batch(["disable", "stop"], name, self.load_all)
                elif resp == 1:
                    self._run_systemctl_batch(["disable"], name, self.load_all)
                else:
                    return
            else:
                if deps:
                    dlg = Gtk.MessageDialog(
                        parent=self.window, flags=Gtk.DialogFlags.MODAL,
                        type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.YES_NO,
                        message_format=f"'{name}' Hizmetini Açılışta Kapatmak İstiyor musunuz?"
                    )
                    dep_list_str = "\n".join(f"- {dep}" for dep in deps[:8])
                    if len(deps) > 8:
                        dep_list_str += f"\n- ve {len(deps) - 8} hizmet daha..."
                    dlg.format_secondary_text(
                        f"Bu hizmeti açılışta kapatmak, ona bağımlı şu hizmetleri etkileyebilir:\n\n{dep_list_str}\n\nDevam etmek istiyor musunuz?"
                    )
                    resp = dlg.run()
                    dlg.destroy()
                    if resp != Gtk.ResponseType.YES:
                        return
                self._run_systemctl("disable", name, self.load_all)
        else:
            if not is_running:
                dlg = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.NONE,
                    message_format=tr("cift_yon_etkinlestirme")
                )
                dlg.add_button(tr("simdi_baslat_ve_etkinlestir"), 2)
                dlg.add_button(tr("sadece_acilis_etkinlestir"), 1)
                dlg.add_button(tr("iptal"), Gtk.ResponseType.CANCEL)
                
                dlg.format_secondary_text(
                    f"'{name}' hizmetinin açılışta otomatik başlamasını etkinleştiriyorsunuz.\n"
                    "Bu hizmet şu an arka planda çalışmıyor.\n\n"
                    "Açılışta etkinleştirirken aynı zamanda şu anki oturumda hemen başlatmak ister misiniz?"
                )
                resp = dlg.run()
                dlg.destroy()
                
                if resp == 2:
                    self._run_systemctl_batch(["enable", "start"], name, self.load_all)
                elif resp == 1:
                    self._run_systemctl_batch(["enable"], name, self.load_all)
                else:
                    return
            else:
                self._run_systemctl("enable", name, self.load_all)

    def _on_service_run_clicked(self, button):
        name = self._get_selected_name()
        if not name:
            return
        d = self._all_data_map.get(name)
        if not d:
            return
        is_running = d["active"] == "active"
        action = "stop" if is_running else "start"
        
        # When stopping a service, suggest disabling it as well (Dual Action)
        if action == "stop":
            is_enabled = d.get("enabled", "unknown") in ("enabled", "enabled-runtime", "generated")
            if is_enabled:
                dlg = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.NONE,
                    message_format=tr("cift_yon_durdurma")
                )
                dlg.add_button(tr("ikisini_de_kapat"), 2)
                dlg.add_button(tr("sadece_simdi_durdur"), 1)
                dlg.add_button(tr("iptal"), Gtk.ResponseType.CANCEL)
                
                dlg.format_secondary_text(
                    f"'{name}' hizmetini şu anki oturumda durduruyorsunuz.\n"
                    "Bu hizmet başlangıçta otomatik çalışacak şekilde ayarlanmış.\n\n"
                    "Hem şu an durdurup hem de bir sonraki açılışlarda çalışmamasını (devre dışı bırakılmasını) ister misiniz?"
                )
                resp = dlg.run()
                dlg.destroy()
                
                if resp == 2:
                    self._run_systemctl_batch(["disable", "stop"], name, self.load_all)
                elif resp == 1:
                    self._run_systemctl_batch(["stop"], name, self.load_all)
                else:
                    return
            else:
                self._run_systemctl("stop", name, self.load_all)
        else:
            # Action is start
            is_enabled = d.get("enabled", "unknown") in ("enabled", "enabled-runtime", "generated")
            if not is_enabled and d.get("enabled") not in ("static", "indirect", "masked"):
                dlg = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.NONE,
                    message_format=tr("cift_yon_baslatma")
                )
                dlg.add_button(tr("simdi_baslat_ve_etkinlestir"), 2)
                dlg.add_button(tr("sadece_simdi_baslat"), 1)
                dlg.add_button(tr("iptal"), Gtk.ResponseType.CANCEL)
                
                dlg.format_secondary_text(
                    f"'{name}' hizmetini şu anki oturumda başlatıyorsunuz.\n"
                    "Bu hizmet başlangıçta otomatik çalışacak şekilde ayarlanmamış.\n\n"
                    "Hem şimdi başlatıp hem de sonraki açılışlarda otomatik başlamasını (etkinleştirilmesini) ister misiniz?"
                )
                resp = dlg.run()
                dlg.destroy()
                
                if resp == 2:
                    self._run_systemctl_batch(["enable", "start"], name, self.load_all)
                elif resp == 1:
                    self._run_systemctl_batch(["start"], name, self.load_all)
                else:
                    return
            else:
                self._run_systemctl("start", name, self.load_all)

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
            warn = tr("kritik_maske_uyarisi") if tip == "kritik" else ""
            
            dlg = Gtk.MessageDialog(
                parent=self.window, flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.WARNING if tip == "kritik" else Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                message_format=f"'{name}' " + tr("maske_sorusu")
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
            self.set_status(tr("yetki_iptal"))
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

    def _run_systemctl_batch(self, actions, name, cb):
        action_names_tr = {
            "enable": "Açılışta Etkinleştirme",
            "disable": "Açılışta Kapatma",
            "start": "Şimdi Başlatma",
            "stop": "Şimdi Durdurma",
            "mask": "Maskeleme",
            "unmask": "Maske Kaldırma"
        }
        
        if not self._ensure_auth():
            self.set_status(tr("yetki_iptal"))
            return
            
        actions_str = " ve ".join(action_names_tr.get(a, a) for a in actions)
        self.set_status(f"'{name}' için {actions_str} eylemleri başlatıldı...")
        
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
                
                success = True
                final_msg = ""
                for action in actions:
                    fn = m.get(action)
                    ok, msg = fn(name) if fn else (False, f"Bilinmeyen eylem: {action}")
                    if not ok:
                        success = False
                        final_msg += f"[{action_names_tr.get(action, action)} Hatası: {msg}] "
                    else:
                        final_msg += f"[{action_names_tr.get(action, action)} başarılı] "
                
                GLib.idle_add(self._on_cmd_done, success, final_msg.strip(), cb)
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
                out = log.strip() if log else ""
                if not out or "-- no entries --" in out.lower() or "permission" in out.lower():
                    if self.manager.password is None:
                        GLib.idle_add(prompt_auth)
                        return
                    else:
                        log = tr("log_bulunamadi")
                GLib.idle_add(buf.set_text, log)
            except Exception as e:
                GLib.idle_add(buf.set_text, f"Hata: {e}")
                
        def prompt_auth():
            buf.set_text(tr("hata_log_yetki"))
            if self._ensure_auth():
                buf.set_text(tr("yetkilendirildi"))
                threading.Thread(target=task, daemon=True).start()
            else:
                buf.set_text(
                    "Logları okuma yetkiniz bulunmuyor.\n\n"
                    "Logları görüntülemek için yönetici şifrenizi girmeniz gerekmektedir."
                )
                
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
        lbl_title.set_text(tr("profiller_title"))
        lbl_title.get_style_context().add_class("content-title")
        box.pack_start(lbl_title, False, False, 0)
        
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_text(tr("profiller_subtitle"))
        lbl_sub.get_style_context().add_class("content-subtitle")
        box.pack_start(lbl_sub, False, False, 0)
        
        grid = Gtk.Grid(column_spacing=16, row_spacing=16)
        box.pack_start(grid, False, False, 0)
        
        self.profiles_data = {}
        for p_id, p_info in _config_data.get("profiles", {}).items():
            self.profiles_data[p_id] = {
                "name": tr(p_info["name_tr_key"]),
                "icon": p_info["icon"],
                "desc": tr(p_info["desc_tr_key"]),
                "services": p_info["services"]
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
                lbl_saving.set_markup(f"<span foreground='#2ec27e'><b>{tr('tahmini_kazanc')}: ~{savings:.1f}s</b></span>")
            else:
                lbl_saving.set_markup(f"<span foreground='#888888'>{tr('tahmini_kazanc')}: &lt; 0.1s</span>")
            lbl_saving.set_margin_bottom(4)
            card.pack_start(lbl_saving, False, False, 0)
            
            btn_apply = Gtk.Button(label=tr("profili_uygula"))
            btn_apply.get_style_context().add_class("primary")
            btn_apply.connect("clicked", self._on_apply_profile_clicked, p_id)
            card.pack_start(btn_apply, False, False, 0)
            
            grid.attach(card, col, 0, 1, 1)
            col += 1
            
        lbl_custom_title = Gtk.Label(xalign=0)
        lbl_custom_title.set_text(tr("kullanici_ozel_profilleri"))
        lbl_custom_title.get_style_context().add_class("card-title")
        lbl_custom_title.set_margin_top(16)
        box.pack_start(lbl_custom_title, False, False, 8)
        
        h_custom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.pack_start(h_custom_bar, False, False, 0)
        
        btn_save_curr = Gtk.Button(label=tr("mevcut_durumu_kaydet"))
        btn_save_curr.get_style_context().add_class("success")
        btn_save_curr.connect("clicked", self._on_save_custom_profile_clicked)
        h_custom_bar.pack_start(btn_save_curr, False, False, 0)
        
        btn_create_custom = Gtk.Button(label=tr("yeni_ozel_profil_btn"))
        btn_create_custom.get_style_context().add_class("primary")
        btn_create_custom.connect("clicked", self._on_create_custom_profile_clicked)
        h_custom_bar.pack_start(btn_create_custom, False, False, 0)
        
        self.custom_profiles_listbox = Gtk.ListBox()
        self.custom_profiles_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        box.pack_start(self.custom_profiles_listbox, False, False, 0)
        
        # Geri Yükleme Noktaları (Yedekler)
        lbl_backup_title = Gtk.Label(xalign=0)
        lbl_backup_title.set_text(tr("sistem_geri_yukleme_noktalari"))
        lbl_backup_title.get_style_context().add_class("card-title")
        lbl_backup_title.set_margin_top(24)
        box.pack_start(lbl_backup_title, False, False, 8)
        
        h_backup_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.pack_start(h_backup_bar, False, False, 0)
        
        btn_create_backup = Gtk.Button(label=tr("yeni_yedek_noktasi_btn"))
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
            lbl.set_markup(f"<span foreground='#888888'>{tr('no_custom_profiles')}</span>")
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
                    lbl_desc.set_markup(f"<span size='small' foreground='#666666'>{count} {tr('hizmet_kurali')}</span>")
                    v_box.pack_start(lbl_desc, False, False, 0)
                    
                    h_box.pack_start(v_box, True, True, 0)
                    
                    btn_apply = Gtk.Button(label=tr("uygula"))
                    btn_apply.set_valign(Gtk.Align.CENTER)
                    btn_apply.get_style_context().add_class("primary")
                    btn_apply.connect("clicked", self._on_apply_custom_profile_clicked, fpath)
                    h_box.pack_start(btn_apply, False, False, 6)
                    
                    btn_del = Gtk.Button()
                    btn_del.set_valign(Gtk.Align.CENTER)
                    img_del = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
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
            lbl.set_markup(f"<span foreground='#888888'>{tr('no_backups_found')}</span>")
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
                lbl_desc.set_markup(f"<span size='small' foreground='#666666'>{count} {tr('hizmetin_yedegi')}</span>")
                v_box.pack_start(lbl_desc, False, False, 0)
                
                h_box.pack_start(v_box, True, True, 0)
                
                btn_restore = Gtk.Button(label=tr("geri_yukle"))
                btn_restore.set_valign(Gtk.Align.CENTER)
                btn_restore.get_style_context().add_class("warning")
                btn_restore.connect("clicked", self._on_restore_backup_clicked, fpath)
                h_box.pack_start(btn_restore, False, False, 6)
                
                btn_del = Gtk.Button()
                btn_del.set_valign(Gtk.Align.CENTER)
                img_del = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
                btn_del.set_image(img_del)
                btn_del.get_style_context().add_class("danger")
                btn_del.connect("clicked", self._on_delete_backup_clicked, fpath)
                h_box.pack_start(btn_del, False, False, 0)
                
                self.backups_listbox.add(row)
        self.backups_listbox.show_all()

    def _on_create_backup_clicked(self, button):
        ok, msg = self.manager.create_backup()
        if ok:
            self.set_status(tr("yedek_olusturuldu"))
            self.load_profiles_page()
        else:
            self.set_status(f"{tr('hata')}: {msg}")

    def _on_restore_backup_clicked(self, button, fpath):
        dlg = Gtk.MessageDialog(
            parent=self.window, flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO,
            message_format=tr("yedek_don_soru")
        )
        dlg.format_secondary_text(tr("yedek_don_aciklama"))
        resp = dlg.run()
        dlg.destroy()
        if resp != Gtk.ResponseType.YES:
            return
            
        if not self._ensure_auth():
            self.set_status(tr("yetki_iptal"))
            return
            
        loader = Gtk.Dialog(title=tr("yedek_geri_yukleniyor"), parent=self.window, flags=Gtk.DialogFlags.MODAL)
        loader.set_default_size(320, 140)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(18)
        box.set_margin_end(18)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        loader.get_content_area().add(box)
        
        lbl = Gtk.Label(label=tr("yedek_yukleniyor_bekleyin"))
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
            message_format=tr("yedek_sil_soru")
        )
        resp = dlg.run()
        dlg.destroy()
        if resp == Gtk.ResponseType.YES:
            try:
                os.remove(fpath)
                self.set_status(tr("yedek_noktasi_silindi"))
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
            message_format=f"'{p_info['name']}' " + tr("profil_uygula_soru")
        )
        dlg.format_secondary_text(tr("profil_uygula_aciklama"))
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
            self.set_status(tr("sistem_uygun_durumda"))
            info = Gtk.MessageDialog(
                parent=self.window, flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK,
                message_format=tr("profil_zaten_uygulanmis")
            )
            info.format_secondary_text(tr("hizmetler_uygun_detay"))
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
            dep_msg = tr("profil_uygula_bagimlilik_mesaji")
            for parent, kids in list(all_deps.items())[:5]:
                dep_msg += f"• {parent} ➔ {', '.join(kids[:3])}\n"
            if len(all_deps) > 5:
                dep_msg += tr("ve_daha_fazla_hizmet").format(len(all_deps) - 5)
                
            dep_dlg = Gtk.MessageDialog(
                parent=self.window, flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.YES_NO,
                message_format=tr("profil_bagimlilik_uyarisi")
            )
            dep_dlg.format_secondary_text(dep_msg + "\nDevam etmek istiyor musunuz?")
            dep_resp = dep_dlg.run()
            dep_dlg.destroy()
            if dep_resp != Gtk.ResponseType.YES:
                return
            
        if not self._ensure_auth():
            self.set_status(tr("yetki_iptal"))
            return
            
        self._run_profile_batch(enable_list, disable_list)

    def _on_apply_custom_profile_clicked(self, button, fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                p_info = json.load(f)
        except Exception as e:
            self.set_status(f"{tr('profil_okuma_hatasi')}{e}")
            return
            
        dlg = Gtk.MessageDialog(
            parent=self.window, flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            message_format=f"'{p_info['name']}' " + tr("profil_uygula_soru")
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
            self.set_status(tr("sistem_uygun_durumda"))
            return
            
        all_deps = {}
        for svc in disable_list:
            deps = self.manager.get_reverse_dependencies(svc)
            filtered_deps = [d for d in deps if d not in disable_list]
            if filtered_deps:
                all_deps[svc] = filtered_deps

        if all_deps:
            dep_msg = tr("profil_uygula_bagimlilik_mesaji")
            for parent, kids in list(all_deps.items())[:5]:
                dep_msg += f"• {parent} ➔ {', '.join(kids[:3])}\n"
            if len(all_deps) > 5:
                dep_msg += tr("ve_daha_fazla_hizmet").format(len(all_deps) - 5)
                
            dep_dlg = Gtk.MessageDialog(
                parent=self.window, flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.YES_NO,
                message_format=tr("profil_bagimlilik_uyarisi")
            )
            dep_dlg.format_secondary_text(dep_msg + "\nDevam etmek istiyor musunuz?")
            dep_resp = dep_dlg.run()
            dep_dlg.destroy()
            if dep_resp != Gtk.ResponseType.YES:
                return
            
        if not self._ensure_auth():
            self.set_status(tr("yetki_iptal"))
            return
            
        self._run_profile_batch(enable_list, disable_list)

    def _run_profile_batch(self, enable_list, disable_list):
        loader = Gtk.Dialog(title=tr("profil_uygulaniyor"), parent=self.window, flags=Gtk.DialogFlags.MODAL)
        loader.set_default_size(320, 140)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(18)
        box.set_margin_end(18)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        loader.get_content_area().add(box)
        
        lbl = Gtk.Label(label=tr("profil_uygulaniyor_bekleyin"))
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
                    message_format=tr("profil_basariyla_uygulandi")
                )
                info.run()
                info.destroy()
                self.load_all()
            else:
                err = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
                    message_format=tr("profil_uygulama_hatasi"),
                )
                err.format_secondary_text(msg)
                err.run()
                err.destroy()
                
        threading.Thread(target=task, daemon=True).start()

    def _on_save_custom_profile_clicked(self, button):
        dialog = Gtk.Dialog(title=tr("profili_kaydet_title"), parent=self.window, flags=Gtk.DialogFlags.MODAL)
        dialog.add_button(tr("iptal"), Gtk.ResponseType.CANCEL)
        btn_save = dialog.add_button(tr("kaydet"), Gtk.ResponseType.OK)
        btn_save.get_style_context().add_class("primary")
        
        content = dialog.get_content_area()
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.pack_start(vbox, True, True, 0)
        
        lbl = Gtk.Label(label=tr("yeni_profil_adi_girin"), xalign=0)
        vbox.pack_start(lbl, False, False, 0)
        
        entry = Gtk.Entry()
        entry.set_text(tr("ozel_profilim"))
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
            self.set_status(f"'{p_name}' " + tr("profili_kaydedildi"))
            self.load_profiles_page()
        except Exception as e:
            self.set_status(f"{tr('kaydetme_hatasi')}{e}")

    def _on_delete_custom_profile_clicked(self, button, fpath):
        try:
            if os.path.exists(fpath):
                os.remove(fpath)
                self.set_status(tr("ozel_profil_silindi"))
                self.load_profiles_page()
        except Exception as e:
            self.set_status(f"{tr('silme_hatasi')}{e}")

    def _on_create_custom_profile_clicked(self, button):
        dlg = ProfileCreatorDialog(self.window)
        response = dlg.run()
        
        if response == Gtk.ResponseType.OK:
            data, err = dlg.get_profile_data()
            dlg.hide()
            GLib.idle_add(dlg.destroy)
            
            if err:
                self.set_status(f"{tr('hata')}: {err}")
                return
                
            p_dir = self.get_custom_profiles_dir()
            clean_name = "".join(c for c in data["name"] if c.isalnum() or c in (" ", "_", "-")).rstrip()
            filename = clean_name.replace(" ", "_").lower() + ".json"
            fpath = os.path.join(p_dir, filename)
            
            try:
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                self.set_status(f"{tr('ozel_profil_olusturuldu')}".format(data['name']))
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
            self.analiz_page.load_analysis_page()
        elif idx == 1:
            self.stack.set_visible_child_name("autostart")
            self.autostart_page.load_autostart_page()
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

