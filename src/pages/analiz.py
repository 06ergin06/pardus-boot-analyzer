import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import threading
import cairo
import datetime
import re

from src.locale_mgr import tr
from src.utils import parse_blame_time, SAFE_TO_DISABLE_ONERI_SERVICES
from src.service_db import get_description

class AnalizPage:
    def __init__(self, controller):
        self.controller = controller
        self.window = controller.window
        self.manager = controller.manager
        self.set_status = controller.set_status
        self._ensure_auth = controller._ensure_auth
        self.load_all = controller.load_all

    def build_page_analiz(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        lbl_title = Gtk.Label(xalign=0)
        lbl_title.set_text(tr("sistem_baslangic_analizi"))
        lbl_title.get_style_context().add_class("content-title")
        box.pack_start(lbl_title, False, False, 0)
        
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_text(tr("analiz_alt_bilgi"))
        lbl_sub.get_style_context().add_class("content-subtitle")
        box.pack_start(lbl_sub, False, False, 0)
        
        h_split = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        box.pack_start(h_split, True, True, 0)
        
        vbox_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox_left.set_size_request(340, -1)
        h_split.pack_start(vbox_left, False, False, 0)
        
        # Left Card 1 - Boot Time
        self.card_boot = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.card_boot.get_style_context().add_class("card")
        vbox_left.pack_start(self.card_boot, False, False, 0)
        
        lbl_boot_title = Gtk.Label(xalign=0)
        lbl_boot_title.set_text(tr("acilis_suresi_ozeti"))
        lbl_boot_title.get_style_context().add_class("card-title")
        self.card_boot.pack_start(lbl_boot_title, False, False, 0)
        
        vbox_circle = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_circle.set_size_request(160, 160)
        vbox_circle.get_style_context().add_class("boot-circle-container")
        vbox_circle.set_valign(Gtk.Align.CENTER)
        vbox_circle.set_halign(Gtk.Align.CENTER)
        
        vbox_inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox_inner.set_valign(Gtk.Align.CENTER)
        vbox_inner.set_halign(Gtk.Align.CENTER)
        vbox_circle.pack_start(vbox_inner, True, False, 0)
        
        self.lbl_boot_val = Gtk.Label()
        self.lbl_boot_val.get_style_context().add_class("boot-time-value")
        self.lbl_boot_val.set_text("--")
        self.lbl_boot_val.set_justify(Gtk.Justification.CENTER)
        vbox_inner.pack_start(self.lbl_boot_val, False, False, 0)
        
        lbl_circle_sub = Gtk.Label()
        lbl_circle_sub.get_style_context().add_class("boot-time-label")
        lbl_circle_sub.set_text(tr("toplam_acilis"))
        lbl_circle_sub.set_justify(Gtk.Justification.CENTER)
        vbox_inner.pack_start(lbl_circle_sub, False, False, 0)
        
        self.card_boot.pack_start(vbox_circle, False, False, 8)
        
        self.breakdown_grid = Gtk.Grid(column_spacing=18, row_spacing=6)
        self.breakdown_grid.set_halign(Gtk.Align.CENTER)
        self.card_boot.pack_start(self.breakdown_grid, False, False, 4)
        
        # Left Card 2 - System Info & PDF Report
        self.card_sysinfo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.card_sysinfo.get_style_context().add_class("card")
        vbox_left.pack_start(self.card_sysinfo, False, False, 0)
        
        lbl_sys_title = Gtk.Label(xalign=0)
        lbl_sys_title.set_text(tr("sistem_bilgileri"))
        lbl_sys_title.get_style_context().add_class("card-title")
        self.card_sysinfo.pack_start(lbl_sys_title, False, False, 0)
        
        self.sysinfo_grid = Gtk.Grid(column_spacing=12, row_spacing=6)
        self.sysinfo_grid.set_margin_start(6)
        self.card_sysinfo.pack_start(self.sysinfo_grid, False, False, 4)
        
        self.btn_pdf = Gtk.Button(label=tr("pdf_olustur"))
        self.btn_pdf.get_style_context().add_class("primary")
        self.btn_pdf.connect("clicked", self._on_pdf_clicked)
        self.card_sysinfo.pack_start(self.btn_pdf, False, False, 4)
        
        # Right Card - Quick Optimization
        self.card_optimize = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.card_optimize.get_style_context().add_class("card")
        h_split.pack_start(self.card_optimize, True, True, 0)
        
        lbl_opt_title = Gtk.Label(xalign=0)
        lbl_opt_title.set_text(tr("baslangic_optimizasyonu"))
        lbl_opt_title.get_style_context().add_class("card-title")
        self.card_optimize.pack_start(lbl_opt_title, False, False, 0)
        
        lbl_opt_desc = Gtk.Label(xalign=0)
        lbl_opt_desc.set_markup(f"<span size='small' foreground='#565f89'>{tr('opt_alt_bilgi')}</span>")
        lbl_opt_desc.set_line_wrap(True)
        self.card_optimize.pack_start(lbl_opt_desc, False, False, 0)
        
        self.opt_savings_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.opt_savings_box.set_margin_top(4)
        self.opt_savings_box.set_margin_bottom(4)
        self.card_optimize.pack_start(self.opt_savings_box, False, False, 0)
        
        self.lbl_savings_val = Gtk.Label(xalign=0)
        self.lbl_savings_val.set_markup(f"{tr('hizlandirma_potansiyeli')}: <b>-- {tr('sec_lbl')}</b>")
        self.opt_savings_box.pack_start(self.lbl_savings_val, True, True, 0)
        
        self.btn_quick_optimize = Gtk.Button(label=tr("tum_onerilenleri_kapat"))
        self.btn_quick_optimize.get_style_context().add_class("success")
        self.btn_quick_optimize.connect("clicked", self._on_quick_optimize_clicked)
        self.card_optimize.pack_start(self.btn_quick_optimize, False, False, 4)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.card_optimize.pack_start(scrolled, True, True, 0)
        
        self.opt_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scrolled.add(self.opt_list_box)
        
        box.show_all()
        return box

    def _get_optimizable_services(self):
        try:
            enabled_map = self.manager.get_unit_file_states()
            blame_list, _ = self.manager.get_blame_data()
        except Exception:
            return [], 0.0
            
        optimizable_services = []
        total_savings_sec = 0.0
        
        for item in blame_list:
            name = item["name"]
            if name in SAFE_TO_DISABLE_ONERI_SERVICES:
                enabled_state = enabled_map.get(name, "unknown")
                if enabled_state in ("enabled", "enabled-runtime"):
                    sec = parse_blame_time(item["time"])
                    desc, tip, oneri = get_description(name)
                    optimizable_services.append({
                        "name": name,
                        "time_str": item["time"],
                        "seconds": sec,
                        "oneri": oneri or desc or "Kapatılması önerilen gereksiz hizmet."
                    })
                    total_savings_sec += sec
                    
        return optimizable_services, total_savings_sec

    def load_analysis_page(self):
        for child in self.breakdown_grid.get_children():
            self.breakdown_grid.remove(child)
            
        for child in self.sysinfo_grid.get_children():
            self.sysinfo_grid.remove(child)
            
        for child in self.opt_list_box.get_children():
            self.opt_list_box.remove(child)
            
        try:
            total_time, full_text = self.manager.get_total_boot_time()
            self.lbl_boot_val.set_text(self._format_time(total_time))
            
            components = {
                "firmware": tr("comp_firmware"),
                "loader": tr("comp_loader"),
                "kernel": tr("comp_kernel"),
                "initrd": tr("comp_initrd"),
                "userspace": tr("comp_userspace")
            }
            
            row = 0
            for key, name in components.items():
                match = re.search(r"([\d.]+(?:s|ms|min))\s*\((Donanım|Önyükleyici|Çekirdek|Başlangıç Arayüzü|Kullanıcı Alanı|" + key + r")\)", full_text) or re.search(r"([\d.]+(?:s|ms|min))\s*\(" + key + r"\)", full_text)
                if match:
                    val = match.group(1)
                    
                    lbl_name = Gtk.Label(xalign=0)
                    lbl_name.set_markup(f"<b>{name}:</b>")
                    self.breakdown_grid.attach(lbl_name, 0, row, 1, 1)
                    
                    lbl_val = Gtk.Label(xalign=0, label=self._format_time(val))
                    self.breakdown_grid.attach(lbl_val, 1, row, 1, 1)
                    row += 1
            
            info = self.manager.get_system_info()
            sys_items = [
                (tr("sys_os"), info["os"]),
                (tr("sys_kernel"), info["kernel"]),
                (tr("sys_ram"), info["ram"]),
                (tr("sys_uptime"), info["uptime"])
            ]
            
            s_row = 0
            for label, value in sys_items:
                lbl_l = Gtk.Label(xalign=1)
                lbl_l.set_markup(f"<b>{label}</b>")
                self.sysinfo_grid.attach(lbl_l, 0, s_row, 1, 1)
                
                lbl_v = Gtk.Label(xalign=0, label=value)
                lbl_v.set_ellipsize(Pango.EllipsizeMode.END if hasattr(Pango, 'EllipsizeMode') else 3)
                self.sysinfo_grid.attach(lbl_v, 1, s_row, 1, 1)
                s_row += 1
                
            optimizable_services, total_savings_sec = self._get_optimizable_services()
            
            if total_savings_sec > 0:
                self.lbl_savings_val.set_markup(
                    f"{tr('hizlandirma_potansiyeli')}: <span foreground='#198754' weight='bold'>~{total_savings_sec:.2f} {tr('sec_lbl')}</span>"
                )
                self.btn_quick_optimize.set_label(f"{tr('tum_onerilenleri_kapat')} (+{total_savings_sec:.1f} {tr('saniye_kazan')})")
                self.btn_quick_optimize.set_sensitive(True)
            else:
                self.lbl_savings_val.set_markup(f"{tr('hizlandirma_potansiyeli')}: <span color='#6c757d'><b>0.00 {tr('sec_lbl')}</b></span>")
                self.btn_quick_optimize.set_label(tr("sistem_optimize_edilmis"))
                self.btn_quick_optimize.set_sensitive(False)
                
            if optimizable_services:
                for item in optimizable_services:
                    name = item["name"]
                    time_str = item["time_str"]
                    oneri_text = item["oneri"]
                    
                    row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                    row_box.get_style_context().add_class("blame-row")
                    
                    vbox_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                    row_box.pack_start(vbox_info, True, True, 0)
                    
                    btn_go = Gtk.Button(label=name)
                    btn_go.set_relief(Gtk.ReliefStyle.NONE)
                    btn_go.set_halign(Gtk.Align.START)
                    btn_go.connect("clicked", lambda b, n=name: self._go_to_service(n))
                    vbox_info.pack_start(btn_go, False, False, 0)
                    
                    lbl_oneri = Gtk.Label(xalign=0)
                    lbl_oneri.set_markup(f"<span size='small' foreground='#888888'>{oneri_text}</span>")
                    lbl_oneri.set_line_wrap(True)
                    vbox_info.pack_start(lbl_oneri, False, False, 0)
                    
                    lbl_time = Gtk.Label(label=time_str)
                    lbl_time.get_style_context().add_class("badge-slow")
                    row_box.pack_start(lbl_time, False, False, 0)
                    
                    btn_disable_one = Gtk.Button()
                    img_dis = Gtk.Image.new_from_icon_name("media-playback-stop", Gtk.IconSize.BUTTON)
                    btn_disable_one.set_image(img_dis)
                    btn_disable_one.get_style_context().add_class("danger")
                    btn_disable_one.set_tooltip_text("Sadece bu hizmeti devre dışı bırak ve durdur")
                    btn_disable_one.connect("clicked", lambda b, n=name: self._disable_single_service(n))
                    row_box.pack_start(btn_disable_one, False, False, 0)
                    
                    self.opt_list_box.pack_start(row_box, False, False, 0)
            else:
                lbl_empty = Gtk.Label()
                lbl_empty.set_markup("<span foreground='#6c757d'>Kapatılması önerilen aktif bir hizmet bulunamadı. Sisteminiz en iyi durumda!</span>")
                lbl_empty.set_line_wrap(True)
                lbl_empty.set_margin_top(16)
                self.opt_list_box.pack_start(lbl_empty, False, False, 0)
                
        except Exception as e:
            self.lbl_boot_val.set_text("Hata")
            lbl = Gtk.Label(label=f"Analiz yüklenirken hata oluştu:\n{e}")
            self.opt_list_box.pack_start(lbl, False, False, 0)
            
        self.card_boot.show_all()
        self.card_sysinfo.show_all()
        self.opt_list_box.show_all()

    def _go_to_service(self, service_name):
        self.controller.sidebar_listbox.select_row(self.controller.sidebar_listbox.get_row_at_index(2))
        self.controller.view_combo.set_active(0)
        self.controller.filter_combo.set_active(0)
        self.controller.tip_combo.set_active(0)
        self.controller.search_entry.set_text("")
        
        def select_row():
            for i in range(len(self.controller.liststore)):
                if self.controller.liststore[i][0] == service_name:
                    self.controller.selection.select_path(Gtk.TreePath(i))
                    self.controller.treeview.scroll_to_cell(Gtk.TreePath(i), None, False, 0.5, 0.5)
                    break
            return False
            
        GLib.timeout_add(100, select_row)

    def _disable_single_service(self, name):
        dlg = Gtk.MessageDialog(
            parent=self.window, flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO,
            message_format=f"'{name}' hizmetini kapatmak istiyor musunuz?"
        )
        dlg.format_secondary_text("Bu işlem hizmeti devre dışı bırakacak (disable) ve durduracaktır (stop).")
        resp = dlg.run()
        dlg.destroy()
        
        if resp == Gtk.ResponseType.YES:
            if not self._ensure_auth():
                self.set_status(tr("yetki_iptal"))
                return
            self.set_status(f"'{name}' hizmeti kapatılıyor...")
            def task():
                ok1, msg1 = self.manager.disable_service(name)
                ok2, msg2 = self.manager.stop_service(name)
                GLib.idle_add(done, ok1 and ok2, f"'{name}' başarıyla kapatıldı." if ok1 and ok2 else f"Hata: {msg1} {msg2}")
                
            def done(ok, msg):
                self.set_status(msg)
                self.load_all()
                self.load_analysis_page()
                
            threading.Thread(target=task, daemon=True).start()

    def _on_quick_optimize_clicked(self, button):
        opt_svcs, _ = self._get_optimizable_services()
        services_to_disable = [s["name"] for s in opt_svcs]
                    
        if not services_to_disable:
            self.set_status(tr("kap_hizmet_yok"))
            return
            
        dlg = Gtk.MessageDialog(
            parent=self.window, flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO,
            message_format="Önerilen Tüm Hizmetleri Kapatmak İstiyor musunuz?"
        )
        
        svc_list_str = "\n".join(f"- {s}" for s in services_to_disable)
        dlg.format_secondary_text(
            "Aşağıdaki gereksiz hizmetler devre dışı bırakılacak ve durdurulacaktır:\n\n"
            f"{svc_list_str}\n\n"
            "Bu işlem sisteminizin açılışını hızlandıracaktır. Yetkilendirme şifresi istenecektir."
        )
        
        resp = dlg.run()
        dlg.destroy()
        
        if resp != Gtk.ResponseType.YES:
            return
            
        if not self._ensure_auth():
            self.set_status(tr("yetki_iptal"))
            return
            
        self._run_quick_optimize_batch(services_to_disable)

    def _run_quick_optimize_batch(self, services_to_disable):
        loader = Gtk.Dialog(title="Sistem Optimize Ediliyor", parent=self.window, flags=Gtk.DialogFlags.MODAL)
        loader.set_default_size(320, 140)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(18)
        box.set_margin_end(18)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        loader.get_content_area().add(box)
        
        lbl = Gtk.Label(label=tr("onerilenler_kapatiliyor_bekleyin"))
        box.pack_start(lbl, False, False, 0)
        
        spinner = Gtk.Spinner()
        box.pack_start(spinner, True, True, 0)
        spinner.start()
        
        loader.show_all()
        
        def task():
            self.manager.create_backup()
            ok, msg = self.manager.apply_profile_batch(enable_list=[], disable_list=services_to_disable)
            GLib.idle_add(done, ok, msg)
            
        def done(ok, msg):
            spinner.stop()
            loader.destroy()
            self.set_status(msg)
            if ok:
                info = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK,
                    message_format="Optimizasyon Tamamlandı!"
                )
                info.format_secondary_text("Önerilen tüm gereksiz hizmetler başarıyla kapatıldı.")
                info.run()
                info.destroy()
                self.load_all()
                self.load_analysis_page()
            else:
                err = Gtk.MessageDialog(
                    parent=self.window, flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
                    message_format="Optimizasyon Sırasında Hata Oluştu",
                )
                err.format_secondary_text(msg)
                err.run()
                err.destroy()
                
        threading.Thread(target=task, daemon=True).start()

    # --- PDF Report Generation (Cairo) ---
    def _on_pdf_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="PDF Raporu Kaydet", parent=self.window,
            action=Gtk.FileChooserAction.SAVE,
            buttons=(tr("iptal"), Gtk.ResponseType.CANCEL, tr("kaydet"), Gtk.ResponseType.ACCEPT)
        )
        dialog.get_widget_for_response(Gtk.ResponseType.ACCEPT).get_style_context().add_class("primary")
        
        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("PDF Dosyaları")
        filter_pdf.add_mime_type("application/pdf")
        filter_pdf.add_pattern("*.pdf")
        dialog.add_filter(filter_pdf)
        
        dialog.set_current_name("Pardus_Baslangic_Raporu.pdf")
        
        resp = dialog.run()
        path = dialog.get_filename()
        dialog.destroy()
        
        if resp == Gtk.ResponseType.ACCEPT and path:
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            self.set_status(tr("pdf_olusturuluyor"))
            
            def task():
                try:
                    print_op = Gtk.PrintOperation()
                    print_op.set_export_filename(path)
                    print_op.connect("draw-page", self._draw_pdf_page)
                    print_op.set_n_pages(1)
                    GLib.idle_add(run_print_op, print_op)
                except Exception as e:
                    GLib.idle_add(self.set_status, f"{tr('pdf_hatasi')}{e}")
                    
            def run_print_op(print_op):
                try:
                    result = print_op.run(Gtk.PrintOperationAction.EXPORT, self.window)
                    if result == Gtk.PrintOperationResult.APPLY:
                        self.set_status(f"PDF Raporu kaydedildi: {path}")
                        info = Gtk.MessageDialog(
                            parent=self.window, flags=Gtk.DialogFlags.MODAL,
                            type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK,
                            message_format="PDF Raporu Oluşturuldu!"
                        )
                        info.format_secondary_text(f"Sistem başlangıç raporunuz başarıyla kaydedildi:\n\n{path}")
                        info.run()
                        info.destroy()
                    else:
                        self.set_status(tr("pdf_tamamlanamadi"))
                except Exception as e:
                    self.set_status(f"{tr('pdf_hatasi')}{e}")
                    
            threading.Thread(target=task, daemon=True).start()

    def _draw_pdf_page(self, operation, context, page_nr):
        cr = context.get_cairo_context()
        
        cr.set_source_rgb(0.05, 0.5, 0.7)
        cr.rectangle(50, 50, 495, 45)
        cr.fill()
        
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(14)
        cr.move_to(70, 78)
        cr.show_text("PARDUS BAŞLANGIÇ YÖNETİCİSİ — ANALİZ RAPORU")
        
        date_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        cr.set_font_size(9)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.move_to(430, 75)
        cr.show_text(date_str)
        
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        cr.move_to(50, 125)
        cr.show_text(tr("pdf_sistem_ozeti"))
        
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.set_line_width(1)
        cr.move_to(50, 132)
        cr.line_to(545, 132)
        cr.stroke()
        
        info = self.manager.get_system_info()
        total_time, full_text = self.manager.get_total_boot_time()
        
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(10)
        
        y = 150
        cr.move_to(60, y); cr.show_text(f"İşletim Sistemi: {info['os']}")
        cr.move_to(300, y); cr.show_text(f"Çekirdek (Kernel): {info['kernel']}")
        
        y = 170
        cr.move_to(60, y); cr.show_text(f"Bellek (RAM): {info['ram']}")
        cr.move_to(300, y); cr.show_text(f"Çalısma Süresi: {info['uptime']}")
        
        y = 190
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.move_to(60, y); cr.show_text(f"Toplam Açılış Süresi: {total_time}")
        
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        cr.move_to(50, 230)
        cr.show_text("2. Açılış Aşamaları Dağılımı")
        
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.move_to(50, 237)
        cr.line_to(545, 237)
        cr.stroke()
        
        components = {
            "firmware": "Donanım (Firmware)",
            "loader": "Önyükleyici (Loader)",
            "kernel": "Çekirdek (Kernel)",
            "initrd": "Başlangıç Arayüzü (Initrd)",
            "userspace": "Kullanıcı Alanı (Userspace)"
        }
        
        y = 255
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(10)
        
        for key, name in components.items():
            match = re.search(r"([\d.]+(?:s|ms|min))\s*\((Donanım|Önyükleyici|Çekirdek|Başlangıç Arayüzü|Kullanıcı Alanı|" + key + r")\)", full_text) or re.search(r"([\d.]+(?:s|ms|min))\s*\(" + key + r"\)", full_text)
            if match:
                val = match.group(1)
                cr.move_to(70, y); cr.show_text(f"•  {name}:")
                cr.move_to(250, y); cr.show_text(val)
                y += 18
                
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        cr.move_to(50, y + 15)
        cr.show_text(tr("pdf_yavas_hizmetler"))
        
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.move_to(50, y + 22)
        cr.line_to(545, y + 22)
        cr.stroke()
        
        enabled_map = self.manager.get_unit_file_states()
        blame_list, _ = self.manager.get_blame_data()
        
        y += 38
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(10)
        
        for item in blame_list[:5]:
            cr.move_to(70, y); cr.show_text(f"•  {item['name']}:")
            cr.move_to(350, y); cr.show_text(item['time'])
            y += 16
            
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        cr.move_to(50, y + 15)
        cr.show_text(tr("pdf_opt_onerileri"))
        
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.move_to(50, y + 22)
        cr.line_to(545, y + 22)
        cr.stroke()
        
        optimizable_services, total_savings_sec = self._get_optimizable_services()
        y += 40
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(10)
        
        if total_savings_sec > 0:
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_source_rgb(0.1, 0.5, 0.3)
            cr.move_to(60, y)
            cr.show_text(f"{tr('hizlandirma_potansiyeli')}: ~{total_savings_sec:.2f} {tr('sec_gained_lbl')}")
            cr.set_source_rgb(0.3, 0.3, 0.3)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            
            y += 20
            for item in optimizable_services[:4]:
                cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                cr.move_to(70, y); cr.show_text(f"- {item['name']} ({item['time_str']})")
                cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                y += 15
                cr.move_to(85, y); cr.show_text(item['oneri'])
                y += 20
        else:
            cr.move_to(60, y)
            cr.show_text(tr("pdf_no_opt"))
            y += 20
            
        cr.set_source_rgb(0.6, 0.6, 0.6)
        cr.set_font_size(8)
        cr.move_to(50, 780)
        cr.line_to(545, 780)
        cr.stroke()
        cr.move_to(50, 792)
        cr.show_text(tr("pdf_footer"))
        cr.move_to(480, 792)
        cr.show_text(tr("pdf_sayfa_1_1"))

    # --- Page 2: Autostart ---
