import os
import locale
import json

CONFIG_DIR = os.path.expanduser("~/.config/pardus-boot-analyzer")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

# Default: auto-detect language from system environment variables
LANG = "tr"
try:
    sys_lang = os.environ.get("LANG", "tr").split(".")[0].split("_")[0].lower()
    if sys_lang in ("en", "tr"):
        LANG = sys_lang
except Exception:
    pass

# Load saved language preference if exists
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            if cfg.get("lang") in ("en", "tr"):
                LANG = cfg["lang"]
    except Exception:
        pass

def save_lang_pref(lang):
    global LANG
    LANG = lang
    try:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"lang": lang}, f)
    except Exception:
        pass
    init_locale(lang)

FALLBACK_DICT = {   'en': {   'about': 'About',
              'about_comments': 'Pardus Boot Analyzer and Optimization Tool',
              'aciklama': 'Description',
              'aciklama_yok': 'No description available.',
              'acilis_ayari': 'Boot Config',
              'acilis_calisacak': 'Will Start at Boot',
              'acilis_calismayacak': 'Will Not Start at Boot',
              'acilis_calistir': 'Start at Boot',
              'acilis_calistirma': "Don't Start",
              'acilis_kapatma_dep': 'Disabling this service at boot might affect the following dependent services:\n'
                                    '\n'
                                    '{dep_list_str}\n'
                                    '\n'
                                    'Do you want to proceed?',
              'acilis_kapatma_soru': 'Do you want to disable this service at boot?',
              'acilis_suresi': 'Boot Time',
              'acilis_suresi_ozeti': 'Boot Time Summary',
              'adi': 'Name',
              'alt_durum': 'Sub State',
              'analiz_alt_bilgi': 'Analyze your system boot time and manage recommended services safely.',
              'autostart_subtitle': 'Manage applications configured to start automatically when your session begins.',
              'avahi_desc': 'Local Network Discovery (Avahi)',
              'bagimliliklar': 'Dependencies',
              'basariyla_kapatildi': 'successfully disabled.',
              'baslangic_optimizasyonu': 'Boot Optimization',
              'baslangica_eklendi': 'added to startup applications.',
              'baslatma_sorusu': 'starting this service in the current session.\n'
                                 'This service is not configured to run at boot.\n'
                                 '\n'
                                 'Do you want to both start it now and enable it for future boots?',
              'bellek': 'Memory',
              'bilgi_ipucu': '<b>Info:</b> <i>Boot Setup</i> determines if the service runs automatically when the '
                             'computer starts; <i>Current State</i> indicates if it is currently active in the '
                             'background.',
              'bluetooth_desc': 'Bluetooth Support',
              'cekirdek_surumu': 'Kernel Version',
              'cift_yon_baslatma': 'Dual Action Suggestion (Start)',
              'cift_yon_durdurma': 'Dual Action Suggestion (Stop)',
              'cift_yon_etkinlestirme': 'Dual Action Suggestion (Enable)',
              'cift_yon_kapatma': 'Dual Action Suggestion (Disable)',
              'comp_firmware': 'Firmware',
              'comp_initrd': 'Initrd (Early Boot)',
              'comp_kernel': 'Kernel',
              'comp_loader': 'Loader',
              'comp_userspace': 'Userspace',
              'cups_browsed_desc': 'Network Printer Discoverer',
              'cups_service_desc': 'Printer Service (CUPS)',
              'degistirilemez': 'Immutable',
              'devices': 'Devices',
              'diger_islemler': 'Other Operations',
              'dolayli_indirekt': 'Indirect',
              'durdurma_sorusu': 'stopping this service in the current session.\n'
                                 'This service is configured to run at boot.\n'
                                 '\n'
                                 'Do you want to both stop it now and disable it for future boots?',
              'durum': 'State',
              'durum_bilinmiyor': 'Unknown state',
              'etkinlestirme_sorusu': 'enabling autostart for this service.\n'
                                      'This service is not currently running.\n'
                                      '\n'
                                      'Do you want to both enable it and start it now?',
              'filter_active': 'Active',
              'filter_all': 'All States',
              'filter_disabled': 'Disabled',
              'filter_inactive': 'Inactive',
              'filter_masked': 'Masked',
              'firmware': 'Hardware (Firmware)',
              'gecikme': 'Delay',
              'gecikme_guncellendi': 'Delay time updated.',
              'gecis_yapiyor': 'Transitioning',
              'geri_yukle': 'Restore',
              'geri_yukleme_basarili': 'Selected backup successfully restored. You may need to restart the system.',
              'goz_at': 'Browse',
              'guncelleme_denetle': 'Check for Updates',
              'gunluk_kaydi': 'Logs',
              'hata': 'Error',
              'hata_dosya_yok': 'Error: Filename not specified.',
              'hata_log_yetki': 'Authentication required to view logs...',
              'hizlandirma_potansiyeli': 'Speed-up Potential',
              'hizmet_adi': 'Service Name',
              'hizmet_kapatiliyor': 'service is disabling...',
              'hizmet_kapatma_dep': 'Disabling this service might affect the following dependent services:\n'
                                    '\n'
                                    '{dep_list_str}\n'
                                    '\n'
                                    'Do you want to proceed?',
              'hizmet_kapatma_soru': 'Do you want to disable this service?',
              'hizmet_kurali': 'service rules',
              'hizmet_kurallari_lbl': 'Service Rules:',
              'hizmet_kurallari_sub': 'On = Enabled, Off = Disabled',
              'hizmet_listesi_guncellendi': 'Service list updated.',
              'hizmet_sayisi': 'services',
              'hizmet_secilmedi': 'No Service Selected',
              'hizmet_secilmedi_desc': 'Select a service from the list to view details.',
              'hizmetin_yedegi': 'services backed up',
              'hizmetler_subtitle': 'Manage, enable, or disable system services and hardware units.',
              'hizmetler_uygun_detay': 'The services startup configuration already matches this profile.',
              'ikisini_de_kapat': 'Close Both (Recommended)',
              'iptal': 'Cancel',
              'islemci': 'Processor',
              'isletim_sistemi': 'Operating System',
              'kap_hizmet_yok': 'No services to disable found.',
              'kapatma_sorusu': 'disabling autostart for this service.\n'
                                'This service is currently running in the background.\n'
                                '\n'
                                'Do you want to both disable it at boot and stop it now?',
              'kaydet': 'Save',
              'kaydetme_hatasi': 'Saving error: ',
              'kernel': 'Kernel',
              'komut': 'Command',
              'kritik_hizmet': 'CRITICAL SERVICE',
              'kritik_maske_uyarisi': '\n'
                                      '\n'
                                      'This service is marked as CRITICAL for the system. Masking it might lead to '
                                      'system instability or boot failure!',
              'kritik_uyari': '\n'
                              '\n'
                              'This service is marked as CRITICAL for the system. Masking it might make your system '
                              'unstable or unbootable!',
              'kullanici_onerisi': 'USER SUGGESTION',
              'kullanici_ozel_profilleri': 'User Custom Profiles',
              'lisans': 'License: GPLv3',
              'loader': 'Bootloader (Loader)',
              'log_bulunamadi': 'No log records found for this service.',
              'maske_sorusu': 'Do you want to mask this service?',
              'maskele': 'Mask',
              'maskelenmis_kapali': 'Masked (Off)',
              'maskeyi_kaldir': 'Unmask',
              'mevcut_durumu_kaydet': 'Save Current State as Profile',
              'modem_desc': 'Cellular Modem Controller',
              'mysql_desc': 'MySQL / MariaDB Database',
              'no_autostart_apps': 'No startup applications found.',
              'no_backups_found': 'No restore points found.',
              'no_custom_profiles': 'No custom profiles found.',
              'oneri': 'Suggestion',
              'onerilenler_kapatiliyor_bekleyin': 'Disabling recommended services, please wait...',
              'opt_alt_bilgi': 'Speed up boot by disabling unnecessary services with a single click.',
              'other': 'Other',
              'ozel_profil_olusturuldu': "Custom profile '{}' successfully created.",
              'ozel_profil_silindi': 'Custom profile deleted.',
              'ozel_profilim': 'My Custom Profile',
              'pdf_acilis_ozeti': '1. Boot Time Summary',
              'pdf_baslik': 'Pardus Boot Analysis Report',
              'pdf_donanim_bilgileri': '2. System Hardware and Version Info',
              'pdf_footer': 'Pardus Boot Manager — System Analysis Report',
              'pdf_hatasi': 'PDF Error: ',
              'pdf_kaydedildi': 'PDF Report successfully generated at:',
              'pdf_no_opt': 'No active unnecessary services recommended to disable. Your system is in optimal state!',
              'pdf_olustur': 'Generate PDF Report',
              'pdf_olusturuluyor': 'Generating PDF Report...',
              'pdf_opt_onerileri': '4. Boot Optimization Suggestions',
              'pdf_sayfa_1_1': 'Page 1 / 1',
              'pdf_sistem_ozeti': '1. System Summary',
              'pdf_tamamlanamadi': 'PDF generation could not be completed.',
              'pdf_tarih': 'Generation Date',
              'pdf_yavas_hizmetler': '3. Top 5 Slowest Services',
              'postgresql_desc': 'PostgreSQL Database',
              'prof_dev_desc': 'Designed for software developers. Docker, SSH, and database services are automatically '
                               'enabled. Unnecessary services like printers are disabled.',
              'prof_dev_name': 'Developer Mode',
              'prof_min_desc': 'To boot the system as fast and lightweight as possible. Disables all additional '
                               'services except network and basic system security. Saves laptop battery.',
              'prof_min_name': 'Minimum Services',
              'prof_office_desc': 'Ideal settings for office tasks and daily use. Printer, Bluetooth, and network '
                                  'services remain enabled.',
              'prof_office_name': 'Office Mode',
              'profil_adi_girin_hata': 'Please enter a profile name.',
              'profil_adi_lbl': 'Profile Name:',
              'profil_adi_placeholder': 'e.g., Code & Office Mix',
              'profil_bagimlilik_uyarisi': 'Profile Application Dependency Warning',
              'profil_basariyla_uygulandi': 'Profile Applied Successfully!',
              'profil_okuma_hatasi': 'Profile reading error: ',
              'profil_uygula_aciklama': 'This action will apply boot configuration presets to multiple system '
                                        'services.',
              'profil_uygula_bagimlilik_mesaji': 'Applying this profile might affect the following active and '
                                                 'dependent services:\n'
                                                 '\n',
              'profil_uygula_soru': 'profile?',
              'profil_uygulama_hatasi': 'Error Occurred While Applying Profile',
              'profil_uygulaniyor': 'Applying Profile',
              'profil_uygulaniyor_bekleyin': 'Applying service profile, please wait...',
              'profil_zaten_uygulanmis': 'Profile Already Applied',
              'profili_kaydedildi': 'profile saved.',
              'profili_kaydet_title': 'Save Profile',
              'profili_uygula': 'Apply Profile',
              'profiller_subtitle': 'Optimize your system with a single click based on specific usage scenarios.',
              'profiller_title': 'System Boot Profiles',
              'sadece_acilis_etkinlestir': 'Only Enable at Boot',
              'sadece_baslangic_degistir': 'Only Change Boot Config',
              'sadece_simdi_baslat': 'Only Start Now',
              'sadece_simdi_durdur': 'Only Stop Current Runtime',
              'saniye_kazan': 'sec Gain',
              'search_placeholder': 'Search...',
              'sec_gained_lbl': 'seconds can be saved!',
              'sec_lbl': 'seconds',
              'secilen_servis_yok': 'Select a service.',
              'secileni_geri_yukle': 'Restore Selected',
              'secileni_sil': 'Delete Selected',
              'services': 'Services',
              'side_analiz': 'Boot Analysis',
              'side_autostart': 'Startup Applications',
              'side_hizmetler': 'System Services',
              'side_profiller': 'Service Profiles',
              'side_title_sub': 'Boot Manager',
              'sifre_placeholder': 'Administrator password',
              'sifreyi_goster': 'Show Password',
              'sil_onay_app': 'Are you sure you want to delete the selected application?',
              'silme_hatasi': 'Deletion error: ',
              'simdi_baslat': 'Start Now',
              'simdi_baslat_ve_etkinlestir': 'Start Now & Enable at Boot',
              'simdi_durdur': 'Stop Now',
              'simdiki_durum': 'Current State',
              'sistem_baslangic_analizi': 'System Boot Analysis',
              'sistem_bilgileri': 'System Information',
              'sistem_geri_yukleme_noktalari': 'System Restore Points',
              'sistem_optimize_edilmis': 'Your System is Already Optimized',
              'sistem_uygun_durumda': 'The system boot configuration already matches this profile.',
              'ssh_desc': 'SSH Remote Access',
              'statik_sabit': 'Static (Fixed)',
              'su_an_calisiyor': 'Running',
              'su_an_durduruldu': 'Stopped',
              'subtitle': 'System Boot Analysis and Optimization Tool',
              'sure': 'Time',
              'sys_kernel': 'Kernel:',
              'sys_os': 'OS:',
              'sys_ram': 'RAM:',
              'sys_uptime': 'Uptime:',
              'tab_analiz': 'Boot Analysis',
              'tab_custom_command': 'Add Custom Command',
              'tab_desktop_apps': 'Desktop Applications',
              'tab_hizmetler': 'Service Management',
              'tab_uygulamalar': 'Startup Applications',
              'tab_yedek': 'Restore Point',
              'tahmini_kazanc': 'Estimated Savings',
              'tarih_saat': 'Date / Time',
              'tip_all': 'All Categories',
              'tip_critical': 'Do Not Disable',
              'tip_required': 'Required',
              'tip_suggestion': 'Can Be Disabled',
              'title': 'Pardus Boot Manager',
              'toplam_acilis': 'Total Boot Time',
              'tum_onerilenleri_kapat': 'Disable All Recommended',
              'tur': 'Type',
              'userspace': 'Userspace',
              'uyg_ekle_ad_bos': 'Error: Application name cannot be empty.',
              'uyg_ekle_komut_bos': 'Error: Command field cannot be empty.',
              'ekle': 'Add',
              'baslangic_uygulamasi_ekle': 'Add Startup Application',
              'uygula': 'Apply',
              'uygulama_adi': 'Application Name',
              'uygulama_aktiflik_guncellendi': 'Application autostart state updated.',
              'uygulama_duzenle': 'Edit Application',
              'uygulama_kaldirildi': 'Application removed from list.',
              'uygulama_ara_placeholder': 'Search application...',
              've_daha_fazla_hizmet': 'and {} more services...\n',
              'action_acilis_kapat': 'Disable at Boot',
              'action_acilis_ac': 'Enable at Boot',
              'action_simdi_baslat': 'Start Now',
              'action_simdi_durdur': 'Stop Now',
              'action_maskele': 'Mask',
              'action_maskeyi_kaldir': 'Unmask',
              'action_baslatildi': "'{}' action started for '{}'...",
              'action_batch_baslatildi': "'{}' actions started for '{}'...",
              'action_basarili': '{} successful',
              'action_hata': '{} Error: {}',
              'action_bilinmiyor': 'Unknown action: {}',
              'action_dep_uyari': '⚠️ WARNING: Stopping this service might affect the following dependent services:\n{}',
              'disable_boot_running_sec': "You are disabling '{}' from starting at boot.\nThis service is currently active in the background.\n\nDo you also want to stop the running process now?",
              'disable_boot_stopped_dep': "Disabling '{}' at boot might affect these dependent services:\n\n{}\n\nDo you want to proceed?",
              'disable_boot_stopped_title': "Disable '{}' at Boot?",
              'enable_boot_stopped_sec': "You are enabling '{}' to start at boot.\nThis service is not currently running.\n\nDo you also want to start it now in this session?",
              'stop_enabled_sec': "You are stopping '{}' in the current session.\nThis service is configured to start at boot.\n\nDo you also want to disable it for future boots?",
              'start_disabled_sec': "You are starting '{}' in the current session.\nThis service is not configured to run at boot.\n\nDo you also want to enable it for future boots?",
              'log_dialog_title': 'Log: {}',
              'log_loading': 'Loading logs, please wait...',
              'log_no_perm': 'You do not have permission to read logs.\n\nYou must enter your administrator password to view logs.',
              'log_error': 'Error: {}',
              'dep_dialog_title': 'Dependencies: {}',
              'dep_info_lbl': '<b>{}</b> dependency tree with other system units:',
              'dep_loading': 'Loading dependency tree...',
              'dep_not_found': 'No dependency information found.',
              'dep_error': 'Error: {}',
              'dialog_close': 'Close',
              'select_service_first': 'Select a service first.',
              'restore_point_name': 'Restore Point ({})',
              'view_devices': 'Device Units (.device)',
              'view_others': 'Others (Socket, Target, Mount)',
              'view_services': 'Services (.service)',
              'yazici_kullanimi': 'Can be disabled if you do not use a printer.',
              'yazilim_guncelleme': 'Checking for software updates...',
              'yedek_adi_girin': 'Enter restore point name:',
              'yedek_basarili': 'Restore point successfully created.',
              'yedek_bulunamadi': 'No backups found.',
              'yedek_don_aciklama': 'This action will restore system services configuration to the exact state when '
                                    'the backup was created.',
              'yedek_don_soru': 'Do you want to restore to this backup point?',
              'yedek_geri_yukleniyor': 'Restoring Backup',
              'yedek_noktalari': 'Restore Points',
              'yedek_noktasi_silindi': 'Restore point deleted.',
              'yedek_olustur': 'Create Restore Point',
              'yedek_olusturuldu': 'Restore point created.',
              'yedek_sil_soru': 'Are you sure you want to delete this restore point?',
              'yedek_silindi': 'Selected backup successfully deleted.',
              'yedek_yukleniyor_bekleyin': 'Restoring system backup, please wait...',
              'yeni_ozel_profil_btn': 'Create New Custom Profile',
              'yeni_profil_adi_girin': 'Enter new profile name:',
              'yeni_uygulama_ekle_btn': '+ Add Application',
              'yeni_uygulamalar': 'Add New Application',
              'yeni_yedek_noktasi_btn': 'Create New Restore Point',
              'yenile': 'Refresh',
              'yetki_alt_bilgi': 'Please enter your administrator (sudo) password to manage system services.',
              'yetki_gerekiyor': 'Administrator Privileges Required',
              'yetki_iptal': 'Authorization cancelled.',
              'yetki_yok': 'You do not have permission to read logs.\n'
                           '\n'
                           'You must enter your administrator password to view logs.',
              'yetkilendir': 'Authorize',
              'yetkilendirildi': 'Authorized, loading logs...'},
    'tr': {   'about': 'Hakkında',
              'about_comments': 'Pardus Başlangıç Analiz ve Optimizasyon Aracı',
              'aciklama': 'Açıklama',
              'aciklama_yok': 'Açıklama mevcut değil.',
              'acilis_ayari': 'Açılış Ayarı',
              'acilis_calisacak': 'Açılışta Çalışacak',
              'acilis_calismayacak': 'Açılışta Çalışmayacak',
              'acilis_calistir': 'Açılışta Çalıştır',
              'acilis_calistirma': 'Açılışta Çalıştırma',
              'acilis_kapatma_dep': 'Bu hizmeti açılışta kapatmak, ona bağımlı şu hizmetleri etkileyebilir:\n'
                                    '\n'
                                    '{dep_list_str}\n'
                                    '\n'
                                    'Devam etmek istiyor musunuz?',
              'acilis_kapatma_soru': 'Hizmetini Açılışta Kapatmak İstiyor musunuz?',
              'acilis_suresi': 'Açılış Süresi',
              'acilis_suresi_ozeti': 'Açılış Süresi Özeti',
              'adi': 'Adı',
              'alt_durum': 'Alt Durum',
              'analiz_alt_bilgi': 'Sisteminizin açılış süresini ve kapatılması güvenli olan önerilen hizmetleri '
                                  'yönetin.',
              'autostart_subtitle': 'Kullanıcı oturumu başladığında otomatik olarak çalışacak uygulamaları yönetin.',
              'avahi_desc': 'Yerel Ağ Keşfi (Avahi)',
              'bagimliliklar': 'Bağımlılıklar',
              'basariyla_kapatildi': 'başarıyla kapatıldı.',
              'baslangic_optimizasyonu': 'Başlangıç Optimizasyonu',
              'baslangica_eklendi': 'başlangıç uygulamalarına eklendi.',
              'baslatma_sorusu': 'hizmetini şu anki oturumda başlatıyorsunuz.\n'
                                 'Bu hizmet başlangıçta otomatik çalışacak şekilde ayarlanmamış.\n'
                                 '\n'
                                 'Hem şimdi başlatıp hem de sonraki açılışlarda otomatik başlamasını '
                                 '(etkinleştirilmesini) ister misiniz?',
              'bellek': 'Bellek',
              'bilgi_ipucu': '<b>Bilgi:</b> <i>Açılış Ayarı</i> servisin bilgisayar açılırken otomatik çalışıp '
                             'çalışmayacağını; <i>Şimdiki Durum</i> ise servisin şu saniyede arka planda aktif '
                             '(RAM/İşlemci tüketiyor) olup olmadığını belirler.',
              'bluetooth_desc': 'Bluetooth Desteği',
              'cekirdek_surumu': 'Çekirdek Sürümü',
              'cift_yon_baslatma': 'Çift Yönlü İşlem Önerisi (Başlatma)',
              'cift_yon_durdurma': 'Çift Yönlü İşlem Önerisi (Durdurma)',
              'cift_yon_etkinlestirme': 'Çift Yönlü İşlem Önerisi (Etkinleştirme)',
              'cift_yon_kapatma': 'Çift Yönlü İşlem Önerisi (Kapatma)',
              'comp_firmware': 'Donanım (Firmware)',
              'comp_initrd': 'Başlangıç Arayüzü (Initrd)',
              'comp_kernel': 'Çekirdek (Kernel)',
              'comp_loader': 'Önyükleyici (Loader)',
              'comp_userspace': 'Kullanıcı Alanı (Userspace)',
              'cups_browsed_desc': 'Ağ Yazıcısı Bulucu',
              'cups_service_desc': 'Yazıcı Servisi (CUPS)',
              'degistirilemez': 'Değiştirilemez',
              'devices': 'Cihazlar',
              'diger_islemler': 'Diğer İşlemler',
              'dolayli_indirekt': 'Dolaylı (İndirekt)',
              'durdurma_sorusu': 'hizmetini şu anki oturumda durduruyorsunuz.\n'
                                 'Bu hizmet başlangıçta otomatik çalışacak şekilde ayarlanmış.\n'
                                 '\n'
                                 'Hem şu an durdurup hem de bir sonraki açılışlarda çalışmamasını (devre dışı '
                                 'bırakılmasını) ister misiniz?',
              'durum': 'Durum',
              'durum_bilinmiyor': 'Durum bilinmiyor',
              'etkinlestirme_sorusu': 'hizmetinin açılışta otomatik başlamasını etkinleştiriyorsunuz.\n'
                                      'Bu hizmet şu an arka planda çalışmıyor.\n'
                                      '\n'
                                      'Açılışta etkinleştirirken aynı zamanda şu anki oturumda hemen başlatmak ister '
                                      'misiniz?',
              'filter_active': 'Aktif',
              'filter_all': 'Tüm Durumlar',
              'filter_disabled': 'Devre Dışı',
              'filter_inactive': 'Pasif',
              'filter_masked': 'Maskeli',
              'firmware': 'Donanım (Firmware)',
              'gecikme': 'Gecikme',
              'gecikme_guncellendi': 'Gecikme süresi güncellendi.',
              'gecis_yapiyor': 'Geçiş Yapıyor',
              'geri_yukle': 'Geri Yükle',
              'geri_yukleme_basarili': 'Seçilen yedek başarıyla geri yüklendi. Sistemi yeniden başlatmanız '
                                       'gerekebilir.',
              'goz_at': 'Göz At',
              'guncelleme_denetle': 'Güncelleştirmeleri Denetle',
              'gunluk_kaydi': 'Günlük Kaydı',
              'hata': 'Hata',
              'hata_dosya_yok': 'Hata: Dosya adı belirtilmedi.',
              'hata_log_yetki': 'Logları görüntülemek için yetkilendirme gerekiyor...',
              'hizlandirma_potansiyeli': 'Hızlandırma Potansiyeli',
              'hizmet_adi': 'Hizmet Adı',
              'hizmet_kapatiliyor': 'hizmeti kapatılıyor...',
              'hizmet_kapatma_dep': 'Bu hizmeti kapatmak, ona bağımlı çalışan şu hizmetleri etkileyebilir:\n'
                                    '\n'
                                    '{dep_list_str}\n'
                                    '\n'
                                    'Devam etmek istiyor musunuz?',
              'hizmet_kapatma_soru': 'Hizmetini Kapatmak İstiyor musunuz?',
              'hizmet_kurali': 'hizmet kuralı',
              'hizmet_kurallari_lbl': 'Hizmet Kuralları:',
              'hizmet_kurallari_sub': 'Açık = Etkinleştirilir, Kapalı = Devre dışı bırakılır',
              'hizmet_listesi_guncellendi': 'Hizmet listesi güncellendi.',
              'hizmet_sayisi': 'servis',
              'hizmet_secilmedi': 'Hizmet Seçilmedi',
              'hizmet_secilmedi_desc': 'Detayları görmek için listeden bir hizmet seçin.',
              'hizmetin_yedegi': 'hizmetin yedeği',
              'hizmetler_subtitle': 'Sistem servislerini ve donanım birimlerini yönetin, etkinleştirin veya devre dışı '
                                    'bırakın.',
              'hizmetler_uygun_detay': 'Hizmetlerin başlangıç durumları zaten bu profile uygun.',
              'ikisini_de_kapat': 'İkisini de Kapat (Önerilen)',
              'iptal': 'İptal',
              'islemci': 'İşlemci',
              'isletim_sistemi': 'İşletim Sistemi',
              'kap_hizmet_yok': 'Kapatılacak hizmet bulunamadı.',
              'kapatma_sorusu': 'hizmetinin açılışta otomatik başlamasını kapatıyorsunuz.\n'
                                'Bu hizmet şu an arka planda aktif/çalışır durumda.\n'
                                '\n'
                                'Hem açılış ayarını kapatıp hem de çalışan süreci şimdi durdurmak ister misiniz?',
              'kaydet': 'Kaydet',
              'kaydetme_hatasi': 'Kaydetme hatası: ',
              'kernel': 'Çekirdek (Kernel)',
              'komut': 'Komut',
              'kritik_hizmet': 'KRİTİK HİZMET',
              'kritik_maske_uyarisi': '\n'
                                      '\n'
                                      'Bu hizmet sistem için KRİTİK olarak işaretlenmiştir. Maskelemeniz sistemin '
                                      'kararsız çalışmasına veya açılmamasına yol açabilir!',
              'kritik_uyari': '\n'
                              '\n'
                              'Bu hizmet sistem için KRİTİK olarak işaretlenmiştir. Maskelemeniz sistemin kararsız '
                              'çalışmasına veya açılmamasına yol açabilir!',
              'kullanici_onerisi': 'KULLANICI ÖNERİSİ',
              'kullanici_ozel_profilleri': 'Kullanıcı Özel Profilleri',
              'lisans': 'Lisans: GPLv3',
              'loader': 'Önyükleyici (Loader)',
              'log_bulunamadi': 'Bu hizmet için herhangi bir log kaydı bulunamadı.',
              'maske_sorusu': 'hizmetini maskelemek istiyor musunuz?',
              'maskele': 'Maskele',
              'maskelenmis_kapali': 'Maskelenmiş (Kapalı)',
              'maskeyi_kaldir': 'Maskeyi Kaldır',
              'mevcut_durumu_kaydet': 'Mevcut Durumu Profil Olarak Kaydet',
              'modem_desc': 'Hücresel Modem Kontrolü',
              'mysql_desc': 'MySQL / MariaDB Veritabanı',
              'no_autostart_apps': 'Otomatik başlatılan uygulama bulunamadı.',
              'no_backups_found': 'Oluşturulmuş geri yükleme noktası bulunamadı.',
              'no_custom_profiles': 'Kayıtlı özel profil bulunamadı.',
              'oneri': 'Öneri',
              'onerilenler_kapatiliyor_bekleyin': 'Önerilen hizmetler kapatılıyor, lütfen bekleyin...',
              'opt_alt_bilgi': 'Açılışı geciktiren ve kapatılması güvenli olan hizmetleri tek tıkla kapatarak hız '
                               'kazanın.',
              'other': 'Diğer',
              'ozel_profil_olusturuldu': "Özel profil '{}' başarıyla oluşturuldu.",
              'ozel_profil_silindi': 'Özel profil silindi.',
              'ozel_profilim': 'Özel Profilim',
              'pdf_acilis_ozeti': '1. Açılış Süresi Özeti',
              'pdf_baslik': 'Pardus Açılış Analiz Raporu',
              'pdf_donanim_bilgileri': '2. Sistem Donanım ve Sürüm Bilgileri',
              'pdf_footer': 'Pardus Başlangıç Yöneticisi — Sistem Analiz Raporu',
              'pdf_hatasi': 'PDF Hatası: ',
              'pdf_kaydedildi': 'PDF Raporu başarıyla oluşturuldu:',
              'pdf_no_opt': 'Aktif olarak kapatılması önerilen gereksiz hizmet bulunamadı. Sisteminiz en iyi durumda!',
              'pdf_olustur': 'PDF Raporu Oluştur',
              'pdf_olusturuluyor': 'PDF Raporu oluşturuluyor...',
              'pdf_opt_onerileri': '4. Başlangıç Optimizasyonu Önerileri',
              'pdf_sayfa_1_1': 'Sayfa 1 / 1',
              'pdf_sistem_ozeti': '1. Sistem Özeti',
              'pdf_tamamlanamadi': 'PDF oluşturma işlemi tamamlanamadı.',
              'pdf_tarih': 'Oluşturulma Tarihi',
              'pdf_yavas_hizmetler': '3. En Yavaş Başlayan 5 Hizmet',
              'postgresql_desc': 'PostgreSQL Veritabanı',
              'prof_dev_desc': 'Yazılım geliştiriciler için hazırlandı. Docker, SSH ve veritabanı servisleri otomatik '
                               'olarak etkinleştirilir. Yazıcı gibi gereksiz servisler kapatılır.',
              'prof_dev_name': 'Yazılımcı Modu',
              'prof_min_desc': 'Sistemi en hızlı ve hafif şekilde başlatmak için. Ağ ve temel sistem güvenliği '
                               'dışındaki tüm ek servisler kapatılır. Pil tasarrufu sağlar.',
              'prof_min_name': 'Minimum Servis Modu',
              'prof_office_desc': 'Ofis işleri ve günlük kullanım için ideal ayarlar. Yazıcı, bluetooth, ağ servisleri '
                                  'açık kalır.',
              'prof_office_name': 'Ofis Modu',
              'profil_adi_girin_hata': 'Lütfen profil adı girin.',
              'profil_adi_lbl': 'Profil Adı:',
              'profil_adi_placeholder': 'Örn: Yazılım & Ofis Karışık',
              'profil_bagimlilik_uyarisi': 'Profil Uygulama Bağımlılık Uyarısı',
              'profil_basariyla_uygulandi': 'Profil Başarıyla Uygulandı!',
              'profil_okuma_hatasi': 'Profil okuma hatası: ',
              'profil_uygula_aciklama': 'Bu işlem sistem servislerinin başlangıç durumlarını toplu olarak '
                                        'düzenleyecektir.',
              'profil_uygula_bagimlilik_mesaji': 'Bu profili uygulamak aşağıdaki aktif hizmetleri ve onlara bağlı '
                                                 'servisleri etkileyebilir:\n'
                                                 '\n',
              'profil_uygula_soru': 'profilini uygulamak istiyor musunuz?',
              'profil_uygulama_hatasi': 'Profil Uygulanırken Hata Oluştu',
              'profil_uygulaniyor': 'Profil Uygulanıyor',
              'profil_uygulaniyor_bekleyin': 'Hizmet profili uygulanıyor, lütfen bekleyin...',
              'profil_zaten_uygulanmis': 'Profil Zaten Uygulanmış',
              'profili_kaydedildi': 'profili kaydedildi.',
              'profili_kaydet_title': 'Profili Kaydet',
              'profili_uygula': 'Profili Uygula',
              'profiller_subtitle': 'Sisteminizi tek tıkla belirli kullanım senaryolarına göre optimize edebilirsiniz.',
              'profiller_title': 'Sistem Başlangıç Profilleri',
              'sadece_acilis_etkinlestir': 'Sadece Başlangıçta Etkinleştir',
              'sadece_baslangic_degistir': 'Sadece Başlangıç Ayarını Değiştir',
              'sadece_simdi_baslat': 'Sadece Şimdi Başlat',
              'sadece_simdi_durdur': 'Sadece Şimdiki Süreci Durdur',
              'saniye_kazan': 'sn Kazan',
              'search_placeholder': 'Ara...',
              'sec_gained_lbl': 'saniye kazanılabilir!',
              'sec_lbl': 'saniye',
              'secilen_servis_yok': 'Bir servis seçin.',
              'secileni_geri_yukle': 'Seçileni Geri Yükle',
              'secileni_sil': 'Seçileni Sil',
              'services': 'Hizmetler',
              'side_analiz': 'Başlangıç Analizi',
              'side_autostart': 'Otomatik Uygulamalar',
              'side_hizmetler': 'Sistem Hizmetleri',
              'side_profiller': 'Hizmet Profilleri',
              'side_title_sub': 'Başlangıç Yöneticisi',
              'sifre_placeholder': 'Yönetici şifresi',
              'sifreyi_goster': 'Şifreyi Göster',
              'sil_onay_app': 'Seçilen uygulamayı silmek istiyor musunuz?',
              'silme_hatasi': 'Silme hatası: ',
              'simdi_baslat': 'Şimdi Başlat',
              'simdi_baslat_ve_etkinlestir': 'Şimdi Başlat ve Açılışta Etkinleştir',
              'simdi_durdur': 'Şimdi Durdur',
              'simdiki_durum': 'Şimdiki Durum',
              'sistem_baslangic_analizi': 'Sistem Başlangıç Analizi',
              'sistem_bilgileri': 'Sistem Bilgileri',
              'sistem_geri_yukleme_noktalari': 'Sistem Geri Yükleme Noktaları',
              'sistem_optimize_edilmis': 'Sisteminiz Zaten Optimize Edilmiş',
              'sistem_uygun_durumda': 'Sistem zaten bu profile uygun durumda.',
              'ssh_desc': 'SSH Uzaktan Erişim',
              'statik_sabit': 'Statik (Sabit Ayar)',
              'su_an_calisiyor': 'Şu An Çalışıyor',
              'su_an_durduruldu': 'Şu An Durduruldu',
              'subtitle': 'Sistem Açılış Analiz ve Optimizasyon Aracı',
              'sure': 'Süre',
              'sys_kernel': 'Çekirdek:',
              'sys_os': 'Sistem:',
              'sys_ram': 'Bellek:',
              'sys_uptime': 'Çalışma:',
              'tab_analiz': 'Başlangıç Analizi',
              'tab_custom_command': 'Özel Komut Ekle',
              'tab_desktop_apps': 'Masaüstü Uygulamaları',
              'tab_hizmetler': 'Hizmet Yönetimi',
              'tab_uygulamalar': 'Uygulama Başlangıcı',
              'tab_yedek': 'Geri Yükleme Noktası',
              'tahmini_kazanc': 'Tahmini Kazanç',
              'tarih_saat': 'Tarih / Saat',
              'tip_all': 'Tüm Kategoriler',
              'tip_critical': 'Kapatılmamalı',
              'tip_required': 'Gerekli',
              'tip_suggestion': 'Kapatılabilir',
              'title': 'Pardus Başlangıç Yöneticisi',
              'toplam_acilis': 'Toplam Açılış Süresi',
              'tum_onerilenleri_kapat': 'Tüm Önerilenleri Kapat',
              'tur': 'Tür',
              'userspace': 'Kullanıcı Alanı (Userspace)',
              'uyg_ekle_ad_bos': 'Hata: Uygulama adı boş olamaz.',
              'uyg_ekle_komut_bos': 'Hata: Komut alanı boş olamaz.',
              'ekle': 'Ekle',
              'baslangic_uygulamasi_ekle': 'Başlangıç Uygulaması Ekle',
              'uygula': 'Uygula',
              'uygulama_adi': 'Uygulama Adı',
              'uygulama_aktiflik_guncellendi': 'Uygulama aktiflik durumu güncellendi.',
              'uygulama_duzenle': 'Uygulama Düzenle',
              'uygulama_kaldirildi': 'Uygulama listeden kaldırıldı.',
              've_daha_fazla_hizmet': 've {} hizmet daha...\n',
              'view_devices': 'Aygıt Birimleri (.device)',
              'view_others': 'Diğerleri (Socket, Target, Mount)',
              'view_services': 'Servisler (.service)',
              'yazici_kullanimi': 'Yazıcı kullanmıyorsanız kapatılabilir.',
              'yazilim_guncelleme': 'Yazılım güncellemeleri kontrol ediliyor...',
              'yedek_adi_girin': 'Geri yükleme noktası adı girin:',
              'yedek_basarili': 'Geri yükleme noktası başarıyla oluşturuldu.',
              'yedek_bulunamadi': 'Yedek bulunamadı.',
              'yedek_don_aciklama': 'Bu işlem sistem servislerinin başlangıç durumlarını yedeğin alındığı tarihteki '
                                    'durumuna geri yükleyecektir.',
              'yedek_don_soru': 'Yedek Noktasına Dönmek İstiyor musunuz?',
              'yedek_geri_yukleniyor': 'Yedek Geri Yükleniyor',
              'yedek_noktalari': 'Geri Yükleme Noktaları',
              'yedek_noktasi_silindi': 'Yedek noktası silindi.',
              'yedek_olustur': 'Geri Yükleme Noktası Oluştur',
              'yedek_olusturuldu': 'Geri yükleme noktası oluşturuldu.',
              'yedek_sil_soru': 'Yedek Noktasını Silmek İstiyor musunuz?',
              'yedek_silindi': 'Seçilen yedek başarıyla silindi.',
              'yedek_yukleniyor_bekleyin': 'Sistem yedeği geri yükleniyor, lütfen bekleyin...',
              'uygulama_ara_placeholder': 'Uygulama ara...',
              'action_acilis_kapat': 'Açılışta Kapatma',
              'action_acilis_ac': 'Açılışta Etkinleştirme',
              'action_simdi_baslat': 'Şimdi Başlatma',
              'action_simdi_durdur': 'Şimdi Durdurma',
              'action_maskele': 'Maskeleme',
              'action_maskeyi_kaldir': 'Maske Kaldırma',
              'action_baslatildi': "'{}' için '{}' eylemi başlatıldı...",
              'action_batch_baslatildi': "'{}' için '{}' eylemleri başlatıldı...",
              'action_basarili': '{} başarılı',
              'action_hata': '{} Hatası: {}',
              'action_bilinmiyor': 'Bilinmeyen eylem: {}',
              'action_dep_uyari': '⚠️ DİKKAT: Bu hizmeti kapatmak, bağımlı çalışan şu hizmetleri etkileyebilir:\n{}',
              'disable_boot_running_sec': "'{}' hizmetinin açılışta otomatik başlamasını kapatıyorsunuz.\nBu hizmet şu an arka planda aktif/çalışır durumda.\n\nHem açılış ayarını kapatıp hem de çalışan süreci şimdi durdurmak ister misiniz?",
              'disable_boot_stopped_dep': "'{}' hizmetini açılışta kapatmak, bağımlı hizmetleri etkileyebilir:\n\n{}\n\nDevam etmek istiyor musunuz?",
              'disable_boot_stopped_title': "'{}' Hizmetini Açılışta Kapatmak İstiyor musunuz?",
              'enable_boot_stopped_sec': "'{}' hizmetinin açılışta otomatik başlamasını etkinleştiriyorsunuz.\nBu hizmet şu an arka planda çalışmıyor.\n\nAçılışta etkinleştirirken aynı zamanda şu anki oturumda hemen başlatmak ister misiniz?",
              'stop_enabled_sec': "'{}' hizmetini şu anki oturumda durduruyorsunuz.\nBu hizmet başlangıçta otomatik çalışacak şekilde ayarlanmış.\n\nHem şu an durdurup hem de bir sonraki açılışlarda çalışmamasını (devre dışı bırakılmasını) ister misiniz?",
              'start_disabled_sec': "'{}' hizmetini şu anki oturumda başlatıyorsunuz.\nBu hizmet başlangıçta otomatik çalışacak şekilde ayarlanmamış.\n\nHem şimdi başlatıp hem de sonraki açılışlarda otomatik başlamasını (etkinleştirilmesini) ister misiniz?",
              'log_dialog_title': 'Log: {}',
              'log_loading': 'Loglar yükleniyor, lütfen bekleyin...',
              'log_no_perm': 'Logları okuma yetkiniz bulunmuyor.\n\nLogları görüntülemek için yönetici şifrenizi girmeniz gerekmektedir.',
              'log_error': 'Hata: {}',
              'dep_dialog_title': 'Bağımlılıklar: {}',
              'dep_info_lbl': '<b>{}</b> hizmetinin diğer sistem birimleriyle olan bağımlılık ilişkileri:',
              'dep_loading': 'Bağımlılık ağacı yükleniyor...',
              'dep_not_found': 'Bağımlılık bilgisi bulunamadı.',
              'dep_error': 'Hata: {}',
              'dialog_close': 'Kapat',
              'select_service_first': 'Bir servis seçin.',
              'restore_point_name': 'Geri Dönüş Noktası ({})',
              'yeni_ozel_profil_btn': 'Yeni Özel Profil Oluştur',
              'yeni_profil_adi_girin': 'Yeni profil adı girin:',
              'yeni_uygulama_ekle_btn': '+ Uygulama Ekle',
              'yeni_uygulamalar': 'Yeni Uygulama Ekle',
              'yeni_yedek_noktasi_btn': 'Yeni Geri Yükleme Noktası Oluştur',
              'yenile': 'Yenile',
              'yetki_alt_bilgi': 'Sistem hizmetlerini yönetmek için yönetici (sudo) şifrenizi girin.',
              'yetki_gerekiyor': 'Yönetici Yetkisi Gerekiyor',
              'yetki_iptal': 'Yetkilendirme iptal edildi.',
              'yetki_yok': 'Logları okuma yetkiniz bulunmuyor.\n'
                           '\n'
                           'Logları görüntülemek için yönetici şifrenizi girmeniz gerekmektedir.',
              'yetkilendir': 'Yetkilendir',
              'yetkilendirildi': 'Yetkilendirildi, loglar yükleniyor...'}}
