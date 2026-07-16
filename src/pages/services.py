import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import threading

from src.locale_mgr import tr
from src.service_db import get_description
from src.utils import (
    STATUS_COLORS, STATUS_TR, FILTER_MAP, TIP_MAP, VIEW_MAP,
    parse_blame_time, make_status_markup
)

class ServicesPage:
    def __init__(self, controller):
        self.controller = controller
        self.window = controller.window
        self.manager = controller.manager
        self.set_status = controller.set_status
        self._ensure_auth = controller._ensure_auth
        
        # Initialize state variables
        self._status_filter = "all"
        self._tip_filter = "all"
        self._search_text = ""
        self._updating_widgets = False
        self._all_data = []
        self._all_data_map = {}
        self._debounce_id = None

    def build_page_services(self):
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
        
        self.service_count_label = Gtk.Label(label=f"0 {tr('service_count')}")
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
        
        col_name = Gtk.TreeViewColumn(tr("service_name"))
        col_name.set_resizable(True)
        col_name.set_expand(True)
        col_name.set_min_width(220)
        col_name.set_sort_column_id(0)
        renderer_name = Gtk.CellRendererText()
        renderer_name.set_property("ellipsize", Pango.EllipsizeMode.END)
        col_name.pack_start(renderer_name, True)
        col_name.add_attribute(renderer_name, "text", 0)
        self.treeview.append_column(col_name)
        
        col_status = Gtk.TreeViewColumn(tr("state"))
        col_status.set_resizable(True)
        col_status.set_min_width(110)
        col_status.set_expand(False)
        col_status.set_sort_column_id(7) # Sort by raw status string in column 7
        renderer_status = Gtk.CellRendererText()
        col_status.pack_start(renderer_status, True)
        col_status.add_attribute(renderer_status, "markup", 1)
        self.treeview.append_column(col_status)
        
        col_sub = Gtk.TreeViewColumn(tr("sub_state"))
        col_sub.set_resizable(True)
        col_sub.set_min_width(110)
        col_sub.set_expand(False)
        col_sub.set_sort_column_id(2)
        renderer_sub = Gtk.CellRendererText()
        col_sub.pack_start(renderer_sub, True)
        col_sub.add_attribute(renderer_sub, "text", 2)
        self.treeview.append_column(col_sub)
        
        col_blame = Gtk.TreeViewColumn(tr("time"))
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
        self.detail_name.set_markup(f"<b>{tr('service_secilmedi')}</b>")
        self.detail_name.set_ellipsize(Pango.EllipsizeMode.END)
        v_detail_text.pack_start(self.detail_name, False, False, 0)
        
        self.detail_desc = Gtk.Label(xalign=0)
        self.detail_desc.set_text(tr("service_secilmedi_desc"))
        self.detail_desc.set_line_wrap(True)
        v_detail_text.pack_start(self.detail_desc, False, False, 0)
        
        self.detail_suggestion = Gtk.Label(xalign=0)
        self.detail_suggestion.set_text("")
        self.detail_suggestion.set_line_wrap(True)
        v_detail_text.pack_start(self.detail_suggestion, False, False, 0)
        
        # Vertical separators and grouped action boxes
        sep1 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        h_detail.pack_start(sep1, False, False, 4)
        
        # 1. Boot Configuration Group
        v_boot_group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        v_boot_group.set_size_request(160, -1)
        h_detail.pack_start(v_boot_group, False, False, 0)
        
        lbl_boot_title = Gtk.Label()
        lbl_boot_title.set_markup(f"<span weight='bold' size='medium'>{tr('boot_ayari')}</span>")
        v_boot_group.pack_start(lbl_boot_title, False, False, 0)
        
        self.btn_enable = Gtk.Button(label=tr("boot_calistir"))
        v_boot_group.pack_start(self.btn_enable, False, False, 0)
        
        self.lbl_boot_state_status = Gtk.Label()
        self.lbl_boot_state_status.set_markup(f"<span size='small' color='#6c757d'>{tr('state_bilinmiyor')}</span>")
        v_boot_group.pack_start(self.lbl_boot_state_status, False, False, 0)
        
        # Separator
        sep2 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        h_detail.pack_start(sep2, False, False, 4)
        
        # 2. Current State Group
        v_current_group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        v_current_group.set_size_request(160, -1)
        h_detail.pack_start(v_current_group, False, False, 0)
        
        lbl_current_title = Gtk.Label()
        lbl_current_title.set_markup(f"<span weight='bold' size='medium'>{tr('simdiki_state')}</span>")
        v_current_group.pack_start(lbl_current_title, False, False, 0)
        
        self.btn_run = Gtk.Button(label=tr("simdi_start"))
        v_current_group.pack_start(self.btn_run, False, False, 0)
        
        self.lbl_current_state_status = Gtk.Label()
        self.lbl_current_state_status.set_markup(f"<span size='small' color='#6c757d'>{tr('state_bilinmiyor')}</span>")
        v_current_group.pack_start(self.lbl_current_state_status, False, False, 0)
        
        # Separator
        sep3 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        h_detail.pack_start(sep3, False, False, 4)
        
        # 3. Other Operations Group
        v_utility_group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        v_utility_group.set_size_request(170, -1)
        h_detail.pack_start(v_utility_group, False, False, 0)
        
        lbl_utility_title = Gtk.Label()
        lbl_utility_title.set_markup(f"<span weight='bold' size='medium'>{tr('other_islemler')}</span>")
        v_utility_group.pack_start(lbl_utility_title, False, False, 0)
        
        self.btn_mask = Gtk.Button(label=tr("maskele"))
        v_utility_group.pack_start(self.btn_mask, False, False, 0)
        
        h_bottom_actions1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        v_utility_group.pack_start(h_bottom_actions1, False, False, 0)
        
        self.btn_log = Gtk.Button(label=tr("gunluk_kaydi"))
        h_bottom_actions1.pack_start(self.btn_log, True, True, 0)
        
        self.btn_dep = Gtk.Button(label=tr("bagimliliklar"))
        h_bottom_actions1.pack_start(self.btn_dep, True, True, 0)
        
        self.btn_refresh = Gtk.Button(label=tr("refresh"))
        v_utility_group.pack_start(self.btn_refresh, False, False, 0)

        # Add explanatory tip/info note to the bottom
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
            f"<span size='small' style='italic' color='#555555'>{tr('info_tip')}</span>"
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
        self.detail_name.set_markup(f"<b>{tr('service_secilmedi')}</b>")
        self.detail_desc.set_text(tr("service_secilmedi_desc"))
        self.detail_suggestion.set_text("")
        self.service_count_label.set_text("0 " + tr("service_count"))
        self.set_status(tr("hizmetler_yukleniyor"))
        self.btn_enable.set_sensitive(False)
        self.btn_run.set_sensitive(False)
        self.btn_mask.set_sensitive(False)
        self.btn_log.set_sensitive(False)
        self.btn_dep.set_sensitive(False)
        self.lbl_boot_state_status.set_markup(f"<span size='small' color='#6c757d'>{tr('state_bilinmiyor')}</span>")
        self.lbl_current_state_status.set_markup(f"<span size='small' color='#6c757d'>{tr('state_bilinmiyor')}</span>")
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
            self.set_status(f"{tr('yukleme_hatasi')}{str(e)}")
            self.service_count_label.set_text(tr("error"))
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
                "suggestion": oneri or "",
            })

        self._all_data.sort(key=lambda x: (-x["seconds"], x["name"]))
        self._all_data_map = {d["name"]: d for d in self._all_data}
        self._apply_filters()
        self.set_status(tr("service_listesi_guncellendi"))
        return False

    def _update_count_label(self):
        view = VIEW_MAP.get(self.view_combo.get_active(), "services")
        n = len(self.liststore)
        t = len(self._all_data)
        self.service_count_label.set_text(f"{n} {tr('service_count')}" if n == t else f"{n}/{t} {tr('service_count')}")

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
                d["suggestion"],
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
            self.detail_name.set_markup(f"<b>{tr('service_secilmedi')}</b>")
            self.detail_desc.set_text(tr("service_secilmedi_desc"))
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
        self.detail_desc.set_text(r[4] or tr("description_none"))
        
        tip = r[5]
        oneri = r[6]
        if oneri:
            if tip == "kritik":
                self.detail_suggestion.set_markup(
                    f"<span foreground='#e01b24' weight='bold'>⚠ {tr('critical_service')}: </span>"
                    f"<span>{oneri}</span>"
                )
            elif tip == "suggestion":
                self.detail_suggestion.set_markup(
                    f"<span foreground='#2ec27e' weight='bold'>💡 {tr('user_onerisi')}: </span>"
                    f"<span>{oneri}</span>"
                )
            else:
                self.detail_suggestion.set_markup(f"<b>{tr('suggestion')}:</b> {oneri}")
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
                self.btn_enable.set_label(tr("boot_calistirma"))
                self.btn_enable.get_style_context().remove_class("success")
                self.btn_enable.get_style_context().add_class("danger")
                self.lbl_boot_state_status.set_markup(f"<span size='small' color='#198754'>● <b>{tr('boot_calisacak')}</b></span>")
            else:
                self.btn_enable.set_label(tr("boot_calistir"))
                self.btn_enable.get_style_context().remove_class("danger")
                self.btn_enable.get_style_context().add_class("success")
                self.lbl_boot_state_status.set_markup(f"<span size='small' color='#dc3545'>○ <b>{tr('boot_calismayacak')}</b></span>")

        if is_running:
            self.btn_run.set_label(tr("simdi_stop"))
            self.btn_run.get_style_context().remove_class("suggested-action")
            self.btn_run.get_style_context().add_class("danger")
            self.lbl_current_state_status.set_markup(f"<span size='small' color='#198754'>● <b>{tr('su_an_calisiyor')}</b></span>")
        else:
            self.btn_run.set_label(tr("simdi_start"))
            self.btn_run.get_style_context().remove_class("danger")
            self.btn_run.get_style_context().add_class("suggested-action")
            self.lbl_current_state_status.set_markup(f"<span size='small' color='#dc3545'>○ <b>{tr('su_an_durduruldu')}</b></span>")

        if active_state in ("activating", "deactivating"):
            self.lbl_current_state_status.set_markup(f"<span size='small' color='#ffc107'>⏳ <b>{tr('gecis_yapiyor')} ({active_state})</b></span>")
            self.btn_run.set_sensitive(False)

        if is_masked:
            self.btn_mask.set_label(tr("maskeyi_remove"))
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
                    message_format=tr("double_way_kapatma")
                )
                dlg.add_button(tr("ikisini_de_disable"), 2)
                dlg.add_button(tr("sadece_startup_degistir"), 1)
                dlg.add_button(tr("cancel"), Gtk.ResponseType.CANCEL)
                
                sec_text = tr("disable_boot_running_select").format(name)
                if deps:
                    dep_list_str = "\n".join(f"- {dep}" for dep in deps[:8])
                    if len(deps) > 8:
                        dep_list_str += f"\n- {tr('ve_daha_fazla_service').format(len(deps) - 8).strip()}"
                    sec_text += "\n\n" + tr("action_dep_uyari").format(dep_list_str)
                
                dlg.format_secondary_text(sec_text)
                
                self._add_command_expander(dlg, [
                    (tr("ikisini_de_disable"), [f"disable {name}", f"stop {name}"]),
                    (tr("sadece_startup_degistir"), [f"disable {name}"])
                ])
                
                resp = dlg.run()
                dlg.hide()
                GLib.idle_add(dlg.destroy)
                
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
                        type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.NONE,
                        message_format=tr("disable_boot_stopped_title").format(name)
                    )
                    dlg.add_button(tr("no"), Gtk.ResponseType.NO)
                    dlg.add_button(tr("yes"), Gtk.ResponseType.YES)
                    dep_list_str = "\n".join(f"- {dep}" for dep in deps[:8])
                    if len(deps) > 8:
                        dep_list_str += f"\n- {tr('ve_daha_fazla_service').format(len(deps) - 8).strip()}"
                    dlg.format_secondary_text(
                        tr("disable_boot_stopped_dep").format(name, dep_list_str)
                    )
                    
                    self._add_command_expander(dlg, [
                        (tr("yes"), [f"disable {name}"])
                    ])
                    
                    resp = dlg.run()
                    dlg.hide()
                    GLib.idle_add(dlg.destroy)
                    if resp != Gtk.ResponseType.YES:
                        return
                self._run_systemctl("disable", name, self.load_all)
        else:
            if not is_running:
                dlg = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.NONE,
                    message_format=tr("double_way_etkinlestirme")
                )
                dlg.add_button(tr("simdi_start_ve_etkinlestir"), 2)
                dlg.add_button(tr("sadece_boot_etkinlestir"), 1)
                dlg.add_button(tr("cancel"), Gtk.ResponseType.CANCEL)
                
                dlg.format_secondary_text(
                    tr("enable_boot_stopped_select").format(name)
                )
                
                self._add_command_expander(dlg, [
                    (tr("simdi_start_ve_etkinlestir"), [f"enable {name}", f"start {name}"]),
                    (tr("sadece_boot_etkinlestir"), [f"enable {name}"])
                ])
                
                resp = dlg.run()
                dlg.hide()
                GLib.idle_add(dlg.destroy)
                
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
                    message_format=tr("double_way_durdurma")
                )
                dlg.add_button(tr("ikisini_de_disable"), 2)
                dlg.add_button(tr("sadece_simdi_stop"), 1)
                dlg.add_button(tr("cancel"), Gtk.ResponseType.CANCEL)
                
                dlg.format_secondary_text(
                    tr("stop_enabled_select").format(name)
                )
                
                self._add_command_expander(dlg, [
                    (tr("ikisini_de_disable"), [f"disable {name}", f"stop {name}"]),
                    (tr("sadece_simdi_stop"), [f"stop {name}"])
                ])
                
                resp = dlg.run()
                dlg.hide()
                GLib.idle_add(dlg.destroy)
                
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
                    message_format=tr("double_way_baslatma")
                )
                dlg.add_button(tr("simdi_start_ve_etkinlestir"), 2)
                dlg.add_button(tr("sadece_simdi_start"), 1)
                dlg.add_button(tr("cancel"), Gtk.ResponseType.CANCEL)
                
                dlg.format_secondary_text(
                    tr("start_disabled_select").format(name)
                )
                
                self._add_command_expander(dlg, [
                    (tr("simdi_start_ve_etkinlestir"), [f"enable {name}", f"start {name}"]),
                    (tr("sadece_simdi_start"), [f"start {name}"])
                ])
                
                resp = dlg.run()
                dlg.hide()
                GLib.idle_add(dlg.destroy)
                
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
            warn = tr("critical_maske_uyarisi") if tip == "kritik" else ""
            
            dlg = Gtk.MessageDialog(
                parent=self.window, flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.WARNING if tip == "kritik" else Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE,
                message_format=f"'{name}' " + tr("maske_sorusu")
            )
            dlg.add_button(tr("no"), Gtk.ResponseType.NO)
            dlg.add_button(tr("yes"), Gtk.ResponseType.YES)
            if warn:
                dlg.format_secondary_text(warn)
                
            self._add_command_expander(dlg, [
                (tr("action_maskele"), [f"mask {name}"])
            ])
            
            resp = dlg.run()
            dlg.hide()
            GLib.idle_add(dlg.destroy)
            if resp != Gtk.ResponseType.YES:
                return

        self._run_systemctl(action, name, self.load_all)

    def _run_systemctl(self, action, name, cb):
        action_map = {
            "enable": tr("action_boot_ac"),
            "disable": tr("action_boot_disable"),
            "start": tr("action_simdi_start"),
            "stop": tr("action_simdi_stop"),
            "mask": tr("action_maskele"),
            "unmask": tr("action_maskeyi_remove")
        }
        action_tr = action_map.get(action, action)
                     
        if not self._ensure_auth():
            self.set_status(tr("auth_cancel"))
            return
            
        self.set_status(tr("action_baslatildi").format(name, action_tr))
        
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
                if fn:
                    ok, msg = fn(name)
                else:
                    ok, msg = False, tr("action_bilinmiyor").format(action)
                GLib.idle_add(self._on_cmd_done, ok, msg, cb)
            except Exception as e:
                GLib.idle_add(self._on_cmd_done, False, str(e), cb)
                
        threading.Thread(target=task, daemon=True).start()

    def _run_systemctl_batch(self, actions, name, cb):
        action_map = {
            "enable": tr("action_boot_ac"),
            "disable": tr("action_boot_disable"),
            "start": tr("action_simdi_start"),
            "stop": tr("action_simdi_stop"),
            "mask": tr("action_maskele"),
            "unmask": tr("action_maskeyi_remove")
        }
        
        if not self._ensure_auth():
            self.set_status(tr("auth_cancel"))
            return
            
        actions_str = " + ".join(action_map.get(a, a) for a in actions)
        self.set_status(tr("action_batch_baslatildi").format(name, actions_str))
        
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
                    aname = action_map.get(action, action)
                    if fn:
                        ok, msg = fn(name)
                    else:
                        ok, msg = False, tr("action_bilinmiyor").format(action)
                    if not ok:
                        success = False
                        final_msg += tr("action_error").format(aname, msg) + " "
                    else:
                        final_msg += tr("action_basarili").format(aname) + " "
                
                GLib.idle_add(self._on_cmd_done, success, final_msg.strip(), cb)
            except Exception as e:
                GLib.idle_add(self._on_cmd_done, False, str(e), cb)
                
        threading.Thread(target=task, daemon=True).start()

    def _on_cmd_done(self, ok, msg, cb):
        try:
            self.set_status(msg or "")
            if ok and cb:
                cb()
        except Exception:
            pass

    def _add_command_expander(self, dialog, options):
        expander = Gtk.Expander(label=tr("calistirilacak_komutlar"))
        expander.set_margin_start(12)
        expander.set_margin_end(12)
        expander.set_margin_bottom(12)
        
        cmd_lines = []
        for group_title, cmds in options:
            if len(options) > 1:
                cmd_lines.append(f"<b>• {group_title}:</b>")
                prefix = "  "
            else:
                prefix = ""
            for cmd in cmds:
                cmd_lines.append(f"{prefix}sudo systemctl {cmd}")
            if len(options) > 1:
                cmd_lines.append("")
        
        cmd_text = "\n".join(cmd_lines).strip()
        
        lbl_cmd = Gtk.Label()
        lbl_cmd.set_markup(f"<span font_family='monospace' size='small'>{cmd_text}</span>")
        lbl_cmd.set_selectable(True)
        lbl_cmd.set_xalign(0)
        lbl_cmd.set_margin_top(8)
        lbl_cmd.set_margin_bottom(8)
        lbl_cmd.set_margin_start(8)
        lbl_cmd.set_margin_end(8)
        
        frame = Gtk.Frame()
        frame.get_style_context().add_class("monospaced-log")
        frame.add(lbl_cmd)
        
        expander.add(frame)
        
        content_area = dialog.get_content_area()
        content_area.pack_end(expander, False, False, 0)
        expander.show_all()


    def _on_show_log(self, *args):
        n = self._get_selected_name()
        if not n:
            self.set_status(tr("select_service_first"))
            return
            
        dialog = Gtk.Dialog(title=tr("log_dialog_title").format(n), parent=self.window, flags=Gtk.DialogFlags.MODAL)
        dialog.set_default_size(750, 480)
        dialog.add_button(tr("dialog_close"), Gtk.ResponseType.CLOSE)
        
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
        buf.set_text(tr("log_loading"))
        
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
                        log = tr("log_not_found")
                GLib.idle_add(buf.set_text, log)
            except Exception as e:
                GLib.idle_add(buf.set_text, tr("log_error").format(e))
                
        def prompt_auth():
            buf.set_text(tr("error_log_auth"))
            if self._ensure_auth():
                buf.set_text(tr("yetkilendirildi"))
                threading.Thread(target=task, daemon=True).start()
            else:
                buf.set_text(tr("log_no_perm"))
                
        threading.Thread(target=task, daemon=True).start()
        
        dialog.run()
        dialog.destroy()

    # --- Dependency Viewer ---
    def _on_show_dependencies(self, button):
        n = self._get_selected_name()
        if not n:
            self.set_status(tr("select_service_first"))
            return
            
        dialog = Gtk.Dialog(title=tr("dep_dialog_title").format(n), parent=self.window, flags=Gtk.DialogFlags.MODAL)
        dialog.set_default_size(550, 450)
        dialog.add_button(tr("dialog_close"), Gtk.ResponseType.CLOSE)
        
        content = dialog.get_content_area()
        content.set_margin_start(10)
        content.set_margin_end(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        
        lbl_info = Gtk.Label(xalign=0)
        lbl_info.set_markup(tr("dep_info_lbl").format(n))
        content.pack_start(lbl_info, False, False, 6)
        
        scrolled = Gtk.ScrolledWindow()
        content.pack_start(scrolled, True, True, 0)
        
        txt_view = Gtk.TextView()
        txt_view.set_editable(False)
        txt_view.set_cursor_visible(False)
        txt_view.get_style_context().add_class("monospaced-log")
        scrolled.add(txt_view)
        
        buf = txt_view.get_buffer()
        buf.set_text(tr("dep_loading"))
        
        dialog.show_all()
        
        def task():
            try:
                deps = self.manager.get_dependencies(n)
                deps_str = "" 
                for i in deps:
                    deps_str += i + '\n'
                GLib.idle_add(buf.set_text, deps_str or tr("dep_not_found"))
            except Exception as e:
                GLib.idle_add(buf.set_text, tr("dep_error").format(e))
                
        threading.Thread(target=task, daemon=True).start()
        
        dialog.run()
        dialog.destroy()
