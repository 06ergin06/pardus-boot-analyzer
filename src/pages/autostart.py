import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from src.locale_mgr import tr
from src.dialogs import AddAutostartDialog
try:
    from gi.repository import Pango
except ImportError:
    class PangoFallback:
        EllipsizeMode = type('EllipsizeMode', (), {'END': 3})
    Pango = PangoFallback()

class AutostartPage:
    def __init__(self, controller):
        self.controller = controller
        self.window = controller.window
        self.manager = controller.manager
        self.set_status = controller.set_status

    def build_page_autostart(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        h_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(h_title, False, False, 0)
        
        lbl_title = Gtk.Label(xalign=0)
        lbl_title.set_text(tr("tab_uygulamalar"))
        lbl_title.get_style_context().add_class("content-title")
        h_title.pack_start(lbl_title, True, True, 0)
        
        btn_add = Gtk.Button(label=tr("yeni_uygulama_ekle_btn"))
        btn_add.connect("clicked", self._on_add_autostart_clicked)
        h_title.pack_start(btn_add, False, False, 0)
        
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_text(tr("autostart_subtitle"))
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
            lbl.set_text(tr('no_autostart_apps'))
            lbl.get_style_context().add_class("dim-label")
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
                lbl_cmd.set_text(entry['exec'])
                lbl_cmd.get_style_context().add_class("dim-label")
                lbl_cmd.set_ellipsize(Pango.EllipsizeMode.END if hasattr(Pango, 'EllipsizeMode') else 3)
                v_box.pack_start(lbl_cmd, False, False, 0)
                
                h_box.pack_start(v_box, True, True, 0)
                
                lbl_delay = Gtk.Label(label=tr("gecikme") + ":")
                lbl_delay.set_valign(Gtk.Align.CENTER)
                h_box.pack_start(lbl_delay, False, False, 6)
                
                spin = Gtk.SpinButton.new_with_range(0, 120, 1)
                spin.set_value(entry["delay"])
                spin.set_valign(Gtk.Align.CENTER)
                spin.connect("value-changed", self._on_autostart_delay_changed, entry["filepath"])
                h_box.pack_start(spin, False, False, 0)
                
                switch = Gtk.Switch()
                switch.set_active(entry["enabled"])
                switch.set_valign(Gtk.Align.CENTER)
                switch.set_halign(Gtk.Align.CENTER)
                switch.connect("state-set", self._on_autostart_toggle, entry["filepath"])
                h_box.pack_start(switch, False, False, 12)
                
                btn_delete = Gtk.Button()
                btn_delete.set_valign(Gtk.Align.CENTER)
                img_del = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
                btn_delete.set_image(img_del)
                btn_delete.connect("clicked", self._on_autostart_delete_clicked, entry["filepath"])
                h_box.pack_start(btn_delete, False, False, 0)
                
                self.autostart_listbox.add(row)
                
        self.autostart_listbox.show_all()

    def _on_autostart_delay_changed(self, spin, filepath):
        delay = int(spin.get_value())
        self.manager.update_autostart_delay(filepath, delay)
        self.set_status(tr("gecikme_guncellendi"))

    def _on_autostart_toggle(self, switch, state, filepath):
        self.manager.toggle_autostart_entry(filepath, state)
        self.set_status(tr("uygulama_aktiflik_guncellendi"))
        return False

    def _on_autostart_delete_clicked(self, button, filepath):
        self.manager.remove_autostart_entry(filepath)
        self.load_autostart_page()
        self.set_status(tr("uygulama_kaldirildi"))

    def _on_add_autostart_clicked(self, button):
        dlg = AddAutostartDialog(self.window, self.manager)
        resp = dlg.run()
        res = dlg.get_result()
        dlg.hide()
        GLib.idle_add(dlg.destroy)
        
        if resp == Gtk.ResponseType.OK and res:
            self.manager.add_autostart_entry(
                name=res["name"],
                command=res["exec"],
                comment=res["comment"],
                icon=res["icon"],
                delay=res["delay"]
            )
            self.set_status(f"'{res['name']}' " + tr("baslangica_eklendi"))
            self.load_autostart_page()

    # --- Page 3: Hizmetler ---
