import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import os
import json

from src.locale_mgr import tr
from src.dialogs import ProfileCreatorDialog
from src.utils import parse_blame_time, PROFILE_SERVICE_LABELS, _config_data

class ProfilesPage:
    def __init__(self, controller):
        self.controller = controller
        self.window = controller.window
        self.manager = controller.manager
        self.set_status = controller.set_status
        self._ensure_auth = controller._ensure_auth
        self._calculate_profile_savings = controller._calculate_profile_savings

    def build_page_profiles(self):
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
            if savings > 0.05:
                lbl_saving.get_style_context().add_class("success-text")
                lbl_saving.set_markup(f"<b>{tr('tahmini_kazanc')}: ~{savings:.1f}s</b>")
            else:
                lbl_saving.get_style_context().add_class("dim-label")
                lbl_saving.set_text(f"{tr('tahmini_kazanc')}: < 0.1s")
            lbl_saving.set_margin_bottom(4)
            card.pack_start(lbl_saving, False, False, 0)
            
            btn_apply = Gtk.Button(label=tr("profili_uygula"))
            btn_apply.get_style_context().add_class("suggested-action")
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
        btn_create_custom.get_style_context().add_class("suggested-action")
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
            lbl.set_text(tr('no_custom_profiles'))
            lbl.get_style_context().add_class("dim-label")
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
                    lbl_desc.set_text(f"{count} {tr('hizmet_kurali')}")
                    lbl_desc.get_style_context().add_class("dim-label")
                    v_box.pack_start(lbl_desc, False, False, 0)
                    
                    h_box.pack_start(v_box, True, True, 0)
                    
                    btn_apply = Gtk.Button(label=tr("uygula"))
                    btn_apply.set_valign(Gtk.Align.CENTER)
                    btn_apply.get_style_context().add_class("suggested-action")
                    btn_apply.connect("clicked", self._on_apply_custom_profile_clicked, fpath)
                    h_box.pack_start(btn_apply, False, False, 6)
                    
                    btn_del = Gtk.Button()
                    btn_del.set_valign(Gtk.Align.CENTER)
                    img_del = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
                    btn_del.set_image(img_del)
                    btn_del.get_style_context().add_class("destructive-action")
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
            lbl.set_text(tr('no_backups_found'))
            lbl.get_style_context().add_class("dim-label")
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
                lbl_desc.set_text(f"{count} {tr('hizmetin_yedegi')}")
                lbl_desc.get_style_context().add_class("dim-label")
                v_box.pack_start(lbl_desc, False, False, 0)
                
                h_box.pack_start(v_box, True, True, 0)
                
                btn_restore = Gtk.Button(label=tr("geri_yukle"))
                btn_restore.set_valign(Gtk.Align.CENTER)
                btn_restore.get_style_context().add_class("suggested-action")
                btn_restore.connect("clicked", self._on_restore_backup_clicked, fpath)
                h_box.pack_start(btn_restore, False, False, 6)
                
                btn_del = Gtk.Button()
                btn_del.set_valign(Gtk.Align.CENTER)
                img_del = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
                btn_del.set_image(img_del)
                btn_del.get_style_context().add_class("destructive-action")
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
        dlg.hide()
        GLib.idle_add(dlg.destroy)
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
        dlg.hide()
        GLib.idle_add(dlg.destroy)
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
        dlg.hide()
        GLib.idle_add(dlg.destroy)
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
            info.hide()
            GLib.idle_add(info.destroy)
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
            dep_dlg.hide()
            GLib.idle_add(dep_dlg.destroy)
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
        dlg.hide()
        GLib.idle_add(dlg.destroy)
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
            dep_dlg.hide()
            GLib.idle_add(dep_dlg.destroy)
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
                info.hide()
                GLib.idle_add(info.destroy)
                self.load_all()
            else:
                err = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
                    message_format=tr("profil_uygulama_hatasi"),
                )
                err.format_secondary_text(msg)
                err.run()
                err.hide()
                GLib.idle_add(err.destroy)
                
        threading.Thread(target=task, daemon=True).start()

    def _on_save_custom_profile_clicked(self, button):
        dialog = Gtk.Dialog(title=tr("profili_kaydet_title"), parent=self.window, flags=Gtk.DialogFlags.MODAL)
        dialog.add_button(tr("iptal"), Gtk.ResponseType.CANCEL)
        btn_save = dialog.add_button(tr("kaydet"), Gtk.ResponseType.OK)
        btn_save.get_style_context().add_class("suggested-action")
        
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
