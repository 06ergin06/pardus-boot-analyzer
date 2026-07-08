import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.controller import Controller


class PardusBootManager:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui/tasarim.glade")

        self.controller = Controller(self.builder)

        self.window = self.builder.get_object("main_window")
        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()


if __name__ == "__main__":
    app = PardusBootManager()
    Gtk.main()
