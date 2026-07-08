DESCRIPTIONS = {
    "NetworkManager-wait-online.service": {
        "desc": "Aglarin kullanima hazir olmasini bekler. Genelde gereksiz yere bekletir.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Internet gecikmesi yasamiyorsaniz gereksiz."
    },
    "NetworkManager.service": {
        "desc": "Ethernet, Wi-Fi ve mobil ag baglantilarini yonetir.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Internet baglantisi icin gereklidir."
    },
    "upower.service": {
        "desc": "Pil ve guc kaynagi bilgilerini yonetir. Dizustu bilgisayarlarda pil omrunu takip eder.",
        "tip": "oneri",
        "oneri": "Masaustu PC'de kapatilabilir. Dizustude gerekli olabilir."
    },
    "bluetooth.service": {
        "desc": "Bluetooth cihazlarinin baglanmasini ve yonetimini saglar.",
        "tip": "oneri",
        "oneri": "Bluetooth kullanmiyorsaniz kapatabilirsiniz."
    },
    "cups.service": {
        "desc": "CUPS yazici sistemi. Yazici alma ve yonetme islemlerini saglar.",
        "tip": "oneri",
        "oneri": "Yazici kullanmiyorsaniz kapatilabilir."
    },
    "cups-browsed.service": {
        "desc": "Agdaki paylasimli yazicilari otomatik olarak bulur ve ekler.",
        "tip": "oneri",
        "oneri": "Yazici kullanmiyorsaniz kapatilabilir."
    },
    "avahi-daemon.service": {
        "desc": "Agda cihazlari ve servisleri otomatik kesfetmeyi saglar (mDNS/DNS-SD).",
        "tip": "oneri",
        "oneri": "Cogu kullanici icin gereksizdir. Kapatilabilir."
    },
    "ModemManager.service": {
        "desc": "Mobil genis bant (3G/4G/LTE) modem baglantilarini yonetir.",
        "tip": "oneri",
        "oneri": "Mobil modem kullanmiyorsaniz kapatilabilir."
    },
    "colord.service": {
        "desc": "Renk yonetimi profillerini yonetir. Monitör ve yazici renk dogrulugu icin.",
        "tip": "oneri",
        "oneri": "Grafik/profesyonel tasarim yapmiyorsaniz kapatilabilir."
    },
    "accounts-daemon.service": {
        "desc": "Kullanici hesaplari ve kimlik dogrulama bilgilerini yonetir.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Kullanici hesabi yonetimi icin gereklidir."
    },
    "udisks2.service": {
        "desc": "Depolama cihazlarinin takilip-cikarilmasini ve yonetimini saglar.",
        "tip": "gerekli",
        "oneri": "Genelde acik kalmalidir. USB bellek vs. takmak icin gerekli."
    },
    "polkit.service": {
        "desc": "Yetkilendirme politikalarini yonetir. Uygulamalarin yonetici yetkisiyle calismasini saglar.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Sistem guvenligi icin gereklidir."
    },
    "wpa_supplicant.service": {
        "desc": "Kablosuz ag (Wi-Fi) baglantisi icin gerekli kriptografik islemleri yapar.",
        "tip": "gerekli",
        "oneri": "Wi-Fi kullaniyorsaniz kapatmayin. Kablolu baglanti kullaniyorsaniz kapatilabilir."
    },
    "gdm.service": {
        "desc": "GNOME Display Manager - Grafiksel giris ekrani.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Grafik arayuz icin gereklidir."
    },
    "apparmor.service": {
        "desc": "Uygulama guvenlik profillerini yukler (AppArmor). Sandbox guvenlik sistemi.",
        "tip": "kritik",
        "oneri": "Guvenlik icin acik kalmalidir."
    },
    "systemd-journald.service": {
        "desc": "Sistem loglarini (gunluk) toplar ve saklar.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Hata ayiklama ve sistem takibi icin gereklidir."
    },
    "systemd-logind.service": {
        "desc": "Kullanici oturumlarini ve erisimini yonetir.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Oturum acma/kapama icin gereklidir."
    },
    "systemd-udevd.service": {
        "desc": "Cihaz algilama ve yonetimini yapar (udev). Yeni donanim takildiginda tanir.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Donanim algilama icin gereklidir."
    },
    "lm-sensors.service": {
        "desc": "Isi, voltaj ve fan sensorlerinden veri okur.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Sensor bilgilerine ihtiyaciniz yoksa gereksiz."
    },
    "smartmontools.service": {
        "desc": "Disk sagligini izler (S.M.A.R.T.). Disk arizalarini onceden tahmin eder.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Disk sagligini takip etmek istiyorsaniz acik birakin."
    },
    "rtkit-daemon.service": {
        "desc": "Gercek zamanli ses ve medya islemleri icin oncelik yonetimi.",
        "tip": "gerekli",
        "oneri": "Ses sorunu yasamiyorsaniz acik kalabilir. Ses icin genelde gerekli."
    },
    "packagekit.service": {
        "desc": "Yazilim yoneticisi arka plan servisi. Paket kurulum/guncelleme islemlerini yapar.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. El ile guncelleme yapiyorsaniz gereksiz."
    },
    "systemd-timesyncd.service": {
        "desc": "Sistem saatini internet uzerinden otomatik olarak dogrular (NTP).",
        "tip": "gerekli",
        "oneri": "Genelde acik birakilmali. Yanlis saat bazi uygulamalarda sorun cikarir."
    },
    "systemd-resolved.service": {
        "desc": "DNS cozumleme islemlerini yonetir. Alan adlarini IP adresine cevirir.",
        "tip": "gerekli",
        "oneri": "Genelde acik birakilmali. Alternatif DNS yoneticisi kullanmiyorsaniz gereklidir."
    },
    "systemd-binfmt.service": {
        "desc": "Farkli ikili dosya bicimlerini (Wine, Java vb.) tanimak icin gerekli ayarlari yukler.",
        "tip": "oneri",
        "oneri": "Genelde kapatilabilir. Wine veya QEMU kullanmiyorsaniz gereksiz."
    },
    "systemd-rfkill.service": {
        "desc": "Kablosuz cihazlarin (Wi-Fi, Bluetooth) acik/kapali durumunu hatirlar.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Kablosuz donanim durumu otomatik hatirlanir."
    },
    "systemd-fsck.service": {
        "desc": "Baslangicta disk dosya sistemi sagligini kontrol eder (fsck).",
        "tip": "kritik",
        "oneri": "Kapatmayin. Disk hatalarini onlemek icin gereklidir."
    },
    "systemd-udev-trigger.service": {
        "desc": "Baslangicta tum cihazlarin algilanmasini tetikler.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Donanim tanima icin gereklidir."
    },
    "systemd-remount-fs.service": {
        "desc": "Baslangicta dosya sistemlerini yeniden baglar (remount) ve dogru ayarlarla baglanmasini saglar.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Dosya sistemleri icin gereklidir."
    },
    "systemd-modules-load.service": {
        "desc": "Baslangicta belirtilen kernel modullerini yukler.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Kernel modulleri icin gereklidir."
    },
    "systemd-sysctl.service": {
        "desc": "Kernel parametrelerini baslangicta ayarlar (sysctl).",
        "tip": "kritik",
        "oneri": "Kapatmayin. Sistem ayarlari icin gereklidir."
    },
    "systemd-random-seed.service": {
        "desc": "Baslangicta rastgele sayi uretecini (random seed) yukler.",
        "tip": "gerekli",
        "oneri": "Acik kalabilir. Guvenlik icin onemlidir."
    },
    "systemd-user-sessions.service": {
        "desc": "Kullanici oturumlarinin baslatilmasini ve sonlandirilmasini yonetir.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Oturum yonetimi icin gereklidir."
    },
    "systemd-tmpfiles-setup.service": {
        "desc": "Gecici dosya ve dizinleri baslangicta olusturur/temizler.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Sistemin duzgun calismasi icin gereklidir."
    },
    "systemd-tmpfiles-setup-dev.service": {
        "desc": "Cihaz dosyalarini baslangicta olusturur.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Donanim dosyalari icin gereklidir."
    },
    "systemd-tmpfiles-clean.service": {
        "desc": "Gecici dosyalari belirli araliklarla temizler.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Disk alani dert degilse gereksiz."
    },
    "systemd-tmpfiles-setup-dev-early.service": {
        "desc": "Cihaz dosyalarini erken baslangicta olusturur.",
        "tip": "kritik",
        "oneri": "Kapatmayin."
    },
    "systemd-journal-flush.service": {
        "desc": "Baslangictaki loglari bellekten diske yazar.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Log kaydi onemli degilse gereksiz."
    },
    "systemd-hostnamed.service": {
        "desc": "Bilgisayar adini (hostname) yonetir.",
        "tip": "gerekli",
        "oneri": "Genelde acik birakilir. Hostname degismiyorsa gereksiz."
    },
    "systemd-machined.service": {
        "desc": "Sanal makineleri ve konteynerlari yonetir ve izler.",
        "tip": "oneri",
        "oneri": "Docker/kapsayici kullanmiyorsaniz kapatilabilir."
    },
    "systemd-backlight.service": {
        "desc": "Ekran ve klavye arka isigi parlaklik ayarlarini hatirlar ve geri yukler.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Parlaklik ayari hatirlanmasi onemli degilse gereksiz."
    },
    "fstrim.service": {
        "desc": "SSD disklerde kullanilmayan bloklari temizler (TRIM). SSD omrunu uzatir.",
        "tip": "gerekli",
        "oneri": "SSD kullaniyorsaniz acik birakin. HDD'de gereksiz."
    },
    "fwupd.service": {
        "desc": "Donanim yazilimlarini (firmware) gunceller.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Donanim guncellemesi onemli degilse gereksiz."
    },
    "fwupd-refresh.service": {
        "desc": "Donanim yazilimi guncelleme veritabanini yeniler.",
        "tip": "oneri",
        "oneri": "Kapatilabilir."
    },
    "man-db.service": {
        "desc": "Yardim sayfalari (man pages) veritabanini gunceller.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Man sayfalarina ihtiyaciniz yoksa gereksiz."
    },
    "logrotate.service": {
        "desc": "Sistem log dosyalarini belirli boyuta ulasinca donusturur ve sıkıstirir.",
        "tip": "gerekli",
        "oneri": "Acik birakilmali. Loglarin disk doldurmasini engeller."
    },
    "dpkg-db-backup.service": {
        "desc": "Paket veritabaninin (dpkg) yedegini alir.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Paket yedegi onemli degilse gereksiz."
    },
    "exim4.service": {
        "desc": "Exim4 e-posta sunucusu. Yerel e-posta gonderimi icin.",
        "tip": "oneri",
        "oneri": "E-posta sunucusu kullanmiyorsaniz kapatilabilir. Cogunlukla gereksizdir."
    },
    "exim4-base.service": {
        "desc": "Exim4 e-posta sunucusu temel yapilandirma servisi.",
        "tip": "oneri",
        "oneri": "E-posta sunucusu kullanmiyorsaniz kapatilabilir."
    },
    "networking.service": {
        "desc": "Ag arayuzlerini baslangicta yapilandirir (/etc/network/interfaces).",
        "tip": "gerekli",
        "oneri": "NetworkManager kullanmiyorsaniz gereklidir."
    },
    "ifupdown-pre.service": {
        "desc": "Ag arayuzlerini baslatmadan once gerekli islemleri yapar.",
        "tip": "gerekli",
        "oneri": "Genelde acik birakilir."
    },
    "dbus.service": {
        "desc": "Uygulamalar arasi iletisim sistemi (D-Bus). Masaustu uygulamalari icin temel",
        "tip": "kritik",
        "oneri": "Kapatmayin. GNOME ve cogu uygulama icin gereklidir."
    },
    "plymouth-start.service": {
        "desc": "Baslangic animasyonunu (splash) gosterir.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Baslangic animasyonu onemli degilse gereksiz."
    },
    "plymouth-quit.service": {
        "desc": "Baslangic animasyonunu sonlandirir ve giris ekranina gecer.",
        "tip": "oneri",
        "oneri": "Plymouth kullanmiyorsaniz gereksiz."
    },
    "plymouth-quit-wait.service": {
        "desc": "Baslangic animasyonunun kapanmasini bekler. Acilisi gereksiz yere uzatabilir.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Bu servis acilisi 1-3 saniye uzatabilir."
    },
    "plymouth-read-write.service": {
        "desc": "Dosya sistemini salt-okunur moddan okuma-yazma moduna gecirir.",
        "tip": "kritik",
        "oneri": "Kapatmayin."
    },
    "console-setup.service": {
        "desc": "Klavye duzeni ve konsol yazi tipini ayarlar.",
        "tip": "gerekli",
        "oneri": "Acik birakilmali yoksa konsolda klavye duzeni hatali olabilir."
    },
    "keyboard-setup.service": {
        "desc": "Klavye duzenini erken baslangicta ayarlar.",
        "tip": "gerekli",
        "oneri": "Klavye duzeni icin acik birakilmali."
    },
    "kmod-static-nodes.service": {
        "desc": "Statik cihaz dugumlerini olusturur.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Donanim icin gereklidir."
    },
    "power-profiles-daemon.service": {
        "desc": "Guc tuketimi profillerini yonetir (performans/dengeli/tasarruf).",
        "tip": "oneri",
        "oneri": "Dizustude acik birakilabilir. Masaustunde gereksiz."
    },
    "switcheroo-control.service": {
        "desc": "Harici GPU (NVIDIA Optimus) yonetimini saglar.",
        "tip": "oneri",
        "oneri": "Harici GPU'nuz yoksa kapatilabilir."
    },
    "upower.service": {
        "desc": "Pil ve guc kaynagi bilgilerini yonetir.",
        "tip": "oneri",
        "oneri": "Masaustu bilgisayarda kapatilabilir."
    },
    "libvirtd.service": {
        "desc": "Sanal makine yonetimi (libvirt/virt-manager).",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmiyorsaniz kapatilabilir."
    },
    "libvirt-guests.service": {
        "desc": "Sanal makinelerin durumunu kaydeder ve geri yukler.",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmiyorsaniz kapatilabilir."
    },
    "virtlogd.service": {
        "desc": "Sanal makine loglarini yonetir.",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmiyorsaniz kapatilabilir."
    },
    "virtlockd.service": {
        "desc": "Sanal makine kilitlerini yonetir.",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmiyorsaniz kapatilabilir."
    },
    "grub-common.service": {
        "desc": "GRUB baslangic yoneticisi yapilandirmasini gunceller.",
        "tip": "gerekli",
        "oneri": "Acik birakilmali. Yeni kernel kurulumunda GRUB'u gunceller."
    },
    "lvm2-monitor.service": {
        "desc": "LVM (Mantiksal Hacim Yonetimi) durumunu izler.",
        "tip": "oneri",
        "oneri": "LVM kullanmiyorsaniz kapatilabilir."
    },
    "blk-availability.service": {
        "desc": "Blok cihazlarin kullanilabilirligini yonetir.",
        "tip": "kritik",
        "oneri": "Kapatmayin. Depolama cihazlari icin gereklidir."
    },
    "modprobe.service": {
        "desc": "Kernel modullerini yukler/module yukleme.",
        "tip": "kritik",
        "oneri": "Kapatmayin."
    },
    "e2scrub_reap.service": {
        "desc": "ext4 dosya sistemi saglik kontrolu sonuclarini temizler.",
        "tip": "oneri",
        "oneri": "Kapatilabilir."
    },
    "e2scrub_all.service": {
        "desc": "Tum ext4 dosya sistemlerinde saglik kontrolu baslatir.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Periyodik disk kontrolu onemli degilse."
    },
    "nvidia-resume.service": {
        "desc": "NVIDIA ekran karti surucusunu uyku/uyanma durumunda yonetir.",
        "tip": "gerekli",
        "oneri": "NVIDIA kart kullaniyorsaniz kapatmayin."
    },
    "nvidia-suspend.service": {
        "desc": "NVIDIA ekran karti surucusunu uyku modunda yonetir.",
        "tip": "gerekli",
        "oneri": "NVIDIA kart kullaniyorsaniz kapatmayin."
    },
    "apt-daily.service": {
        "desc": "Gunluk paket guncelleme kontrolu yapar (APT).",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Paketleri elle guncelliyorsaniz gereksiz."
    },
    "apt-daily-upgrade.service": {
        "desc": "Bekleyen paket guncellemelerini otomatik yukler.",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Otomatik guncelleme istemiyorsaniz gereksiz."
    },
    "snapd.service": {
        "desc": "Snap paket yoneticisi arka plan servisi.",
        "tip": "oneri",
        "oneri": "Snap kullanmiyorsaniz kapatilabilir."
    },
    "snapd.seeded.service": {
        "desc": "Snap paketlerinin ilk kurulumunu tamamlar.",
        "tip": "oneri",
        "oneri": "Snap kullanmiyorsaniz kapatilabilir."
    },
    "snapd.apparmor.service": {
        "desc": "Snap uygulamalari icin AppArmor profillerini yukler.",
        "tip": "oneri",
        "oneri": "Snap kullanmiyorsaniz kapatilabilir."
    },
    "user@.service": {
        "desc": "Kullaniciya ait systemd servislerini baslatir (user manager).",
        "tip": "kritik",
        "oneri": "Kapatmayin. Kullanici servisleri icin gereklidir."
    },
    "user-runtime-dir.service": {
        "desc": "Kullaniciya ait gecici dosya dizinini (runtime dir) olusturur.",
        "tip": "kritik",
        "oneri": "Kapatmayin."
    },
    "wtmpdb-update-boot.service": {
        "desc": "Baslangic kaydini wtmp veritabanina ekler (oturum kayitlari).",
        "tip": "oneri",
        "oneri": "Kapatilabilir. Oturum kaydi onemli degilse gereksiz."
    },
}


def get_description(name):
    entry = DESCRIPTIONS.get(name)
    if entry:
        return entry["desc"], entry["tip"], entry["oneri"]
    return None, None, None
