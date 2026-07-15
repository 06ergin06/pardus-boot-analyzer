import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

from src.locale_mgr import tr

class AddAutostartDialog(Gtk.Dialog):
    def __init__(self, parent, manager):
        super().__init__(title=tr("startup_uygulamasi_add"), parent=parent, flags=Gtk.DialogFlags.MODAL)
        self.set_default_size(520, 420)
        self.manager = manager
        
        self.add_button(tr("cancel"), Gtk.ResponseType.CANCEL)
        self.btn_ok = self.add_button(tr("add"), Gtk.ResponseType.OK)
        self.btn_ok.get_style_context().add_class("suggested-action")
        
        content = self.get_content_area()
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        
        notebook = Gtk.Notebook()
        content.pack_start(notebook, True, True, 0)
        
        # Tab 1: Installed Apps
        tab1_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        search_entry = Gtk.SearchEntry(placeholder_text=tr("app_search_placeholder"))
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
        
        col_name = Gtk.TreeViewColumn(tr("app_name"))
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
            
        notebook.append_page(tab1_box, Gtk.Label(label=tr("tab_desktop_apps")))
        
        # Tab 2: Custom Command
        tab2_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tab2_box.set_margin_top(12)
        
        grid = Gtk.Grid(column_spacing=12, row_spacing=12)
        tab2_box.pack_start(grid, False, False, 0)
        
        lbl_name = Gtk.Label(label=tr("app_name") + ":", xalign=1)
        self.entry_name = Gtk.Entry()
        grid.attach(lbl_name, 0, 0, 1, 1)
        grid.attach(self.entry_name, 1, 0, 1, 1)
        
        lbl_exec = Gtk.Label(label=tr("komut") + " (Exec):", xalign=1)
        self.entry_exec = Gtk.Entry()
        grid.attach(lbl_exec, 0, 1, 1, 1)
        grid.attach(self.entry_exec, 1, 1, 1, 1)
        
        lbl_comment = Gtk.Label(label=tr("description") + ":", xalign=1)
        self.entry_comment = Gtk.Entry()
        grid.attach(lbl_comment, 0, 2, 1, 1)
        grid.attach(self.entry_comment, 1, 2, 1, 1)
        
        lbl_delay = Gtk.Label(label=tr("delay") + f" ({tr('select_lbl')}):", xalign=1)
        self.spin_delay = Gtk.SpinButton.new_with_range(0, 120, 1)
        grid.attach(lbl_delay, 0, 3, 1, 1)
        grid.attach(self.spin_delay, 1, 3, 1, 1)
        
        notebook.append_page(tab2_box, Gtk.Label(label=tr("tab_custom_command")))
        
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
        
        # Cancel button closes dialog with CANCEL response
        self.btn_cancel = self.add_button(tr("cancel"), Gtk.ResponseType.CANCEL)
        
        # Yetkilendir button triggers click handler directly (doesn't auto-close)
        self.btn_auth = Gtk.Button(label=tr("yetkilendir"))
        self.btn_auth.get_style_context().add_class("suggested-action")
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
        lbl_head.set_text(tr("auth_gerekiyor"))
        lbl_head.get_style_context().add_class("auth-head")
        vbox.pack_start(lbl_head, False, False, 0)
        
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_text(tr("auth_sub_info"))
        lbl_sub.get_style_context().add_class("auth-sub")
        lbl_sub.set_line_wrap(True)
        vbox.pack_start(lbl_sub, False, False, 0)
        
        h_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(h_row, False, False, 0)
        
        self.entry_pwd = Gtk.Entry()
        self.entry_pwd.set_visibility(False)
        self.entry_pwd.set_placeholder_text(tr("password_placeholder"))
        self.entry_pwd.connect("activate", lambda e: self._on_auth_clicked(None))
        h_row.pack_start(self.entry_pwd, True, True, 0)
        
        self.chk_show = Gtk.CheckButton(label=tr("sifreyi_show"))
        self.chk_show.connect("toggled", self._on_show_toggled)
        vbox.pack_start(self.chk_show, False, False, 0)
        
        self.lbl_error = Gtk.Label(xalign=0)
        self.lbl_error.get_style_context().add_class("error-text")
        vbox.pack_start(self.lbl_error, False, False, 0)
        
        self.show_all()

    def _on_show_toggled(self, widget):
        self.entry_pwd.set_visibility(widget.get_active())

    def _on_auth_clicked(self, button):
        import threading
        pwd = self.entry_pwd.get_text()
        self.lbl_error.set_text("")
        
        # Disable UI and show spinner while verifying in background thread
        self.set_sensitive(False)
        self.btn_auth.set_label(tr("yetkilendiriliyor"))
        
        def verify():
            valid = self.manager.verify_sudo_password(pwd)
            GLib.idle_add(self._on_auth_done, valid, pwd)
        
        threading.Thread(target=verify, daemon=True).start()

    def _on_auth_done(self, valid, pwd):
        self.set_sensitive(True)
        self.btn_auth.set_label(tr("yetkilendir"))
        
        if valid:
            self.success = True
            self.entered_password = pwd
            self.response(Gtk.ResponseType.OK)
        else:
            self.lbl_error.set_markup(
                f"<span foreground='#dc3545'>{tr('hatali_password')}</span>"
            )
        return False




class ProfileCreatorDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title=tr("yeni_custom_profile_btn"), parent=parent, flags=Gtk.DialogFlags.MODAL)
        self.set_default_size(420, 480)
        
        # Add buttons
        self.add_button(tr("cancel"), Gtk.ResponseType.CANCEL)
        btn_save = self.add_button(tr("save"), Gtk.ResponseType.OK)
        btn_save.get_style_context().add_class("suggested-action")
        
        # Main layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        self.get_content_area().add(box)
        
        # Name Entry
        lbl_name = Gtk.Label(xalign=0)
        lbl_name.set_markup(f"<b>{tr('profile_name_lbl')}</b>")
        box.pack_start(lbl_name, False, False, 0)
        
        self.entry_name = Gtk.Entry()
        self.entry_name.set_placeholder_text(tr("profile_name_placeholder"))
        box.pack_start(self.entry_name, False, False, 0)
        
        # Services label
        lbl_services = Gtk.Label(xalign=0)
        lbl_services.set_markup(f"<b>{tr('service_kurallari_lbl')}</b>\n<span size='small' foreground='#666666'>{tr('service_kurallari_sub')}</span>")
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
            "cups.service": tr("cups_service_desc"),
            "cups-browsed.service": tr("cups_browsed_desc"),
            "bluetooth.service": tr("bluetooth_desc"),
            "docker.service": "Docker Konteyner",
            "postgresql.service": tr("postgresql_desc"),
            "mysql.service": tr("mysql_desc"),
            "ssh.service": tr("ssh_desc"),
            "avahi-daemon.service": tr("avahi_desc"),
            "ModemManager.service": tr("modem_desc"),
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
            return None, tr("profile_name_girin_error")
            
        services = {}
        for svc, switch in self.switches.items():
            services[svc] = "enable" if switch.get_active() else "disable"
            
        return {
            "name": name,
            "services": services
        }, None
