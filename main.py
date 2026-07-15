import os
import sys
import json

# Set language environment variables for GTK to match saved application language or system language
try:
    lang = "tr"
    sys_lang = os.environ.get("LANG", "tr").split(".")[0].split("_")[0].lower()
    if sys_lang in ("en", "tr"):
        lang = sys_lang
    config_dir = os.path.expanduser("~/.config/pardus-boot-analyzer")
    config_path = os.path.join(config_dir, "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            if cfg.get("lang") in ("en", "tr"):
                lang = cfg["lang"]
    os.environ["LANGUAGE"] = lang
    os.environ["LANG"] = "en_US.UTF-8" if lang == "en" else "tr_TR.UTF-8"
    os.environ["LC_ALL"] = "en_US.UTF-8" if lang == "en" else "tr_TR.UTF-8"
except Exception:
    pass

def _detect_dark_preference():
    """Returns True if user prefers dark mode — checks portal, env, settings.ini."""
    # 1. GTK_THEME env var (highest priority)
    val = (os.environ.get("GTK_THEME") or "").lower()
    if "dark" in val or "black" in val or "night" in val:
        return True

    # 2. Freedesktop color-scheme portal (Wayland standard, KDE, GNOME)
    try:
        import subprocess
        out = subprocess.check_output(
            ["dbus-send", "--print-reply", "--dest=org.freedesktop.portal.Desktop",
             "/org/freedesktop/portal/desktop", "org.freedesktop.portal.Settings.Read",
             "string:org.freedesktop.appearance", "string:color-scheme"],
            stderr=subprocess.DEVNULL, timeout=1
        ).decode("utf-8")
        if "uint32 1" in out:
            return True
    except Exception:
        pass

    # 3. gtk-3.0/settings.ini
    try:
        path = os.path.expanduser("~/.config/gtk-3.0/settings.ini")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().lower()
            if "gtk-application-prefer-dark-theme=1" in content or \
               "gtk-application-prefer-dark-theme=true" in content:
                return True
            for line in content.splitlines():
                if line.strip().startswith("gtk-theme-name"):
                    if any(x in line for x in ("dark", "black", "night", "dracula")):
                        return True
    except Exception:
        pass

    return False

def _needs_adwaita_fallback():
    """
    Returns True if we should force Adwaita.
    We do NOT touch the theme on full desktop environments (GNOME, KDE, etc.)
    — they have their own theme engines and the user has made their choice.
    We only force Adwaita on minimal WMs or when GTK has no theme configured.
    """
    desktop = (os.environ.get("XDG_CURRENT_DESKTOP") or "").lower()
    session = (os.environ.get("DESKTOP_SESSION") or "").lower()

    # Full DEs — respect system theme completely
    full_de_keywords = ("gnome", "kde", "plasma", "xfce", "cinnamon",
                        "mate", "lxde", "lxqt", "pantheon", "budgie",
                        "deepin", "unity", "enlightenment")
    if any(kw in desktop or kw in session for kw in full_de_keywords):
        return False

    # No DE detected (bare WM: i3, Hyprland, Sway, openbox, etc.)
    return True

# Apply Adwaita only where needed — before GTK is imported
try:
    if _needs_adwaita_fallback():
        is_dark = _detect_dark_preference()
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
        self.set_version("1.0.4")
        self.set_comments(tr("about_comments"))
        self.set_copyright("© 2026 İbrahim Hakkı Ergin")
        self.set_website("https://github.com/06ergin06/pardus-boot-analyzer")
        self.set_website_label("Website")
        
        self.set_license(tr("lisans"))
        self.set_wrap_license(True)
        
        # Load logo for AboutDialog
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "pardus-boot-analyzer.svg")
        
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 64, 64, True)
            self.set_logo(pixbuf)
        except Exception:
            icon_theme = Gtk.IconTheme.get_default()
            if icon_theme.has_icon("pardus-boot-analyzer"):
                self.set_logo_icon_name("pardus-boot-analyzer")
            elif icon_theme.has_icon("pardus"):
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
        self.hb = hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.set_title(tr("title"))
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
        from src.locale_mgr import LANG, save_lang_pref, tr
        
        new_lang = "en" if LANG == "tr" else "tr"
        save_lang_pref(new_lang)
        
        # 1. Update HeaderBar button label and tooltip
        button.set_label("EN" if new_lang == "tr" else "TR")
        self.window.set_title(tr("title"))
        self.hb.set_title(tr("title"))
        
        # 2. Update About button tooltip text
        for child in self.window.get_titlebar().get_children():
            if isinstance(child, Gtk.Button) and child != button:
                # This must be the about button
                child.set_tooltip_text(tr("about"))
        
        # 3. Dynamic UI Rebuilding on Controller
        self.controller.rebuild_ui_for_language()

if __name__ == "__main__":
    app = PardusBootManager()
    Gtk.main()
