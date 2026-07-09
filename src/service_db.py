DESCRIPTIONS = {
    "NetworkManager-wait-online.service": {
        "desc": "Ağların kullanıma hazır olmasını bekler. Açılışta ağ bağlantısının tamamen kurulmasını bekleyerek sistemi geciktirebilir.",
        "tip": "oneri",
        "oneri": "Güvenle kapatılabilir. Açılışta ağın hazır olmasını beklemeden masaüstünün yüklenmesini sağlar. İnternet bağlantı sorunları yaşamıyorsanız kapatılması önerilir."
    },
    "NetworkManager.service": {
        "desc": "Ethernet, Wi-Fi ve mobil ağ bağlantılarını yönetir.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sisteminizin internete ve yerel ağa bağlanması için kesinlikle gereklidir."
    },
    "upower.service": {
        "desc": "Pil ve güç kaynağı bilgilerini yönetir. Dizüstü bilgisayarlarda pil ömrünü takip eder.",
        "tip": "oneri",
        "oneri": "Masaüstü bilgisayarlarda güvenle kapatılabilir. Dizüstü bilgisayarlarda pil durumu takibi için açık kalmalıdır."
    },
    "bluetooth.service": {
        "desc": "Bluetooth cihazlarının (klavye, fare, kulaklık vb.) bağlanmasını ve yönetimini sağlar.",
        "tip": "oneri",
        "oneri": "Bluetooth özellikli cihazlar kullanmıyorsanız açılış süresini iyileştirmek için kapatılması önerilir."
    },
    "cups.service": {
        "desc": "CUPS yazıcı sistemi. Yazıcı tanımlama, yazdırma ve kuyruk işlemlerini yönetir.",
        "tip": "oneri",
        "oneri": "Sisteminizde bağlı veya tanımlı bir yazıcı kullanmıyorsanız açılışta gereksiz kaynak tüketmemesi için kapatılması önerilir."
    },
    "cups-browsed.service": {
        "desc": "Ağdaki paylaşımlı yazıcıları otomatik olarak keşfeder ve sisteme ekler.",
        "tip": "oneri",
        "oneri": "Ağ yazıcısı veya paylaşımlı yazıcı kullanmıyorsanız kapatılması önerilir."
    },
    "avahi-daemon.service": {
        "desc": "Yerel ağdaki cihazları ve servisleri otomatik olarak keşfetmeyi sağlar (mDNS/DNS-SD).",
        "tip": "oneri",
        "oneri": "Yerel ağda dosya/yazıcı paylaşımı veya Apple cihazları ile keşif yapmıyorsanız kapatılması önerilir."
    },
    "ModemManager.service": {
        "desc": "Mobil geniş bant (3G/4G/LTE) modem ve SIM kart bağlantılarını yönetir.",
        "tip": "oneri",
        "oneri": "Hücresel şebeke modemleri veya SIM kartlı mobil modemler kullanmıyorsanız güvenle kapatılabilir."
    },
    "colord.service": {
        "desc": "Renk yönetimi profillerini yönetir. Monitör ve yazıcı renk doğruluğunu sağlar.",
        "tip": "oneri",
        "oneri": "Profesyonel grafik tasarım veya renk kalibrasyonu yapmıyorsanız açılışı hızlandırmak için kapatılması önerilir."
    },
    "accounts-daemon.service": {
        "desc": "Kullanıcı hesapları ve kimlik doğrulama bilgilerini yönetir.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Kullanıcı yönetimi ve sisteme giriş yapabilmek için kesinlikle gereklidir."
    },
    "udisks2.service": {
        "desc": "Depolama cihazlarının (diskler, USB bellekler vb.) takılıp çıkarılmasını ve yönetimini sağlar.",
        "tip": "gerekli",
        "oneri": "Açık kalmalıdır. USB bellek veya taşınabilir disklerin otomatik tanınması için gereklidir."
    },
    "polkit.service": {
        "desc": "Yetkilendirme politikalarını yönetir. Uygulamaların yönetici yetkisiyle güvenli çalışmasını sağlar.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistem güvenliği ve yetkilendirme işlemleri için kesinlikle gereklidir."
    },
    "wpa_supplicant.service": {
        "desc": "Kablosuz ağ (Wi-Fi) bağlantısı için gerekli şifreleme ve kimlik doğrulama işlemlerini yapar.",
        "tip": "gerekli",
        "oneri": "Wi-Fi bağlantısı kullanıyorsanız kapatmayın. Sadece kablolu internet kullanıyorsanız kapatılabilir."
    },
    "gdm.service": {
        "desc": "GNOME Ekran Yöneticisi. Grafiksel giriş ekranını sağlar.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Grafik arayüzle oturum açabilmeniz için kesinlikle gereklidir."
    },
    "apparmor.service": {
        "desc": "Uygulama güvenlik profillerini yükler. Güvenli uygulama izolasyonu sağlar.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistem güvenliği ve zararlı yazılımların sınırlandırılması için gereklidir."
    },
    "systemd-journald.service": {
        "desc": "Sistem günlük (log) kayıtlarını toplar ve saklar.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistem hatalarının tespiti ve log takibi için kesinlikle gereklidir."
    },
    "systemd-logind.service": {
        "desc": "Kullanıcı oturumlarını, güç tuşlarını ve sistem erişimini yönetir.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Oturum açma, kapama ve askıya alma işlemleri için gereklidir."
    },
    "systemd-udevd.service": {
        "desc": "Cihaz algılama ve udev kurallarını yönetir. Yeni donanım takıldığında otomatik tanır.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanım algılama ve sürücülerin yüklenmesi için kesinlikle gereklidir."
    },
    "lm-sensors.service": {
        "desc": "Anakart üzerindeki sıcaklık, voltaj ve fan sensörlerinden veri okur.",
        "tip": "oneri",
        "oneri": "Donanım sıcaklıklarını veya fan hızlarını sürekli izleme ihtiyacınız yoksa kapatılabilir."
    },
    "smartmontools.service": {
        "desc": "Sabit disk ve SSD sağlık durumunu (S.M.A.R.T.) izler, olası disk arızalarını tahmin eder.",
        "tip": "oneri",
        "oneri": "Disk sağlığını arka planda sürekli takip etmek istemiyorsanız açılış hızını artırmak için kapatılabilir."
    },
    "rtkit-daemon.service": {
        "desc": "Gerçek zamanlı ses ve medya işlemleri için sistem önceliklerini yönetir.",
        "tip": "gerekli",
        "oneri": "Açık kalmalıdır. Ses sisteminin (PulseAudio/PipeWire) düzgün ve takılmadan çalışması için gereklidir."
    },
    "packagekit.service": {
        "desc": "Yazılım yöneticisi arka plan servisi. Paket güncelleme ve yükleme işlemlerini yönetir.",
        "tip": "oneri",
        "oneri": "Grafik arayüzden otomatik güncelleme kontrolleri istemiyorsanız kapatılabilir. Güncellemeleri uçbirimden kendiniz yapabilirsiniz."
    },
    "systemd-timesyncd.service": {
        "desc": "Sistem saatini internet üzerindeki güvenilir sunucularla (NTP) otomatik eşitler.",
        "tip": "gerekli",
        "oneri": "Açık kalması önerilir. Yanlış sistem saati SSL sertifikası hatalarına ve tarayıcı sorunlarına yol açabilir."
    },
    "systemd-resolved.service": {
        "desc": "Ağ DNS çözümleme işlemlerini yönetir.",
        "tip": "gerekli",
        "oneri": "DNS çözümlemesi için açık kalması önerilir. Alternatif bir DNS yöneticisi kullanmıyorsanız kapatmayın."
    },
    "systemd-binfmt.service": {
        "desc": "Farklı ikili dosya biçimlerini (Wine, Java vb.) çalıştırmak için gerekli çekirdek yapılandırmasını yükler.",
        "tip": "oneri",
        "oneri": "Wine, Java veya QEMU gibi çapraz platform araçlarını kullanmıyorsanız kapatılabilir."
    },
    "systemd-rfkill.service": {
        "desc": "Kablosuz cihazların (Wi-Fi, Bluetooth) uçak modu veya güç durumlarını hatırlar.",
        "tip": "oneri",
        "oneri": "Uçuş modu veya kablosuz donanım durumlarının otomatik hatırlanmasına ihtiyacınız yoksa kapatılabilir."
    },
    "systemd-fsck.service": {
        "desc": "Açılışta disk dosya sistemi bütünlüğünü ve sağlığını denetler.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Olası dosya sistemi hatalarını ve veri kayıplarını önlemek için gereklidir."
    },
    "systemd-udev-trigger.service": {
        "desc": "Açılış esnasında udev cihaz olaylarını tetikler ve donanımları algılar.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanımların sistem tarafından doğru tanınması için kesinlikle gereklidir."
    },
    "systemd-remount-fs.service": {
        "desc": "Açılışta kök ve diğer dosya sistemlerini doğru izinlerle yeniden bağlar.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Dosya sistemlerinin yazma/okuma izinlerinin ayarlanması için gereklidir."
    },
    "systemd-modules-load.service": {
        "desc": "Sistem başlangıcında çekirdek (kernel) modüllerini otomatik yükler.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanım sürücülerinin ve çekirdek özelliklerinin çalışması için gereklidir."
    },
    "systemd-sysctl.service": {
        "desc": "Çekirdek (kernel) parametrelerini açılışta yapılandırır.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistem ince ayarları ve kararlılığı için gereklidir."
    },
    "systemd-random-seed.service": {
        "desc": "Açılışta rastgele sayı üretecinin güvenliğini sağlamak için tohum verisi yükler.",
        "tip": "gerekli",
        "oneri": "Açık kalması önerilir. Şifreleme ve güvenlik protokolleri için önemlidir."
    },
    "systemd-user-sessions.service": {
        "desc": "Kullanıcı oturumlarının başlatılmasına izin verir ve yönetir.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Kullanıcıların grafik arayüz veya konsol üzerinden oturum açabilmesi için gereklidir."
    },
    "systemd-tmpfiles-setup.service": {
        "desc": "Geçici dosya ve dizinleri açılışta oluşturur ve eski olanları temizler.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistemin kararlı çalışması için geçici dizinlerin hazır olması şarttır."
    },
    "systemd-tmpfiles-setup-dev.service": {
        "desc": "Sistem başlangıcında donanım cihaz dosyalarını oluşturur.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanım erişimi için gerekli cihaz düğümlerini oluşturur."
    },
    "systemd-tmpfiles-clean.service": {
        "desc": "Geçici dosyaları arka planda belirli aralıklarla temizler.",
        "tip": "oneri",
        "oneri": "Kapatılabilir. Disk alanınız kısıtlı değilse veya manuel temizliyorsanız kapatılabilir."
    },
    "systemd-tmpfiles-setup-dev-early.service": {
        "desc": "Açılışın erken evresinde kritik donanım cihaz dosyalarını hazırlar.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Erken aşama donanım erişimi için zorunludur."
    },
    "systemd-journal-flush.service": {
        "desc": "Açılışın erken evresindeki log kayıtlarını bellekten kalıcı diske yazar.",
        "tip": "oneri",
        "oneri": "Hata tespiti için açık kalması önerilir. Logların kalıcı diske yazılmasını istemiyorsanız kapatılabilir."
    },
    "systemd-hostnamed.service": {
        "desc": "Bilgisayar adını (hostname) yönetir.",
        "tip": "gerekli",
        "oneri": "Genelde açık bırakılır. Yerel ağda bilgisayar adınızın çözümlenmesi için gereklidir."
    },
    "systemd-machined.service": {
        "desc": "Sanal makineleri ve kapsayıcıları (container) izler ve yönetir.",
        "tip": "oneri",
        "oneri": "Docker, LXC veya sistem düzeyinde sanallaştırma kullanmıyorsanız kapatılabilir."
    },
    "systemd-backlight.service": {
        "desc": "Ekran ve klavye arka ışık parlaklık ayarlarını sistem kapanirken kaydeder ve açılışta yükler.",
        "tip": "oneri",
        "oneri": "Ekran parlaklığının açılışta otomatik hatırlanmasını istemiyorsanız kapatılabilir."
    },
    "fstrim.service": {
        "desc": "SSD disklerde kullanılmayan veri bloklarını temizler (TRIM). SSD ömrünü uzatır.",
        "tip": "gerekli",
        "oneri": "SSD kullanıyorsanız kesinlikle açık bırakılmalıdır. Sadece HDD kullanıyorsanız kapatılabilir."
    },
    "fwupd.service": {
        "desc": "Sistem donanım yazılımlarını (firmware) güvenli şekilde günceller.",
        "tip": "oneri",
        "oneri": "Otomatik donanım güncellemeleri istemiyorsanız kapatılabilir."
    },
    "fwupd-refresh.service": {
        "desc": "Donanım yazılımı güncelleme veritabanını belirli aralıklarla yeniler.",
        "tip": "oneri",
        "oneri": "Kapatılabilir."
    },
    "man-db.service": {
        "desc": "Uçbirim yardım sayfalarının (man pages) dizin veritabanını günceller.",
        "tip": "oneri",
        "oneri": "Yardım sayfalarını sıkça kullanmıyorsanız açılıştaki disk yükünü azaltmak için kapatılabilir."
    },
    "logrotate.service": {
        "desc": "Sistem günlük dosyalarını (log) otomatik arşivler, sıkıştırır ve temizler.",
        "tip": "gerekli",
        "oneri": "Açık kalması önerilir. Log dosyalarının zamanla diski doldurmasını engeller."
    },
    "dpkg-db-backup.service": {
        "desc": "Debian/Pardus paket yönetim veritabanının günlük yedeğini alır.",
        "tip": "oneri",
        "oneri": "Güvenle kapatılabilir. Paket yedeklerinin diskte birikmesini istemiyorsanız kapatılabilir."
    },
    "exim4.service": {
        "desc": "Exim4 yerel posta sunucusu. Sistem içi e-posta gönderimi ve yönlendirmesi için kullanılır.",
        "tip": "oneri",
        "oneri": "Sisteminizde bir yerel e-posta sunucusu çalıştırmıyorsanız (çoğu kullanıcı için gereksizdir) kapatılması kesinlikle önerilir."
    },
    "exim4-base.service": {
        "desc": "Exim4 yerel e-posta sunucusu temel yapılandırma servisi.",
        "tip": "oneri",
        "oneri": "Yerel e-posta sunucusu kullanmıyorsanız kapatılabilir."
    },
    "networking.service": {
        "desc": "Geleneksel ağ arayüzlerini başlangıçta yapılandırır.",
        "tip": "gerekli",
        "oneri": "NetworkManager dışındaki manuel ağ yapılandırmaları için gereklidir."
    },
    "ifupdown-pre.service": {
        "desc": "Ağ arayüzleri başlatılmadan önce gerekli hazırlıkları yapar.",
        "tip": "gerekli",
        "oneri": "Geleneksel ağ yönetimi kullanan sistemlerde açık bırakılır."
    },
    "dbus.service": {
        "desc": "Uygulamalar arası iletişim veri yolu (D-Bus). Masaüstü ortamının temel iletişim katmanıdır.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Masaüstü arayüzü ve sistem servislerinin çalışması için kesinlikle gereklidir."
    },
    "plymouth-start.service": {
        "desc": "Başlangıç animasyonunu (Pardus açılış logosu ve yükleme ekranı) başlatır.",
        "tip": "oneri",
        "oneri": "Açılışta animasyon görmek istemiyorsanız kapatılabilir."
    },
    "plymouth-quit.service": {
        "desc": "Açılış animasyonunu durdurur ve kontrolü giriş ekranına (display manager) devreder.",
        "tip": "oneri",
        "oneri": "Plymouth kullanılmıyorsanız gereksizdir."
    },
    "plymouth-quit-wait.service": {
        "desc": "Açılış animasyonunun tamamen kapanmasını bekler. Açılış süresini gereksiz uzatabilir.",
        "tip": "oneri",
        "oneri": "Kapatılması önerilir. Giriş ekranına geçişi 1-3 saniye arasında hızlandırabilir."
    },
    "plymouth-read-write.service": {
        "desc": "Dosya sistemini salt-okunur moddan yazılabilir moda geçirir.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Dosya yazma işlemleri için gereklidir."
    },
    "console-setup.service": {
        "desc": "Konsol ekran yazı tipini ve klavye düzenini ayarlar.",
        "tip": "gerekli",
        "oneri": "Açık kalması önerilir. Konsol ekranında Türkçe klavye desteği için gereklidir."
    },
    "keyboard-setup.service": {
        "desc": "Klavye düzenini açılışın erken evresinde yapılandırır.",
        "tip": "gerekli",
        "oneri": "Açık kalmalıdır. Doğru klavye yerleşimi için gereklidir."
    },
    "kmod-static-nodes.service": {
        "desc": "Çekirdek modülleri için gerekli statik cihaz düğümlerini oluşturur.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanımların doğru çalışabilmesi için gereklidir."
    },
    "power-profiles-daemon.service": {
        "desc": "Güç tüketim profillerini (performans, dengeli, güç tasarrufu) yönetir.",
        "tip": "oneri",
        "oneri": "Dizüstü bilgisayarlarda pil ömrü için açık bırakılmalıdır. Masaüstünde kapatılabilir."
    },
    "switcheroo-control.service": {
        "desc": "Çift ekran kartlı (NVIDIA Optimus / harici GPU) sistemlerde ekran kartları arası geçişi yönetir.",
        "tip": "oneri",
        "oneri": "Çift ekran kartlı dizüstü bilgisayarlar dışında kapatılabilir."
    },
    "upower.service": {
        "desc": "Pil ve güç kaynağı bilgilerini yönetir. Dizüstü bilgisayarlarda pil ömrünü takip eder.",
        "tip": "oneri",
        "oneri": "Masaüstü bilgisayarlarda güvenle kapatılabilir. Dizüstü bilgisayarlarda pil durumu takibi için açık kalmalıdır."
    },
    "libvirtd.service": {
        "desc": "Sanal makine yonetimi (libvirt/virt-manager).",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmıyorsanız kapatılabilir."
    },
    "libvirt-guests.service": {
        "desc": "Sanal makinelerin durumunu kaydeder ve geri yükler.",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmıyorsanız kapatılabilir."
    },
    "virtlogd.service": {
        "desc": "Sanal makine loglarini yönetir.",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmıyorsanız kapatılabilir."
    },
    "virtlockd.service": {
        "desc": "Sanal makine kilitlerini yönetir.",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmıyorsanız kapatılabilir."
    },
    "grub-common.service": {
        "desc": "GRUB başlangıç yöneticisi ayarlarını başlangıçta kontrol eder.",
        "tip": "gerekli",
        "oneri": "Açık bırakılması önerilir. Çekirdek güncellemelerinin GRUB'a doğru işlenmesini sağlar."
    },
    "lvm2-monitor.service": {
        "desc": "LVM (Mantıksal Hacim Yönetimi) disk bölümlerinin durumunu izler.",
        "tip": "oneri",
        "oneri": "Sisteminizde LVM disk bölümleme yapısı kullanmıyorsanız kapatılabilir."
    },
    "blk-availability.service": {
        "desc": "Blok cihazların kullanılabilirliğini yönetir.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Disklerin güvenli yönetimi için gereklidir."
    },
    "modprobe.service": {
        "desc": "Kernel modullerini yükler/module yukleme.",
        "tip": "kritik",
        "oneri": "Kapatmayın."
    },
    "e2scrub_reap.service": {
        "desc": "ext4 dosya sistemi saglik kontrolu sonuclarini temizler.",
        "tip": "oneri",
        "oneri": "Kapatılabilir."
    },
    "e2scrub_all.service": {
        "desc": "Tum ext4 dosya sistemlerinde saglik kontrolu baslatir.",
        "tip": "oneri",
        "oneri": "Kapatılabilir. Periyodik disk kontrolu onemli degilse."
    },
    "nvidia-resume.service": {
        "desc": "NVIDIA ekran karti sürücüsünü uyku/uyanma durumunda yönetir.",
        "tip": "gerekli",
        "oneri": "NVIDIA kart kullaniyorsaniz kapatmayın."
    },
    "nvidia-suspend.service": {
        "desc": "NVIDIA ekran karti sürücüsünü uyku modunda yönetir.",
        "tip": "gerekli",
        "oneri": "NVIDIA kart kullaniyorsaniz kapatmayın."
    },
    "apt-daily.service": {
        "desc": "Gunluk paket güncelleme kontrolu yapar (APT).",
        "tip": "oneri",
        "oneri": "Kapatılabilir. Paketleri elle güncelliyorsanız gereksiz."
    },
    "apt-daily-upgrade.service": {
        "desc": "Bekleyen paket guncellemelerini otomatik yükler.",
        "tip": "oneri",
        "oneri": "Kapatılabilir. Otomatik güncelleme istemiyorsaniz gereksiz."
    },
    "snapd.service": {
        "desc": "Snap paket yoneticisi arka plan servisi.",
        "tip": "oneri",
        "oneri": "Snap kullanmıyorsanız kapatılabilir."
    },
    "snapd.seeded.service": {
        "desc": "Snap paketlerinin ilk kurulumunu tamamlar.",
        "tip": "oneri",
        "oneri": "Snap kullanmıyorsanız kapatılabilir."
    },
    "snapd.apparmor.service": {
        "desc": "Snap uygulamalari için AppArmor profillerini yükler.",
        "tip": "oneri",
        "oneri": "Snap kullanmıyorsanız kapatılabilir."
    },
    "user@.service": {
        "desc": "Kullaniciya ait systemd servislerini baslatir (user manager).",
        "tip": "kritik",
        "oneri": "Kapatmayın. Kullanıcı servisleri için gereklidir."
    },
    "user-runtime-dir.service": {
        "desc": "Kullaniciya ait gecici dosya dizinini (runtime dir) olusturur.",
        "tip": "kritik",
        "oneri": "Kapatmayın."
    },
    "wtmpdb-update-boot.service": {
        "desc": "Baslangic kaydini wtmp veritabanina ekler (oturum kayitlari).",
        "tip": "oneri",
        "oneri": "Kapatılabilir. Oturum kaydi onemli degilse gereksiz."
    },

    "getty@.service": {
        "desc": "Sanal konsolda (TTY) oturum acmayi sağlar. Ctrl+Alt+F1-F6 ile gecilen ekranlar.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Konsol oturumu için gereklidir."
    },
    "user@.service": {
        "desc": "Kullaniciya ait systemd servislerini baslatir (user manager).",
        "tip": "kritik",
        "oneri": "Kapatmayın. Kullanıcı servisleri için gereklidir."
    },
    "user-runtime-dir@.service": {
        "desc": "Kullaniciya ait gecici dosya dizinini (runtime dir) olusturur.",
        "tip": "kritik",
        "oneri": "Kapatmayın."
    },
    "systemd-backlight@.service": {
        "desc": "Ekran ve klavye arka ışığı parlaklık ayarlarini hatirlar ve geri yükler.",
        "tip": "oneri",
        "oneri": "Kapatılabilir. Parlaklik ayari onemli degilse gereksiz."
    },
    "systemd-cryptsetup@.service": {
        "desc": "Sifrelenmis disk bölümlerini (LUKS) başlangıçta acmak için şifre sorar.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sifrelenmis diskinizin acilmasi için gereklidir."
    },
    "systemd-fsck@.service": {
        "desc": "Başlangıçta disk dosya sistemi sağlığını kontrol eder (fsck).",
        "tip": "kritik",
        "oneri": "Kapatmayın. Disk hatalarini onlemek için gereklidir."
    },
    "systemd-modules-load.service": {
        "desc": "Sistem başlangıcında çekirdek (kernel) modüllerini otomatik yükler.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanım sürücülerinin ve çekirdek özelliklerinin çalışması için gereklidir."
    },
    "modprobe@.service": {
        "desc": "Belirli kernel modullerini başlangıçta yükler.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanim sürücüleri için gereklidir."
    },
    "systemd-zram-setup@.service": {
        "desc": "ZRAM (sikistirilmis sanal bellek) aygiti olusturur. RAM'i sikistirarak daha fazla bellek gibi kullanir.",
        "tip": "oneri",
        "oneri": "ZRAM kullanmıyorsanız kapatılabilir."
    },
    "systemd-pcrphase@.service": {
        "desc": "TPM 2.0 olcum kayitlarini (PCR) baslangic asamalarinda günceller.",
        "tip": "gerekli",
        "oneri": "TPM kullaniyorsaniz kapatmayın."
    },
    "dirmngr@.service": {
        "desc": "GPG anahtar sunucusu ile iletisimi yönetir. Paket imzalari dogrulamasi için.",
        "tip": "gerekli",
        "oneri": "Pacman/kurulum için genelde gerekli."
    },
    "gpg-agent@.service": {
        "desc": "GPG sifreleme anahtarlarını bellekte tutar. Paket imzalaması ve sifreleme için.",
        "tip": "gerekli",
        "oneri": "Pacman ve paket yonetimi için genelde gerekli."
    },
    "keyboxd@.service": {
        "desc": "GPG anahtar deposu yoneticisi. GPG anahtarlarını guvenli sekilde saklar.",
        "tip": "gerekli",
        "oneri": "Pacman için genelde gerekli."
    },

    "ananicy-cpp.service": {
        "desc": "IO ve CPU onceliklerini otomatik ayarlayarak sistem yanit verebilirligini artırır.",
        "tip": "oneri",
        "oneri": "Kapatılabilir. Oyun/masaüstü performansi için faydali olabilir."
    },
    "archlinux-keyring-wkd-sync.service": {
        "desc": "Arch Linux paket imzalama anahtarlarını Web Key Directory uzerinden günceller.",
        "tip": "gerekli",
        "oneri": "Pacman paket dogrulamasi için gereklidir."
    },
    "asusd.service": {
        "desc": "ASUS donanim yonetimi (klavye ışığı, performans modu, fan profilleri).",
        "tip": "oneri",
        "oneri": "ASUS laptop kullaniyorsaniz açık birakin."
    },
    "asus-shutdown.service": {
        "desc": "ASUS donanimini bilgisayar kapanirken guvenli sekilde kapatir.",
        "tip": "oneri",
        "oneri": "ASUS laptop kullaniyorsaniz kapatmayın."
    },
    "auditd.service": {
        "desc": "Sistem güvenlik denetim loglarini (audit) toplar ve kaydeder.",
        "tip": "oneri",
        "oneri": "Guvenlik denetimi istemiyorsaniz kapatılabilir."
    },
    "audit-rules.service": {
        "desc": "Sistem güvenlik denetim kurallarini yükler.",
        "tip": "oneri",
        "oneri": "auditd kapaliysa gereksiz."
    },
    "bpftune.service": {
        "desc": "BPF (Berkeley Packet Filter) ile ag performansını otomatik ayarlar.",
        "tip": "oneri",
        "oneri": "Kapatılabilir. Gelismis ag optimizasyonu için."
    },
    "containerd.service": {
        "desc": "Konteyner çalıştırma ortami (containerd). Docker ve diger konteynerlerin temeli.",
        "tip": "oneri",
        "oneri": "Docker/konteyner kullanmıyorsanız kapatılabilir."
    },
    "dbus-broker.service": {
        "desc": "Hizli ve guvenilir D-Bus mesaji brokeri. Uygulamalar arasi iletisimi sağlar.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Masaüstü ortami için gereklidir."
    },
    "dm-event.service": {
        "desc": "Device Mapper olaylarini izler ve LVM işlemlerini tetikler.",
        "tip": "gerekli",
        "oneri": "LVM kullaniyorsaniz kapatmayın."
    },
    "docker.service": {
        "desc": "Docker konteyner platformu. Konteynerleri calistirir ve yönetir.",
        "tip": "oneri",
        "oneri": "Docker kullanmıyorsanız kapatılabilir."
    },
    "emergency.service": {
        "desc": "Acil durum modu. Sistem baslamazsa komut satiri için kullanilir.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Kurtarma modu için gereklidir."
    },
    "ldconfig.service": {
        "desc": "Paylasilan kutuphane (shared library) önbelleğini günceller.",
        "tip": "gerekli",
        "oneri": "Kapatmayın. Yeni kütüphanelerin taninmasi için gereklidir."
    },
    "libvirtd.service": {
        "desc": "Sanal makine yonetimi (libvirt/virt-manager). Konuk makineleri calistirir.",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmıyorsanız kapatılabilir."
    },
    "lvm2-lvmpolld.service": {
        "desc": "LVM hacim yonetimi işlemlerini arka planda izler ve yönetir.",
        "tip": "oneri",
        "oneri": "LVM kullanmıyorsanız kapatılabilir."
    },
    "lvm2-monitor.service": {
        "desc": "LVM (Mantıksal Hacim Yönetimi) disk bölümlerinin durumunu izler.",
        "tip": "oneri",
        "oneri": "Sisteminizde LVM disk bölümleme yapısı kullanmıyorsanız kapatılabilir."
    },
    "mkinitcpio-generate-shutdown-ramfs.service": {
        "desc": "Kapanis için gerekli initramfs (ilk RAM dosya sistemi) imajini olusturur.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistemin guvenli kapanmasi için gereklidir."
    },
    "plocate-updatedb.service": {
        "desc": "Dosya arama veritabanını (plocate/mlocate) günceller. 'locate' komutu için.",
        "tip": "oneri",
        "oneri": "'locate' komutunu kullanmıyorsanız kapatılabilir."
    },
    "powertop.service": {
        "desc": "Guc tuketimini analiz eder ve enerji tasarrufu onerileri sunar.",
        "tip": "oneri",
        "oneri": "Dizüstü bilgisayarda faydali. Masaustunde gereksiz."
    },
    "rescue.service": {
        "desc": "Kurtarma modu. Tek kullanıcı modunda sistem kurtarma için.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Acil durum kurtarma için gereklidir."
    },
    "sddm.service": {
        "desc": "Basit masaüstü yoneticisi (SDDM). Grafiksel giriş ekranı.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Grafik arayüz için gereklidir."
    },
    "shadow.service": {
        "desc": "Golge parola ve kullanıcı hesabı bilgilerini günceller.",
        "tip": "gerekli",
        "oneri": "Kapatmayın. Kullanıcı yonetimi için gereklidir."
    },
    "snapper-cleanup.service": {
        "desc": "Snapper anlık goruntu (snapshot) temizliğini otomatik yapar.",
        "tip": "oneri",
        "oneri": "Snapper kullanmıyorsanız kapatılabilir."
    },
    "systemd-battery-check.service": {
        "desc": "Başlangıçta pil sağlığını kontrol eder ve dusuk seviyede uyarir.",
        "tip": "oneri",
        "oneri": "Dizüstü kullaniyorsaniz açık birakabilirsiniz."
    },
    "systemd-boot-random-seed.service": {
        "desc": "Başlangıçta rastgele sayi uretecini TPM ile guvenli sekilde yükler.",
        "tip": "gerekli",
        "oneri": "TPM kullaniyorsaniz kapatmayın."
    },
    "systemd-bsod.service": {
        "desc": "Kritik sistem hatalarinda mavi ekran (BSOD) gosterir.",
        "tip": "oneri",
        "oneri": "Kapatılabilir. Sadece hata durumunda devreye girer."
    },
    "systemd-confext.service": {
        "desc": "Sistem yapilandirma dosyasi uzantılarını (/etc/extensions) yükler.",
        "tip": "oneri",
        "oneri": "Kullanmiyorsaniz kapatılabilir."
    },
    "systemd-firstboot.service": {
        "desc": "Sistem ilk baslatildiginda temel yapilandirma (dil, saat, klavye) sorar.",
        "tip": "oneri",
        "oneri": "Sistem zaten kuruluysa calismaz, kapatmaya gerek yok."
    },
    "systemd-hibernate-resume.service": {
        "desc": "Hazirda bekletme (hibernate) modundan donuste sistem durumunu geri yükler.",
        "tip": "kritik",
        "oneri": "Hazirda bekletme kullaniyorsaniz kapatmayın."
    },
    "systemd-importd.service": {
        "desc": "Konteyner/sanal makine imajlarini iceri aktarmayi yönetir.",
        "tip": "oneri",
        "oneri": "Konteyner kullanmıyorsanız kapatılabilir."
    },
    "systemd-machine-id-commit.service": {
        "desc": "Gecici makine kimligini (machine-id) kalici hale getirir.",
        "tip": "kritik",
        "oneri": "Kapatmayın."
    },
    "systemd-oomd.service": {
        "desc": "Bellek yetersizliginde (OOM) hangi uygulamanin sonlandirilacagina akilli sekilde karar verir.",
        "tip": "gerekli",
        "oneri": "Bellek yetersizligi yasiyorsaniz açık birakin."
    },
    "systemd-quotacheck-root.service": {
        "desc": "Kok dosya sistemi için disk kullanim sinirlamalarini (quota) kontrol eder.",
        "tip": "oneri",
        "oneri": "Disk kotasi kullanmıyorsanız gereksiz."
    },
    "systemd-repart.service": {
        "desc": "Disk bölümlerini otomatik olarak yeniden boyutlandirir ve olusturur.",
        "tip": "oneri",
        "oneri": "Genelde calismaz. Otomatik bölümleme gerekiyorsa kullanilir."
    },
    "systemd-resolved.service": {
        "desc": "Ağ DNS çözümleme işlemlerini yönetir.",
        "tip": "gerekli",
        "oneri": "DNS çözümlemesi için açık kalması önerilir. Alternatif bir DNS yöneticisi kullanmıyorsanız kapatmayın."
    },
    "systemd-soft-reboot.service": {
        "desc": "Yeniden baslatmadan sadece kullanıcı alanini (user space) yeniden baslatir.",
        "tip": "oneri",
        "oneri": "Genelde kullanilmaz. Elle tetiklenir."
    },
    "systemd-sysext.service": {
        "desc": "Sistem goruntu uzantılarını (sysroot /var/lib/extensions) yükler.",
        "tip": "oneri",
        "oneri": "Kullanmiyorsaniz kapatılabilir."
    },
    "systemd-sysusers.service": {
        "desc": "Sistem kullanicilarini ve gruplarini başlangıçta olusturur.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Kullanıcı hesapları için gereklidir."
    },
    "systemd-tpm2-setup.service": {
        "desc": "TPM 2.0 güvenlik yongasını başlangıçta yapılandırır.",
        "tip": "gerekli",
        "oneri": "TPM kullaniyorsaniz kapatmayın."
    },
    "systemd-udev-load-credentials.service": {
        "desc": "Udev kurallari için gerekli yetki bilgilerini yükler.",
        "tip": "kritik",
        "oneri": "Kapatmayın."
    },
    "systemd-udev-settle.service": {
        "desc": "Tum cihazlarin algilanmasini bekler. Acilisi gereksiz yere uzatabilir.",
        "tip": "oneri",
        "oneri": "Gereksiz yere bekletiyorsa maskelenebilir. Genelde gereksizdir."
    },
    "systemd-update-done.service": {
        "desc": "Sistem guncellemesinden sonra yapılması gereken islemleri işaretler.",
        "tip": "gerekli",
        "oneri": "Kapatmayın."
    },
    "systemd-userdbd.service": {
        "desc": "Kullanıcı veritabanı servisi. Kullanicilari JSON uzerinden dinamik sorgular.",
        "tip": "gerekli",
        "oneri": "Genelde açık birakilir."
    },
    "systemd-vconsole-setup.service": {
        "desc": "Klavye düzeni ve konsol yazı tipini başlangıçta ayarlar.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Klavye düzeni için gereklidir."
    },
    "tlp.service": {
        "desc": "Guc yonetimi aracı. Dizüstü bilgisayarlarda pil ömrünü uzatır.",
        "tip": "oneri",
        "oneri": "Dizüstü kullaniyorsaniz açık birakin. Masaustunde gereksiz."
    },
    "ufw.service": {
        "desc": "Basit güvenlik duvari (Uncomplicated Firewall). Ag trafigini kontrol eder.",
        "tip": "gerekli",
        "oneri": "Guvenlik duvari istiyorsaniz açık birakin."
    },
    "virtsecretd.service": {
        "desc": "Sanal makine sirlarini (parola, anahtar) yönetir.",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmıyorsanız kapatılabilir."
    },
    "virtlogd.service": {
        "desc": "Sanal makine loglarini yönetir.",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmıyorsanız kapatılabilir."
    },
    "virtlockd.service": {
        "desc": "Sanal makine kilitlerini yönetir. Kaynak catismasini onler.",
        "tip": "oneri",
        "oneri": "Sanal makine kullanmıyorsanız kapatılabilir."
    },
    "warp-svc.service": {
        "desc": "Cloudflare WARP VPN servisi. İnternet baglantinizi guvenli hale getirir.",
        "tip": "oneri",
        "oneri": "WARP kullanmıyorsanız kapatılabilir."
    },
    "zapret.service": {
        "desc": "DPI (Derin Paket Inceleme) engellemesini asmak için ag trafigini düzenler.",
        "tip": "oneri",
        "oneri": "Kullanmiyorsaniz kapatılabilir."
    },
    "cachyos-iw-set-regdomain.service": {
        "desc": "Kablosuz ag bölge kodunu (regdomain) ayarlar. Wi-Fi kanal uyumlulugu için.",
        "tip": "oneri",
        "oneri": "Wi-Fi calismiyorsa gerekli olabilir."
    },
    "initrd-cleanup.service": {
        "desc": "Initrd (ilk RAM disk) aşamasından sonra gecici dosyalari temizler.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistem baslangici için gereklidir."
    },
    "initrd-parse-etc.service": {
        "desc": "Initrd aşamasında /etc dosyalarini okur ve yapilandirmayi yükler.",
        "tip": "kritik",
        "oneri": "Kapatmayın."
    },
    "initrd-switch-root.service": {
        "desc": "Initrd'den gerçek kök dosya sistemine geçişi yönetir.",
        "tip": "kritik",
        "oneri": "Kapatmayın."
    },
    "initrd-udevadm-cleanup-db.service": {
        "desc": "Initrd asamasindaki cihaz veritabanını temizler.",
        "tip": "kritik",
        "oneri": "Kapatmayın."
    },
}

_BASE_NAMES = {}
for key in list(DESCRIPTIONS.keys()):
    if "@" in key:
        base = key.split("@")[0] + "@"
        _BASE_NAMES[base] = key


def get_description(name):
    entry = DESCRIPTIONS.get(name)
    if entry:
        return entry["desc"], entry["tip"], entry["oneri"]
    if "@" in name:
        base = name.split("@")[0] + "@"
        template_name = _BASE_NAMES.get(base)
        if template_name:
            entry = DESCRIPTIONS.get(template_name)
            if entry:
                return entry["desc"], entry["tip"], entry["oneri"]
    return None, None, None
