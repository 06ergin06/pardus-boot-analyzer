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
from src.pages.hizmetler import HizmetlerPage


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
        self.hizmetler_page = HizmetlerPage(self)
        self.stack.add_named(self.hizmetler_page.build_page_hizmetler(), "hizmetler")
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
        self.hizmetler_page = HizmetlerPage(self)
        self.stack.add_named(self.hizmetler_page.build_page_hizmetler(), "hizmetler")
        self.stack.add_named(self.build_page_profiller(), "profiller")
        
        # 6. Reload data to populate widgets
        self.load_all()
        
        # 7. Restore sidebar selection
        self.sidebar_listbox.select_row(self.sidebar_listbox.get_row_at_index(selected_index))
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
        self.analiz_page.load_analysis_page()
        self.autostart_page.load_autostart_page()
        self.hizmetler_page.load_all()
        self.load_profiles_page()

    # Expose HizmetlerPage properties for backward compatibility
    @property
    def liststore(self):
        return self.hizmetler_page.liststore

    @property
    def selection(self):
        return self.hizmetler_page.selection

    @property
    def treeview(self):
        return self.hizmetler_page.treeview

    @property
    def view_combo(self):
        return self.hizmetler_page.view_combo

    @property
    def filter_combo(self):
        return self.hizmetler_page.filter_combo

    @property
    def tip_combo(self):
        return self.hizmetler_page.tip_combo

    @property
    def search_entry(self):
        return self.hizmetler_page.search_entry

try:
    from gi.repository import Pango
except ImportError:
    class PangoFallback:
        EllipsizeMode = type('EllipsizeMode', (), {'END': 3})
    Pango = PangoFallback()

