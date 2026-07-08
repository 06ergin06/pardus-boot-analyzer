import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from src.controller import Controller

class PardusAboutDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(parent=parent, flags=Gtk.DialogFlags.MODAL)
        self.set_default_size(420, 320)
        self.set_resizable(False)
        
        # HeaderBar for the about dialog itself
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        self.set_titlebar(hb)
        
        # Stack switcher at the top center of the HeaderBar
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(200)
        
        switcher = Gtk.StackSwitcher()
        switcher.set_stack(stack)
        hb.set_custom_title(switcher)
        
        # --- Tab 1: Hakkında (About) ---
        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox1.set_margin_start(24)
        vbox1.set_margin_end(24)
        vbox1.set_margin_top(16)
        vbox1.set_margin_bottom(16)
        
        # Icon
        img = Gtk.Image.new_from_icon_name("utilities-system-monitor", Gtk.IconSize.DIALOG)
        vbox1.pack_start(img, False, False, 10)
        
        # Title
        lbl_title = Gtk.Label()
        lbl_title.set_markup("<span size='large' weight='bold'>Pardus Başlangıç Yöneticisi</span>")
        vbox1.pack_start(lbl_title, False, False, 2)
        
        # Version
        lbl_ver = Gtk.Label(label="1.0.0")
        lbl_ver.get_style_context().add_class("dim-label")
        vbox1.pack_start(lbl_ver, False, False, 2)
        
        # Description
        lbl_desc = Gtk.Label(label="Sistem açılışını analiz et ve başlangıç hizmetlerini yönet.")
        lbl_desc.set_line_wrap(True)
        vbox1.pack_start(lbl_desc, False, False, 4)
        
        # Website link
        lbl_web = Gtk.Label()
        lbl_web.set_markup("<a href='https://github.com/06ergin06/pardus-boot-analyzer'>Web sitesi</a>")
        vbox1.pack_start(lbl_web, False, False, 6)
        
        # Copyright
        lbl_copy = Gtk.Label(label="© 2026 TÜBİTAK BİLGEM")
        lbl_copy.get_style_context().add_class("dim-label")
        vbox1.pack_start(lbl_copy, False, False, 4)
        
        # License Disclaimer
        lbl_license = Gtk.Label()
        lbl_license.set_markup(
            "<span size='small'>Bu program kesinlikle hiçbir garanti vermiyor.\n"
            "Ayrıntılar için <a href='https://www.gnu.org/licenses/gpl-3.0.html'>GNU Genel Kamu Lisansı, sürüm 3 ya da sonrası</a> bağlantısına bakın.</span>"
        )
        lbl_license.set_justify(Gtk.Justification.CENTER)
        lbl_license.set_line_wrap(True)
        vbox1.pack_start(lbl_license, False, False, 6)
        
        stack.add_titled(vbox1, "about", "Hakkında")
        
        # --- Tab 2: Hazırlayanlar (Credits) ---
        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox2.set_margin_start(24)
        vbox2.set_margin_end(24)
        vbox2.set_margin_top(16)
        vbox2.set_margin_bottom(16)
        
        # Credits grid
        grid = Gtk.Grid()
        grid.set_column_spacing(18)
        grid.set_row_spacing(10)
        grid.set_halign(Gtk.Align.CENTER)
        vbox2.pack_start(grid, True, True, 20)
        
        # Row 0: Oluşturan
        lbl_cr_title = Gtk.Label(xalign=1)
        lbl_cr_title.set_markup("<b>Oluşturan</b>")
        lbl_cr_title.get_style_context().add_class("dim-label")
        grid.attach(lbl_cr_title, 0, 0, 1, 1)
        
        lbl_cr_val = Gtk.Label(xalign=0)
        lbl_cr_val.set_text("İbrahim Hakkı Ergin")
        grid.attach(lbl_cr_val, 1, 0, 1, 1)
        
        # Row 1: Tasarım
        lbl_ds_title = Gtk.Label(xalign=1)
        lbl_ds_title.set_markup("<b>Tasarım</b>")
        lbl_ds_title.get_style_context().add_class("dim-label")
        grid.attach(lbl_ds_title, 0, 1, 1, 1)
        
        lbl_ds_val = Gtk.Label(xalign=0)
        lbl_ds_val.set_text("İbrahim Hakkı Ergin")
        grid.attach(lbl_ds_val, 1, 1, 1, 1)
        
        # Row 2: Grafikler
        lbl_gr_title = Gtk.Label(xalign=1)
        lbl_gr_title.set_markup("<b>Grafikler</b>")
        lbl_gr_title.get_style_context().add_class("dim-label")
        grid.attach(lbl_gr_title, 0, 2, 1, 1)
        
        lbl_gr_val = Gtk.Label(xalign=0)
        lbl_gr_val.set_text("İbrahim Hakkı Ergin")
        grid.attach(lbl_gr_val, 1, 2, 1, 1)
        
        stack.add_titled(vbox2, "credits", "Hazırlayanlar")
        
        content = self.get_content_area()
        content.pack_start(stack, True, True, 0)
        
        self.show_all()

class PardusBootManager:
    def __init__(self):
        # We construct the Window programmatically to enable a modern layout
        self.window = Gtk.Window(title="Pardus Başlangıç Yöneticisi")
        self.window.set_default_size(1050, 720)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        
        # Construct HeaderBar matching native Pardus design
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.set_title("Pardus Başlangıç Yöneticisi")
        hb.set_subtitle("Sistem Açılış Analiz ve Optimizasyon Aracı")
        self.window.set_titlebar(hb)
        
        # Add About button to HeaderBar
        btn_about = Gtk.Button()
        btn_about.set_image(Gtk.Image.new_from_icon_name("help-about", Gtk.IconSize.BUTTON))
        btn_about.set_tooltip_text("Hakkında")
        btn_about.connect("clicked", self._on_about_clicked)
        hb.pack_end(btn_about)
        
        # Load Controller which will construct the layout dynamically
        self.controller = Controller(self.window)
        
        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()

    def _on_about_clicked(self, button):
        dlg = PardusAboutDialog(self.window)
        dlg.run()
        dlg.hide()
        GLib.idle_add(dlg.destroy)

if __name__ == "__main__":
    app = PardusBootManager()
    Gtk.main()
