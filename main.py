import os
import sys

# Force GTK to use the compiled-in Adwaita theme ONLY on minimal window managers (like Hyprland, Sway, i3)
# where GTK theme engines are unconfigured or missing.
try:
    desktop = (os.environ.get("XDG_CURRENT_DESKTOP") or "").lower()
    is_minimal = any(wm in desktop for wm in ("hyprland", "sway", "i3", "openbox", "bspwm", "awesome")) or not desktop
    
    if is_minimal:
        is_dark = False
        # 1. Check existing env variables
        for key in ("GTK_THEME", "THEME"):
            val = (os.environ.get(key) or "").lower()
            if "dark" in val or "black" in val or "night" in val:
                is_dark = True
                break
                
        # 2. Check portal color-scheme via dbus (KDE, Hyprland, Wayland standard)
        if not is_dark:
            try:
                import subprocess
                out = subprocess.check_output(
                    ["dbus-send", "--print-reply", "--dest=org.freedesktop.portal.Desktop",
                     "/org/freedesktop/portal/desktop", "org.freedesktop.portal.Settings.Read",
                     "string:org.freedesktop.appearance", "string:color-scheme"],
                    stderr=subprocess.DEVNULL, timeout=1
                ).decode("utf-8")
                if "uint32 1" in out:
                    is_dark = True
            except Exception:
                pass
                
        # 3. Check settings.ini
        if not is_dark:
            try:
                path = os.path.expanduser("~/.config/gtk-3.0/settings.ini")
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read().lower()
                        if "gtk-application-prefer-dark-theme=true" in content or "gtk-application-prefer-dark-theme=1" in content:
                            is_dark = True
                        else:
                            for line in content.splitlines():
                                if line.strip().startswith("gtk-theme-name"):
                                    if any(x in line for x in ("dark", "black", "night", "tokyo", "dracula")):
                                        is_dark = True
                                        break
            except Exception:
                pass
                
        os.environ["GTK_THEME"] = "Adwaita:dark" if is_dark else "Adwaita"
except Exception:
    pass

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf
from src.controller import Controller
from src.locale_mgr import tr

class PardusAboutDialog(Gtk.AboutDialog):
    def __init__(self, parent):
        super().__init__(parent=parent, flags=Gtk.DialogFlags.MODAL)
        self.set_program_name(tr("title"))
        self.set_version("1.0.0")
        self.set_comments(tr("about_comments"))
        self.set_copyright("© 2026 İbrahim Hakkı Ergin")
        self.set_website("https://github.com/06ergin06/pardus-boot-analyzer")
        self.set_website_label("Website")
        
        self.set_license(tr("lisans"))
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
        self.window = Gtk.Window(title=tr("title"))
        self.window.set_default_size(1050, 720)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        
        # Load the custom SVG logo path safely
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "pardus-boot-analyzer.svg")
        
        # Construct HeaderBar matching native Pardus design
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        # Note: We do not set text title/subtitle in the headerbar,
        # instead displaying the logo as the main branding element on the top left.
        self.window.set_titlebar(hb)
        
        # Load logo for HeaderBar using Pixbuf to handle SVG scaling cleanly and pack on the left
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 28, 28, True)
            img_logo = Gtk.Image.new_from_pixbuf(pixbuf)
        except Exception:
            img_logo = Gtk.Image.new_from_icon_name("utilities-system-monitor", Gtk.IconSize.MENU)
            
        img_logo.set_margin_start(6)
        img_logo.set_margin_end(6)
        hb.pack_start(img_logo)
        
        # Add About button to HeaderBar
        btn_about = Gtk.Button()
        btn_about.set_image(Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.BUTTON))
        btn_about.set_tooltip_text(tr("about"))
        btn_about.connect("clicked", self._on_about_clicked)
        hb.pack_end(btn_about)
        
        # Add Language button to HeaderBar
        from src.locale_mgr import LANG
        btn_lang = Gtk.Button(label="EN" if LANG == "tr" else "TR")
        btn_lang.set_tooltip_text("Dil Değiştir / Switch Language")
        btn_lang.connect("clicked", self._on_lang_clicked)
        hb.pack_end(btn_lang)
        
        # Load Controller which will construct the layout dynamically
        self.controller = Controller(self.window)
        
        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()

    def _on_about_clicked(self, button):
        dlg = PardusAboutDialog(self.window)
        dlg.run()
        dlg.hide()
        GLib.idle_add(dlg.destroy)

    def _on_lang_clicked(self, button):
        from src.locale_mgr import LANG, save_lang_pref
        import sys
        import os
        
        new_lang = "en" if LANG == "tr" else "tr"
        save_lang_pref(new_lang)
        
        # Restart process instantly to apply language settings
        os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    # If the system has no GTK theme configured (falls back to Raleigh or Default),
    # force the built-in Adwaita theme to ensure a clean layout on minimal platforms (Hyprland, i3, etc.).
    try:
        settings = Gtk.Settings.get_default()
        if settings:
            theme_name = settings.get_property("gtk-theme-name")
            if not theme_name or theme_name.lower() in ("raleigh", "default"):
                is_dark = False
                try:
                    import subprocess
                    out = subprocess.check_output(
                        ["dbus-send", "--print-reply", "--dest=org.freedesktop.portal.Desktop",
                         "/org/freedesktop/portal/desktop", "org.freedesktop.portal.Settings.Read",
                         "string:org.freedesktop.appearance", "string:color-scheme"],
                        stderr=subprocess.DEVNULL, timeout=1
                    ).decode("utf-8")
                    if "uint32 1" in out:
                        is_dark = True
                except Exception:
                    pass
                
                settings.set_property("gtk-theme-name", "Adwaita")
                if is_dark:
                    settings.set_property("gtk-application-prefer-dark-theme", True)
    except Exception:
        pass

    app = PardusBootManager()
    Gtk.main()
