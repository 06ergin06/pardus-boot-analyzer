import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from src.system_manager import SystemManager


SERVICE_DESCRIPTIONS = {
    "NetworkManager-wait-online.service": "Aglar hazir olana kadar bekler. Gereksizse kapatilabilir.",
    "NetworkManager.service": "Ag baglantilarini yonetir. Internet kullaniyorsaniz gerekli.",
    "upower.service": "Pil ve guc yonetimi. Masaustu bilgisayarda gereksiz.",
    "bluetooth.service": "Bluetooth destegi. Bluetooth kullanmiyorsaniz kapatabilirsiniz.",
    "cups.service": "Yazici destegi (CUPS). Yazici kullanmiyorsaniz kapatabilirsiniz.",
    "avahi-daemon.service": "Agda cihaz kesfi. Genelde gereksiz.",
    "ModemManager.service": "Mobil broadband (3G/4G) modem destegi. Gerekmiyorsa kapatilabilir.",
    "cups-browsed.service": "Ag yazicilarini otomatik bulur. Yazici yoksa gereksiz.",
    "colord.service": "Renk yonetimi. Grafik isiyle ugrasmiyorsaniz gereksiz.",
    "PackageKit.service": "Yazilim yoneticisi arka plan servisi.",
    "gdm.service": "Giris ekrani (GDM). Pardus'un calismasi icin gerekli.",
    "accounts-daemon.service": "Kullanici hesaplari servisi. Sistem icin gerekli.",
    "udisks2.service": "Disk takip-cikar yonetimi. Genelde gerekli.",
    "polkit.service": "Yetki yonetimi. Sistem icin gerekli.",
    "systemd-journald.service": "Sistem log kayitlari. Genelde gerekli.",
    "systemd-logind.service": "Kullanici oturum yonetimi. Sistem icin gerekli.",
    "systemd-udevd.service": "Cihaz yonetimi (udev). Sistem icin gerekli.",
    "wpa_supplicant.service": "Kablosuz ag baglantisi. Wi-Fi kullaniyorsaniz gerekli.",
    "smartmontools.service": "Disk sagligi izleme. Gereksiz olabilir.",
    "lm-sensors.service": "Isi ve voltaj sensorleri. Gereksiz olabilir.",
    "apparmor.service": "Guvenlik modulu (AppArmor). Guvenlik icin onerilir.",
}


SERVICE_SUGGESTIONS = {
    "NetworkManager-wait-online.service": ("oneri", "Genelde kapatilabilir. Ag hazir olana kadar bekletir."),
    "upower.service": ("oneri", "Masaustu PC'de kapatilabilir."),
    "bluetooth.service": ("oneri", "Bluetooth kullanmiyorsaniz kapatabilirsiniz."),
    "cups.service": ("oneri", "Yazici kullanmiyorsaniz kapatilabilir."),
    "avahi-daemon.service": ("oneri", "Guvenlik ve performans icin kapatilabilir."),
    "ModemManager.service": ("oneri", "3G/4G modem kullanmiyorsaniz kapatilabilir."),
    "NetworkManager.service": ("kritik", "Internet baglantisi icin gerekli."),
    "gdm.service": ("kritik", "Grafik arayuz icin gerekli. Kapatmayin."),
    "accounts-daemon.service": ("kritik", "Kullanici hesaplari icin gerekli."),
    "polkit.service": ("kritik", "Yetki yonetimi icin gerekli."),
    "systemd-journald.service": ("kritik", "Sistem loglari icin gerekli."),
    "systemd-logind.service": ("kritik", "Oturum yonetimi icin gerekli."),
    "systemd-udevd.service": ("kritik", "Cihaz algilama icin gerekli."),
    "apparmor.service": ("kritik", "Guvenlik icin onerilir."),
}


STATUS_COLORS = {
    "active": "#2e7d32",
    "inactive": "#c62828",
    "disabled": "#6a1b9a",
    "masked": "#795548",
    "static": "#1565c0",
    "activating": "#e65100",
    "deactivating": "#e65100",
}


