import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from src.system_manager import SystemManager


class Controller:
    def __init__(self, builder):
        self.builder = builder
        self.manager = SystemManager()

        self.liststore = builder.get_object("service_liststore")
        self.treeview = builder.get_object("service_treeview")
        self.selection = builder.get_object("service_selection")
        self.boot_time_label = builder.get_object("boot_time_label")
        self.search_entry = builder.get_object("search_entry")
        self.log_textview = builder.get_object("log_textview")

        self._connect_signals()
        self.load_all()

    def _connect_signals(self):
        self.builder.get_object("btn_refresh").connect("clicked", self.load_all)
        self.builder.get_object("btn_enable").connect("clicked", self._on_enable)
        self.builder.get_object("btn_disable").connect("clicked", self._on_disable)
        self.builder.get_object("btn_mask").connect("clicked", self._on_mask)
        self.builder.get_object("btn_unmask").connect("clicked", self._on_unmask)
        self.builder.get_object("btn_show_log").connect("clicked", self._on_show_log)
        self.search_entry.connect("changed", self._on_search_changed)

    def load_all(self, *args):
        self.liststore.clear()
        self._set_log_text("Yukleniyor...")

        try:
            services = self.manager.get_services()
            blame_data = {}
            for item in self.manager.get_blame_data()[0]:
                blame_data[item["name"]] = item["time"]

            total_time, _ = self.manager.get_total_boot_time()
            self.boot_time_label.set_text(f"Toplam Acilis Suresi: {total_time}")

            for svc in services:
                name = svc["name"]
                blame_time = blame_data.get(name, "")
                self.liststore.append([
                    name,
                    svc["active"],
                    svc["sub"],
                    svc["load"],
                    blame_time,
                    svc["description"]
                ])

            if self.search_entry.get_text():
                self._apply_filter()
            else:
                self._set_log_text(f"{len(services)} servis listelendi.")
        except Exception as e:
            self._set_log_text(f"Hata: {str(e)}")

    def _get_selected_service(self):
        model, treeiter = self.selection.get_selected()
        if treeiter is not None:
            return model[treeiter][0]
        return None

    def _on_enable(self, *args):
        name = self._get_selected_service()
        if not name:
            self._set_log_text("Lutfen bir servis secin.")
            return
        success, msg = self.manager.enable_service(name)
        self._set_log_text(msg)
        if success:
            self.load_all()

    def _on_disable(self, *args):
        name = self._get_selected_service()
        if not name:
            self._set_log_text("Lutfen bir servis secin.")
            return
        success, msg = self.manager.disable_service(name)
        self._set_log_text(msg)
        if success:
            self.load_all()

    def _on_mask(self, *args):
        name = self._get_selected_service()
        if not name:
            self._set_log_text("Lutfen bir servis secin.")
            return

        dialog = Gtk.MessageDialog(
            parent=self.builder.get_object("main_window"),
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            message_format=f"'{name}' servisini maskelemek istediginize emin misiniz?"
        )
        dialog.format_secondary_text(
            "Maske islemi, servisi tamamen kullanilamaz hale getirir "
            "ve baska servislerin tetiklemesini de engeller."
        )
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            success, msg = self.manager.mask_service(name)
            self._set_log_text(msg)
            if success:
                self.load_all()

    def _on_unmask(self, *args):
        name = self._get_selected_service()
        if not name:
            self._set_log_text("Lutfen bir servis secin.")
            return
        success, msg = self.manager.unmask_service(name)
        self._set_log_text(msg)
        if success:
            self.load_all()

    def _on_show_log(self, *args):
        name = self._get_selected_service()
        if not name:
            self._set_log_text("Lutfen bir servis secin.")
            return
        log = self.manager.get_journal_log(name)
        self._set_log_text(log)

    def _on_search_changed(self, *args):
        self._apply_filter()

    def _apply_filter(self):
        query = self.search_entry.get_text().lower()
        self.liststore.clear()

        try:
            services = self.manager.get_services()
            blame_data = {}
            for item in self.manager.get_blame_data()[0]:
                blame_data[item["name"]] = item["time"]

            for svc in services:
                if query and query not in svc["name"].lower():
                    continue
                name = svc["name"]
                blame_time = blame_data.get(name, "")
                self.liststore.append([
                    name,
                    svc["active"],
                    svc["sub"],
                    svc["load"],
                    blame_time,
                    svc["description"]
                ])
        except Exception as e:
            self._set_log_text(f"Arama sirasinda hata: {str(e)}")

    def _set_log_text(self, text):
        buffer = self.log_textview.get_buffer()
        buffer.set_text(text)