# Initialize gettext
import gettext
current_dir = os.path.dirname(os.path.abspath(__file__))
locale_dir = os.path.join(os.path.dirname(current_dir), "locale")
_tr = lambda x: x

def init_locale(lang=None):
    global LANG, _tr
    if lang:
        LANG = lang
    try:
        translation = gettext.translation("messages", localedir=locale_dir, languages=[LANG], fallback=True)
        _tr = translation.gettext
    except Exception:
        _tr = lambda x: x

init_locale()

def tr(key):
    try:
        val = _tr(key)
        # If translation key itself was returned, fallback to built-in static dictionary
        if val == key:
            lang_dict = FALLBACK_DICT.get(LANG, FALLBACK_DICT["tr"])
            return lang_dict.get(key, FALLBACK_DICT["tr"].get(key, key))
            
        # Dynamically restore leading/trailing newlines to match fallback catalog expectations
        orig_val = FALLBACK_DICT["tr"].get(key, "")
        if orig_val:
            if orig_val.startswith("\n") and not val.startswith("\n"):
                val = "\n" + val
            if orig_val.endswith("\n") and not val.endswith("\n"):
                val = val + "\n"
        return val
    except Exception:
        lang_dict = FALLBACK_DICT.get(LANG, FALLBACK_DICT["tr"])
        return lang_dict.get(key, FALLBACK_DICT["tr"].get(key, key))