class Controller:
    def __init__(self, builder):
        self.builder = builder
        self.manager = SystemManager()
        self._current_filter = "all"

        self.liststore = builder.get_object("service_liststore")
        self.treeview = builder.get_object("service_treeview")
        self.selection = builder.get_object("service_selection")
        self.boot_time_label = builder.get_object("boot_time_label")
        self.search_entry = builder.get_object("search_entry")
        self.log_textview = builder.get_object("log_textview")
        self.detail_name = builder.get_object("detail_name")
        self.detail_desc = builder.get_object("detail_desc")
        self.detail_suggestion = builder.get_object("detail_suggestion")
        self.renderer_status = builder.get_object("renderer_status")
        self.renderer_name = builder.get_object("renderer_name")

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
        self.selection.connect("changed", self._on_selection_changed)

        filters = [
            ("filter_all", "all"),
            ("filter_active", "active"),
            ("filter_inactive", "inactive"),
            ("filter_disabled", "disabled"),
            ("filter_masked", "masked"),
        ]
        for btn_name, state in filters:
            btn = self.builder.get_object(btn_name)
            btn.connect("toggled", self._on_filter_toggled, state)

    def load_all(self, *args):
        self.liststore.clear()
        self._set_log_text("Yukleniyor...")
        self.detail_name.set_text("Servis secilmedi")
        self.detail_desc.set_text("Detaylar icin bir servis secin.")
        self.detail_suggestion.set_text("")

        try:
            services = self.manager.get_services()
            blame_data = {}
            for item in self.manager.get_blame_data()[0]:
                blame_data[item["name"]] = item["time"]

            total_time, raw = self.manager.get_total_boot_time()
            self.boot_time_label.set_text("Toplam Acilis Suresi: " + total_time)

            for svc in services:
                name = svc["name"]
                desc = SERVICE_DESCRIPTIONS.get(name, svc["description"])
                color = self._get_color(svc["active"])
                suggestion_text = ""
                if name in SERVICE_SUGGESTIONS:
                    stype, stext = SERVICE_SUGGESTIONS[name]
                    suggestion_text = stext

                if self._matches_filter(svc["active"], svc["sub"]):
                    self.liststore.append([
                        name,
                        svc["active"],
                        svc["sub"],
                        svc["load"],
                        blame_data.get(name, ""),
                        desc,
                        color,
                        suggestion_text,
                    ])

            count = len(self.liststore)
            self._set_log_text(f"{count} servis listelendi.")
        except Exception as e:
            self._set_log_text(f"Hata: {str(e)}")

    def _get_color(self, status):
        return STATUS_COLORS.get(status, "#000000")

    def _matches_filter(self, active_state, sub_state):
        f = self._current_filter
        if f == "all":
            return True
        if f == "active":
            return active_state == "active"
        if f == "inactive":
            return active_state == "inactive"
        if f == "disabled":
            return sub_state == "disabled" or active_state == "disabled"
        if f == "masked":
            return sub_state == "masked"
        return True

    def _on_filter_toggled(self, button, state):
        if not button.get_active():
            return
        self._current_filter = state
        self.load_all()

    def _get_selected_row(self):
        model, treeiter = self.selection.get_selected()
        if treeiter is not None:
            return model, treeiter, model[treeiter]
        return None, None, None

    def _on_selection_changed(self, *args):
        model, treeiter, row = self._get_selected_row()
        if row is None:
            self.detail_name.set_text("Servis secilmedi")
            self.detail_desc.set_text("Detaylar icin bir servis secin.")
            self.detail_suggestion.set_text("")
            return

        name = row[0]
        desc = row[5]
        suggestion = row[7]
        status_text = row[1]

        self.detail_name.set_markup(
            "<b>" + name + "</b>  —  " + status_text
        )
        self.detail_desc.set_text(desc)
        if suggestion:
            self.detail_suggestion.set_markup(
                "<span foreground='#1565c0'>" + suggestion + "</span>"
            )
        else:
            self.detail_suggestion.set_text("")

    def _get_selected_name(self):
        model, treeiter, row = self._get_selected_row()
        if row is not None:
            return row[0]
        return None

    def _on_enable(self, *args):
        name = self._get_selected_name()
        if not name:
            self._set_log_text("Lutfen bir servis secin.")
            return
        success, msg = self.manager.enable_service(name)
        self._set_log_text(msg)
        if success:
            self.load_all()

    def _on_disable(self, *args):
        name = self._get_selected_name()
        if not name:
            self._set_log_text("Lutfen bir servis secin.")
            return
        success, msg = self.manager.disable_service(name)
        self._set_log_text(msg)
        if success:
            self.load_all()

    def _on_mask(self, *args):
        name = self._get_selected_name()
        if not name:
            self._set_log_text("Lutfen bir servis secin.")
            return

        stype = SERVICE_SUGGESTIONS.get(name, (None, ""))[0]
        warning = ("Bu servis sistem icin KRITIK olarak isaretlenmistir. "
                   "Kapatmaniz sorunlara yol acabilir!") if stype == "kritik" else ""

        dialog = Gtk.MessageDialog(
            parent=self.builder.get_object("main_window"),
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.WARNING if stype == "kritik" else Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            message_format=f"'{name}' servisini maskelemek istediginize emin misiniz?"
        )
        if warning:
            dialog.format_secondary_text(warning)
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            success, msg = self.manager.mask_service(name)
            self._set_log_text(msg)
            if success:
                self.load_all()

    def _on_unmask(self, *args):
        name = self._get_selected_name()
        if not name:
            self._set_log_text("Lutfen bir servis secin.")
            return
        success, msg = self.manager.unmask_service(name)
        self._set_log_text(msg)
        if success:
            self.load_all()

    def _on_show_log(self, *args):
        name = self._get_selected_name()
        if not name:
            self._set_log_text("Lutfen bir servis secin.")
            return
        log = self.manager.get_journal_log(name)
        self._set_log_text(log)

    def _on_search_changed(self, *args):
        self.load_all()

    def _set_log_text(self, text):
        buffer = self.log_textview.get_buffer()
        buffer.set_text(text)
