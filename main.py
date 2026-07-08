import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.controller import Controller

class PardusBootManager:
    def __init__(self):
        # We construct the Window programmatically to enable a modern layout
        self.window = Gtk.Window(title="Pardus Başlangıç Yöneticisi")
        self.window.set_default_size(1050, 720)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        
        # Load Controller which will construct the layout dynamically
        self.controller = Controller(self.window)
        
        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()

if __name__ == "__main__":
    app = PardusBootManager()
    Gtk.main()
