import gi
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class PardusBootManager:
	def __init__(self):
		self.builder = Gtk.Builder()
		self.builder.add_from_file("tasarim.glade")

		self.window = self.builder.get_object("main_window")
		self.window.connect("destroy", Gtk.main_quit)

		self.btn_analiz = self.builder.get_object("btn_analiz")
		self.btn_analiz.connect("clicked", self.analiz_et)

		self.output_screen = self.builder.get_object("output_screen")
		self.text_buffer = self.output_screen.get_buffer()

		self.window.show_all()

	def analiz_et(self, widget):
		try:
			analyze_output = subprocess.check_output(["systemd-analyze", "blame"]).decode("utf-8")
			filtered_lines = [
				line.strip() 
				for line in analyze_output.splitlines()
				if any(word in line for word in ["service"])
			]
			decoded_output = "\n".join(filtered_lines)
			self.text_buffer.set_text(decoded_output)
		except Exception as e:
			self.text_buffer.set_text(str(e))


if __name__ == "__main__":
	app = PardusBootManager()
	Gtk.main()
