import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from src.controller import Controller

class PardusAboutDialog(Gtk.AboutDialog):
    def __init__(self, parent):
        super().__init__(parent=parent, flags=Gtk.DialogFlags.MODAL)
        self.set_program_name("Pardus Başlangıç Yöneticisi")
        self.set_version("1.0.0")
        self.set_comments("Sistem açılışını analiz et ve başlangıç hizmetlerini yönet.")
        self.set_copyright("© 2026 TÜBİTAK BİLGEM")
        self.set_website("https://github.com/06ergin06/pardus-boot-analyzer")
        self.set_website_label("Web sitesi")
        
        self.set_license(
            "Bu program kesinlikle hiçbir garanti vermiyor.\n"
            "Ayrıntılar için GNU Genel Kamu Lisansı, sürüm 3 ya da sonrası bağlantısına bakın."
        )
        self.set_wrap_license(True)
        
        icon_theme = Gtk.IconTheme.get_default()
        if icon_theme.has_icon("pardus"):
            self.set_logo_icon_name("pardus")
        else:
            self.set_logo_icon_name("utilities-system-monitor")
            
        self.set_authors(["İbrahim Hakkı Ergin (Oluşturan, Tasarım, Grafikler)"])
        self.set_artists(["İbrahim Hakkı Ergin"])
        
        self.connect("response", lambda dialog, response_id: dialog.destroy())

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
        
        # Sol üst köşede Pardus logosu
        icon_theme = Gtk.IconTheme.get_default()
        if icon_theme.has_icon("pardus-symbolic"):
            img_logo = Gtk.Image.new_from_icon_name("pardus-symbolic", Gtk.IconSize.MENU)
        elif icon_theme.has_icon("pardus"):
            img_logo = Gtk.Image.new_from_icon_name("pardus", Gtk.IconSize.MENU)
        else:
            img_logo = Gtk.Image.new_from_icon_name("preferences-system-symbolic", Gtk.IconSize.MENU)
        img_logo.set_margin_start(6)
        img_logo.set_margin_end(6)
        hb.pack_start(img_logo)
        
        # Add About button to HeaderBar
        btn_about = Gtk.Button()
        btn_about.set_image(Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.BUTTON))
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
