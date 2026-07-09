DESCRIPTIONS = {
    "NetworkManager-wait-online.service": {
        "desc": "Ağların kullanıma hazır olmasını bekler. Açılışta ağ bağlantısının tamamen kurulmasını bekleyerek sistemi geciktirebilir.",
        "desc_en": "Waits for network to be ready online. Can delay boot progress by waiting for complete network initialization.",
        "tip": "oneri",
        "oneri": "Güvenle kapatılabilir. Açılışta ağın hazır olmasını beklemeden masaüstünün yüklenmesini sağlar. İnternet bağlantı sorunları yaşamıyorsanız kapatılması önerilir.",
        "oneri_en": "Safe to disable. Allows loading the desktop without waiting for network to be fully online. Recommended to disable if no connection lag issues are observed."
    },
    "NetworkManager.service": {
        "desc": "Ethernet, Wi-Fi ve mobil ağ bağlantılarını yönetir.",
        "desc_en": "Manages Ethernet, Wi-Fi, and mobile network connections.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sisteminizin internete ve yerel ağa bağlanması için kesinlikle gereklidir.",
        "oneri_en": "Do not disable. Absolutely required for system internet and network connectivity."
    },
    "upower.service": {
        "desc": "Pil ve güç kaynağı bilgilerini yönetir. Dizüstü bilgisayarlarda pil ömrünü takip eder.",
        "desc_en": "Manages power source and battery information. Tracks battery life on laptops.",
        "tip": "oneri",
        "oneri": "Masaüstü bilgisayarlarda güvenle kapatılabilir. Dizüstü bilgisayarlarda pil durumu takibi için açık kalmalıdır.",
        "oneri_en": "Can be disabled on desktops. Recommended to keep enabled on laptops for battery status tracking."
    },
    "bluetooth.service": {
        "desc": "Bluetooth cihazlarının (klavye, fare, kulaklık vb.) bağlanmasını ve yönetimini sağlar.",
        "desc_en": "Manages Bluetooth devices (keyboard, mouse, headset etc.) and connections.",
        "tip": "oneri",
        "oneri": "Bluetooth özellikli cihazlar kullanmıyorsanız açılış süresini iyileştirmek için kapatılması önerilir.",
        "oneri_en": "Recommended to disable to improve boot times if you do not use Bluetooth devices."
    },
    "cups.service": {
        "desc": "CUPS yazıcı sistemi. Yazıcı tanımlama, yazdırma ve kuyruk işlemlerini yönetir.",
        "desc_en": "CUPS printing system. Manages print queues, spooling, and printer discovery.",
        "tip": "oneri",
        "oneri": "Sisteminizde bağlı veya tanımlı bir yazıcı kullanmıyorsanız açılışta gereksiz kaynak tüketmemesi için kapatılması önerilir.",
        "oneri_en": "Recommended to disable if you do not have any printers connected to the system."
    },
    "cups-browsed.service": {
        "desc": "Ağdaki paylaşımlı yazıcıları otomatik olarak keşfeder ve sisteme ekler.",
        "desc_en": "Automatically discovers and adds shared printers on the local network.",
        "tip": "oneri",
        "oneri": "Ağ yazıcısı veya paylaşımlı yazıcı kullanmıyorsanız kapatılması önerilir.",
        "oneri_en": "Recommended to disable if you do not use network printers."
    },
    "avahi-daemon.service": {
        "desc": "Yerel ağdaki cihazları ve servisleri otomatik olarak keşfetmeyi sağlar (mDNS/DNS-SD).",
        "desc_en": "Enables local network service discovery (mDNS/DNS-SD) for plug-and-play services.",
        "tip": "oneri",
        "oneri": "Yerel ağda dosya/yazıcı paylaşımı veya Apple cihazları ile keşif yapmıyorsanız kapatılması önerilir.",
        "oneri_en": "Recommended to disable if you do not share files/printers or discover other local devices."
    },
    "ModemManager.service": {
        "desc": "Mobil geniş bant (3G/4G/LTE) modem ve SIM kart bağlantılarını yönetir.",
        "desc_en": "Manages mobile broadband (3G/4G/LTE) modem and SIM card connections.",
        "tip": "oneri",
        "oneri": "Hücresel şebeke modemleri veya SIM kartlı mobil modemler kullanmıyorsanız güvenle kapatılabilir.",
        "oneri_en": "Can be safely disabled if you do not use SIM card modems or mobile broadband cards."
    },
    "colord.service": {
        "desc": "Renk yönetimi profillerini yönetir. Monitör ve yazıcı renk doğruluğunu sağlar.",
        "desc_en": "Manages color profiles. Controls color accuracy for monitors and printers.",
        "tip": "oneri",
        "oneri": "Profesyonel grafik tasarım veya renk kalibrasyonu yapmıyorsanız açılışı hızlandırmak için kapatılması önerilir.",
        "oneri_en": "Recommended to disable to speed up boot unless you do professional graphic design or color calibration."
    },
    "accounts-daemon.service": {
        "desc": "Kullanıcı hesapları ve kimlik doğrulama bilgilerini yönetir.",
        "desc_en": "Manages user account authentication and information.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Kullanıcı yönetimi ve sisteme giriş yapabilmek için kesinlikle gereklidir.",
        "oneri_en": "Do not disable. Absolutely required for user management and login screen authentication."
    },
    "udisks2.service": {
        "desc": "Depolama cihazlarının (diskler, USB bellekler vb.) takılıp çıkarılmasını ve yönetimini sağlar.",
        "desc_en": "Manages storage devices (hard drives, USB flash drives, etc.) and auto-mounts them.",
        "tip": "gerekli",
        "oneri": "Açık kalmalıdır. USB bellek veya taşınabilir disklerin otomatik tanınması için gereklidir.",
        "oneri_en": "Keep enabled. Required for automatically mounting USB flash drives and external disks."
    },
    "polkit.service": {
        "desc": "Yetkilendirme politikalarını yönetir. Uygulamaların yönetici yetkisiyle güvenli çalışmasını sağlar.",
        "desc_en": "Manages authorization policies. Controls privilege escalation for running administrative commands.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistem güvenliği ve yetkilendirme işlemleri için kesinlikle gereklidir.",
        "oneri_en": "Do not disable. Essential for system security and administrative actions."
    },
    "wpa_supplicant.service": {
        "desc": "Kablosuz ağ (Wi-Fi) bağlantısı için gerekli şifreleme ve kimlik doğrulama işlemlerini yapar.",
        "desc_en": "Handles cryptography and authentication for Wi-Fi connections.",
        "tip": "gerekli",
        "oneri": "Wi-Fi bağlantısı kullanıyorsanız kapatmayın. Sadece kablolu internet kullanıyorsanız kapatılabilir.",
        "oneri_en": "Keep enabled if you connect to the internet via Wi-Fi. Can be disabled if only using wired Ethernet."
    },
    "gdm.service": {
        "desc": "GNOME Ekran Yöneticisi. Grafiksel giriş ekranını sağlar.",
        "desc_en": "GNOME Display Manager. Provides the graphical login screen.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Grafik arayüzle oturum açabilmeniz için kesinlikle gereklidir.",
        "oneri_en": "Do not disable. Required to boot into the graphical desktop environment."
    },
    "apparmor.service": {
        "desc": "Uygulama güvenlik profillerini yükler. Güvenli uygulama izolasyonu sağlar.",
        "desc_en": "Loads AppArmor security profiles. Provides secure sandboxing for applications.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistem güvenliği ve zararlı yazılımların sınırlandırılması için gereklidir.",
        "oneri_en": "Do not disable. Essential for security and limiting potential exploits."
    },
    "systemd-journald.service": {
        "desc": "Sistem günlük (log) kayıtlarını toplar ve saklar.",
        "desc_en": "Collects and stores system event log records.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistem hatalarının tespiti ve log takibi için kesinlikle gereklidir.",
        "oneri_en": "Do not disable. Crucial for system troubleshooting and checking logs."
    },
    "systemd-logind.service": {
        "desc": "Kullanıcı oturumlarını, güç tuşlarını ve sistem erişimini yönetir.",
        "desc_en": "Manages user login sessions, power buttons, and system sleep/suspend states.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Oturum açma, kapama ve askıya alma işlemleri için gereklidir.",
        "oneri_en": "Do not disable. Essential for managing power states and user sessions."
    },
    "systemd-udevd.service": {
        "desc": "Cihaz algılama ve udev kurallarını yönetir. Yeni donanım takıldığında otomatik tanır.",
        "desc_en": "Manages udev hardware rule processing. Automatically detects newly plugged devices.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanım algılama ve sürücülerin yüklenmesi için kesinlikle gereklidir.",
        "oneri_en": "Do not disable. Absolutely required for hardware detection and driver loading."
    },
    "lm-sensors.service": {
        "desc": "Anakart üzerindeki sıcaklık, voltaj ve fan sensörlerinden veri okur.",
        "desc_en": "Reads values from motherboard hardware monitoring sensors (temperatures, fans, voltages).",
        "tip": "oneri",
        "oneri": "Donanım sıcaklıklarını veya fan hızlarını sürekli izleme ihtiyacınız yoksa kapatılabilir.",
        "oneri_en": "Can be disabled unless you monitor temperatures and fan speeds."
    },
    "smartmontools.service": {
        "desc": "Sabit disk ve SSD sağlık durumunu (S.M.A.R.T.) izler, olası disk arızalarını tahmin eder.",
        "desc_en": "Monitors disk health (S.M.A.R.T.) and predicts potential hard drive or SSD failures.",
        "tip": "oneri",
        "oneri": "Disk sağlığını arka planda sürekli takip etmek istemiyorsanız açılış hızını artırmak için kapatılabilir.",
        "oneri_en": "Can be disabled to speed up boot if you don't require continuous background disk monitoring."
    },
    "rtkit-daemon.service": {
        "desc": "Gerçek zamanlı ses ve medya işlemleri için sistem önceliklerini yönetir.",
        "desc_en": "Manages system real-time priorities for audio and media processes.",
        "tip": "gerekli",
        "oneri": "Açık kalmalıdır. Ses sisteminin (PulseAudio/PipeWire) düzgün ve takılmadan çalışması için gereklidir.",
        "oneri_en": "Keep enabled. Required for smooth audio playback without stuttering (PulseAudio/PipeWire)."
    },
    "packagekit.service": {
        "desc": "Yazılım yöneticisi arka plan servisi. Paket güncelleme ve yükleme işlemlerini yönetir.",
        "desc_en": "Software manager background daemon. Handles updates and software installations.",
        "tip": "oneri",
        "oneri": "Grafik arayüzden otomatik güncelleme kontrolleri istemiyorsanız kapatılabilir. Güncellemeleri uçbirimden kendiniz yapabilirsiniz.",
        "oneri_en": "Can be disabled if you do updates and package installations manually via terminal."
    },
    "systemd-timesyncd.service": {
        "desc": "Sistem saatini internet üzerindeki güvenilir sunucularla (NTP) otomatik eşitler.",
        "desc_en": "Automatically synchronizes system time with reliable NTP internet servers.",
        "tip": "gerekli",
        "oneri": "Açık kalması önerilir. Yanlış sistem saati SSL sertifikası hatalarına ve tarayıcı sorunlarına yol açabilir.",
        "oneri_en": "Recommended to keep enabled. Incorrect time can lead to SSL validation errors in browsers."
    },
    "systemd-resolved.service": {
        "desc": "Ağ DNS çözümleme işlemlerini yönetir.",
        "desc_en": "Manages network DNS resolution.",
        "tip": "gerekli",
        "oneri": "DNS çözümlemesi için açık kalması önerilir. Alternatif bir DNS yöneticisi kullanmıyorsanız kapatmayın.",
        "oneri_en": "Recommended to keep enabled. Do not disable unless you use an alternative DNS manager."
    },
    "systemd-binfmt.service": {
        "desc": "Farklı ikili dosya biçimlerini (Wine, Java vb.) çalıştırmak için gerekli çekirdek yapılandırmasını yükler.",
        "desc_en": "Registers kernel support for executing foreign binary formats (Wine, Java, etc.).",
        "tip": "oneri",
        "oneri": "Wine, Java veya QEMU gibi çapraz platform araçlarını kullanmıyorsanız kapatılabilir.",
        "oneri_en": "Can be disabled if you do not use Wine, Java, or QEMU cross-architecture tools."
    },
    "systemd-rfkill.service": {
        "desc": "Kablosuz cihazların (Wi-Fi, Bluetooth) uçak modu veya güç durumlarını hatırlar.",
        "desc_en": "Remembers wireless device (Wi-Fi, Bluetooth) power states and airplane mode across boots.",
        "tip": "oneri",
        "oneri": "Uçuş modu veya kablosuz donanım durumlarının otomatik hatırlanmasına ihtiyacınız yoksa kapatılabilir.",
        "oneri_en": "Can be disabled if you do not need to save the airplane mode state."
    },
    "systemd-fsck.service": {
        "desc": "Açılışta disk dosya sistemi bütünlüğünü ve sağlığını denetler.",
        "desc_en": "Checks filesystem health and integrity during boot.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Olası dosya sistemi hatalarını ve veri kayıplarını önlemek için gereklidir.",
        "oneri_en": "Do not disable. Essential to prevent data corruption by checking and repairing disks."
    },
    "systemd-udev-trigger.service": {
        "desc": "Açılış esnasında udev cihaz olaylarını tetikler ve donanımları algılar.",
        "desc_en": "Triggers udev device events during boot to discover all hardware devices.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanımların sistem tarafından doğru tanınması için kesinlikle gereklidir.",
        "oneri_en": "Do not disable. Crucial for proper device detection and layout initialization."
    },
    "systemd-remount-fs.service": {
        "desc": "Açılışta kök ve diğer dosya sistemlerini doğru izinlerle yeniden bağlar.",
        "desc_en": "Remounts root and other filesystems with correct write/read permissions during boot.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Dosya sistemlerinin yazma/okuma izinlerinin ayarlanması için gereklidir.",
        "oneri_en": "Do not disable. Required to configure write access to the filesystem."
    },
    "systemd-modules-load.service": {
        "desc": "Sistem başlangıcında çekirdek (kernel) modüllerini otomatik yükler.",
        "desc_en": "Loads specified kernel modules automatically during boot.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanım sürücülerinin ve çekirdek özelliklerinin çalışması için gereklidir.",
        "oneri_en": "Do not disable. Required for loading essential hardware drivers and kernel modules."
    },
    "systemd-sysctl.service": {
        "desc": "Çekirdek (kernel) parametrelerini açılışta yapılandırır.",
        "desc_en": "Configures kernel parameters during boot.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistem ince ayarları ve kararlılığı için gereklidir.",
        "oneri_en": "Do not disable. Essential for system tuning and stability parameters."
    },
    "systemd-random-seed.service": {
        "desc": "Açılışta rastgele sayı üretecinin güvenliğini sağlamak için tohum verisi yükler.",
        "desc_en": "Loads random seed data during boot to secure the system random number generator.",
        "tip": "gerekli",
        "oneri": "Açık kalması önerilir. Şifreleme ve güvenlik protokolleri için önemlidir.",
        "oneri_en": "Recommended to keep enabled. Important for security protocols and encryption."
    },
    "systemd-user-sessions.service": {
        "desc": "Kullanıcı oturumlarının başlatılmasına izin verir ve yönetir.",
        "desc_en": "Allows and manages user login sessions.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Kullanıcıların grafik arayüz veya konsol üzerinden oturum açabilmesi için gereklidir.",
        "oneri_en": "Do not disable. Essential for letting users log in via terminal or desktop interface."
    },
    "systemd-tmpfiles-setup.service": {
        "desc": "Geçici dosya ve dizinleri açılışta oluşturur ve eski olanları temizler.",
        "desc_en": "Creates and cleans up temporary files and directories during boot.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Sistemin kararlı çalışması için geçici dizinlerin hazır olması şarttır.",
        "oneri_en": "Do not disable. Crucial for preparing standard temporary storage folders."
    },
    "systemd-tmpfiles-setup-dev.service": {
        "desc": "Sistem başlangıcında donanım cihaz dosyalarını oluşturur.",
        "desc_en": "Creates hardware device files at system startup.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanım erişimi için gerekli cihaz düğümlerini oluşturur.",
        "oneri_en": "Do not disable. Essential for hardware access node setup."
    },
    "systemd-tmpfiles-clean.service": {
        "desc": "Geçici dosyaları arka planda belirli aralıklarla temizler.",
        "desc_en": "Cleans up temporary files in the background at regular intervals.",
        "tip": "oneri",
        "oneri": "Kapatılabilir. Disk alanınız kısıtlı değilse veya manuel temizliyorsanız kapatılabilir.",
        "oneri_en": "Can be disabled if disk space is not critical."
    },
    "systemd-tmpfiles-setup-dev-early.service": {
        "desc": "Açılışın erken evresinde kritik donanım cihaz dosyalarını hazırlar.",
        "desc_en": "Creates critical hardware device files early in the boot sequence.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Erken aşama donanım erişimi için zorunludur.",
        "oneri_en": "Do not disable. Absolutely required for early boot device access."
    },
    "systemd-journal-flush.service": {
        "desc": "Açılışın erken evresindeki log kayıtlarını bellekten kalıcı diske yazar.",
        "desc_en": "Flushes early boot log messages from memory to persistent disk storage.",
        "tip": "oneri",
        "oneri": "Hata tespiti için açık kalması önerilir. Logların kalıcı diske yazılmasını istemiyorsanız kapatılabilir.",
        "oneri_en": "Recommended to keep enabled. Can be disabled if you do not want persistent boot logs."
    },
    "systemd-hostnamed.service": {
        "desc": "Bilgisayar adını (hostname) yönetir.",
        "desc_en": "Manages the hostname (computer name) of the system.",
        "tip": "gerekli",
        "oneri": "Genelde açık bırakılır. Yerel ağda bilgisayar adınızın çözümlenmesi için gereklidir.",
        "oneri_en": "Generally kept enabled. Required for network host identification."
    },
    "systemd-machined.service": {
        "desc": "Sanal makineleri ve kapsayıcıları (container) izler ve yönetir.",
        "desc_en": "Monitors and manages virtual machines and container instances.",
        "tip": "oneri",
        "oneri": "Docker, LXC veya sistem düzeyinde sanallaştırma kullanmıyorsanız kapatılabilir.",
        "oneri_en": "Can be disabled if you do not run Docker, LXC, or other containers."
    },
    "systemd-backlight.service": {
        "desc": "Ekran ve klavye arka ışık parlaklık ayarlarını sistem kapanirken kaydeder ve açılışta yükler.",
        "desc_en": "Saves screen and keyboard backlight brightness settings on shutdown and restores them at boot.",
        "tip": "oneri",
        "oneri": "Ekran parlaklığının açılışta otomatik hatırlanmasını istemiyorsanız kapatılabilir.",
        "oneri_en": "Can be disabled if auto-brightness restoration is not required."
    },
    "fstrim.service": {
        "desc": "SSD disklerde kullanılmayan veri bloklarını temizler (TRIM). SSD ömrünü uzatır.",
        "desc_en": "Cleans unused blocks on SSD drives (TRIM). Extends SSD life and performance.",
        "tip": "gerekli",
        "oneri": "SSD kullanıyorsanız kesinlikle açık bırakılmalıdır. Sadece HDD kullanıyorsanız kapatılabilir.",
        "oneri_en": "Highly recommended to keep enabled on systems with SSDs. Can be disabled if only HDD is used."
    },
    "fwupd.service": {
        "desc": "Sistem donanım yazılımlarını (firmware) güvenli şekilde günceller.",
        "desc_en": "Checks and updates system hardware device firmware safely.",
        "tip": "oneri",
        "oneri": "Otomatik donanım güncellemeleri istemiyorsanız kapatılabilir.",
        "oneri_en": "Can be disabled if you do not wish to automatically check for hardware firmware updates."
    },
    "fwupd-refresh.service": {
        "desc": "Donanım yazılımı güncelleme veritabanını belirli aralıklarla yeniler.",
        "desc_en": "Refreshes the firmware update database periodically.",
        "tip": "oneri",
        "oneri": "Kapatılabilir.",
        "oneri_en": "Can be disabled."
    },
    "man-db.service": {
        "desc": "Uçbirim yardım sayfalarının (man pages) dizin veritabanını günceller.",
        "desc_en": "Updates the manual page (man pages) database index.",
        "tip": "oneri",
        "oneri": "Yardım sayfalarını sıkça kullanmıyorsanız açılıştaki disk yükünü azaltmak için kapatılabilir.",
        "oneri_en": "Can be disabled to reduce disk write overhead during boot."
    },
    "logrotate.service": {
        "desc": "Sistem günlük dosyalarını (log) otomatik arşivler, sıkıştırır ve temizler.",
        "desc_en": "Automatically archives, compresses, and cleans up system log files.",
        "tip": "gerekli",
        "oneri": "Açık kalması önerilir. Log dosyalarının zamanla diski doldurmasını engeller.",
        "oneri_en": "Recommended to keep enabled. Prevents log files from growing indefinitely and filling the disk."
    },
    "dpkg-db-backup.service": {
        "desc": "Debian/Pardus paket yönetim veritabanının günlük yedeğini alır.",
        "desc_en": "Backs up the Debian/Pardus package management database daily.",
        "tip": "oneri",
        "oneri": "Güvenle kapatılabilir. Paket yedeklerinin diskte birikmesini istemiyorsanız kapatılabilir.",
        "oneri_en": "Can be disabled if you do not require package database backups."
    },
    "exim4.service": {
        "desc": "Exim4 yerel posta sunucusu. Sistem içi e-posta gönderimi ve yönlendirmesi için kullanılır.",
        "desc_en": "Exim4 mail transport agent. Used for local system email routing.",
        "tip": "oneri",
        "oneri": "Sisteminizde bir yerel e-posta sunucusu çalıştırmıyorsanız (çoğu kullanıcı için gereksizdir) kapatılması kesinlikle önerilir.",
        "oneri_en": "Highly recommended to disable for desktop users since local mail transport is rarely used."
    },
    "exim4-base.service": {
        "desc": "Exim4 yerel e-posta sunucusu temel yapılandırma servisi.",
        "desc_en": "Base configuration helper for Exim4 mail server.",
        "tip": "oneri",
        "oneri": "Yerel e-posta sunucusu kullanmıyorsanız kapatılabilir.",
        "oneri_en": "Can be safely disabled if local email routing is not used."
    },
    "networking.service": {
        "desc": "Geleneksel ağ arayüzlerini başlangıçta yapılandırır.",
        "desc_en": "Configures traditional network interfaces at startup.",
        "tip": "gerekli",
        "oneri": "NetworkManager dışındaki manuel ağ yapılandırmaları için gereklidir.",
        "oneri_en": "Required if network configuration is managed via /etc/network/interfaces instead of NetworkManager."
    },
    "ifupdown-pre.service": {
        "desc": "Ağ arayüzleri başlatılmadan önce gerekli hazırlıkları yapar.",
        "desc_en": "Prepares network interfaces before they are brought online.",
        "tip": "gerekli",
        "oneri": "Geleneksel ağ yönetimi kullanan sistemlerde açık bırakılır.",
        "oneri_en": "Required on systems using traditional network management."
    },
    "dbus.service": {
        "desc": "Uygulamalar arası iletişim veri yolu (D-Bus). Masaüstü ortamının temel iletişim katmanıdır.",
        "desc_en": "D-Bus message bus. The base communication layer for applications and services.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Masaüstü arayüzü ve sistem servislerinin çalışması için kesinlikle gereklidir.",
        "oneri_en": "Do not disable. Absolutely required for running the desktop interface."
    },
    "plymouth-start.service": {
        "desc": "Başlangıç animasyonunu (Pardus açılış logosu ve yükleme ekranı) başlatır.",
        "desc_en": "Starts the boot splash screen animation.",
        "tip": "oneri",
        "oneri": "Açılışta animasyon görmek istemiyorsanız kapatılabilir.",
        "oneri_en": "Can be disabled if you prefer text logs on boot instead of a graphical splash."
    },
    "plymouth-quit.service": {
        "desc": "Açılış animasyonunu durdurur ve kontrolü giriş ekranına (display manager) devreder.",
        "desc_en": "Stops the boot splash screen and hands control over to the login manager.",
        "tip": "oneri",
        "oneri": "Plymouth kullanılmıyorsanız gereksizdir.",
        "oneri_en": "Can be disabled if Plymouth boot animation is not used."
    },
    "plymouth-quit-wait.service": {
        "desc": "Açılış animasyonunun tamamen kapanmasını bekler. Açılış süresini gereksiz uzatabilir.",
        "desc_en": "Waits for the boot splash animation to close. Can delay display manager loading.",
        "tip": "oneri",
        "oneri": "Kapatılması önerilir. Giriş ekranına geçişi 1-3 saniye arasında hızlandırabilir.",
        "oneri_en": "Recommended to disable. Can speed up time-to-login screen by 1 to 3 seconds."
    },
    "plymouth-read-write.service": {
        "desc": "Dosya sistemini salt-okunur moddan yazılabilir moda geçirir.",
        "desc_en": "Transitions the root filesystem from read-only to read-write mode.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Dosya yazma işlemleri için gereklidir.",
        "oneri_en": "Do not disable. Required for standard write operations."
    },
    "console-setup.service": {
        "desc": "Konsol ekran yazı tipini ve klavye düzenini ayarlar.",
        "desc_en": "Configures keyboard layout and console font styles.",
        "tip": "gerekli",
        "oneri": "Açık kalması önerilir. Konsol ekranında Türkçe klavye desteği için gereklidir.",
        "oneri_en": "Recommended to keep enabled. Required for correct localized keyboard layout in console TTY."
    },
    "keyboard-setup.service": {
        "desc": "Klavye düzenini açılışın erken evresinde yapılandırır.",
        "desc_en": "Configures the keyboard layout early in the boot sequence.",
        "tip": "gerekli",
        "oneri": "Açık kalmalıdır. Doğru klavye yerleşimi için gereklidir.",
        "oneri_en": "Keep enabled. Required for proper keyboard mappings."
    },
    "kmod-static-nodes.service": {
        "desc": "Çekirdek modülleri için gerekli statik cihaz düğümlerini oluşturur.",
        "desc_en": "Creates static device nodes based on kernel module configuration.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanımların doğru çalışabilmesi için gereklidir.",
        "oneri_en": "Do not disable. Essential for hardware devices to work correctly."
    },
    "power-profiles-daemon.service": {
        "desc": "Güç tüketim profillerini (performans, dengeli, güç tasarrufu) yönetir.",
        "desc_en": "Manages system power consumption profiles (power saver, balanced, performance).",
        "tip": "oneri",
        "oneri": "Dizüstü bilgisayarlarda pil ömrü için açık bırakılmalıdır. Masaüstünde kapatılabilir.",
        "oneri_en": "Recommended to keep enabled on laptops to save battery. Can be disabled on desktops."
    },
    "switcheroo-control.service": {
        "desc": "Çift ekran kartlı (NVIDIA Optimus / harici GPU) sistemlerde ekran kartları arası geçişi yönetir.",
        "desc_en": "Manages GPU offloading and switching on hybrid graphics setups (NVIDIA Optimus / dual GPU).",
        "tip": "oneri",
        "oneri": "Çift ekran kartlı dizüstü bilgisayarlar dışında kapatılabilir.",
        "oneri_en": "Can be disabled on desktops or laptops without dual switchable GPUs."
    },
    "upower.service": {
        "desc": "Pil ve güç kaynağı bilgilerini yönetir. Dizüstü bilgisayarlarda pil ömrünü takip eder.",
        "desc_en": "Manages power source and battery information. Tracks battery life on laptops.",
        "tip": "oneri",
        "oneri": "Masaüstü bilgisayarlarda güvenle kapatılabilir. Dizüstü bilgisayarlarda pil durumu takibi için açık kalmalıdır.",
        "oneri_en": "Can be disabled on desktops. Recommended to keep enabled on laptops for battery status tracking."
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
        "desc_en": "Runs GRUB bootloader initialization checks at boot.",
        "tip": "gerekli",
        "oneri": "Açık bırakılması önerilir. Çekirdek güncellemelerinin GRUB'a doğru işlenmesini sağlar.",
        "oneri_en": "Recommended to keep enabled. Ensures new kernel updates are correctly registered in the boot loader."
    },
    "lvm2-monitor.service": {
        "desc": "LVM (Mantıksal Hacim Yönetimi) disk bölümlerinin durumunu izler.",
        "desc_en": "Monitors LVM (Logical Volume Manager) storage volumes.",
        "tip": "oneri",
        "oneri": "Sisteminizde LVM disk bölümleme yapısı kullanmıyorsanız kapatılabilir.",
        "oneri_en": "Can be disabled if your system does not utilize LVM storage partition layouts."
    },
    "blk-availability.service": {
        "desc": "Blok cihazların kullanılabilirliğini yönetir.",
        "desc_en": "Manages block device availability on shutdown and startup.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Disklerin güvenli yönetimi için gereklidir.",
        "oneri_en": "Do not disable. Essential for clean partition management."
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
        "desc_en": "Loads specified kernel modules automatically during boot.",
        "tip": "kritik",
        "oneri": "Kapatmayın. Donanım sürücülerinin ve çekirdek özelliklerinin çalışması için gereklidir.",
        "oneri_en": "Do not disable. Required for loading essential hardware drivers and kernel modules."
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
        "desc_en": "Monitors LVM (Logical Volume Manager) storage volumes.",
        "tip": "oneri",
        "oneri": "Sisteminizde LVM disk bölümleme yapısı kullanmıyorsanız kapatılabilir.",
        "oneri_en": "Can be disabled if your system does not utilize LVM storage partition layouts."
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
        "desc_en": "Manages network DNS resolution.",
        "tip": "gerekli",
        "oneri": "DNS çözümlemesi için açık kalması önerilir. Alternatif bir DNS yöneticisi kullanmıyorsanız kapatmayın.",
        "oneri_en": "Recommended to keep enabled. Do not disable unless you use an alternative DNS manager."
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
    try:
        from locale_mgr import LANG
    except ImportError:
        try:
            from src.locale_mgr import LANG
        except ImportError:
            LANG = "tr"

    entry = DESCRIPTIONS.get(name)
    if entry:
        desc = entry.get("desc_" + LANG, entry.get("desc"))
        oneri = entry.get("oneri_" + LANG, entry.get("oneri"))
        return desc, entry["tip"], oneri
    if "@" in name:
        base = name.split("@")[0] + "@"
        template_name = _BASE_NAMES.get(base)
        if template_name:
            entry = DESCRIPTIONS.get(template_name)
            if entry:
                desc = entry.get("desc_" + LANG, entry.get("desc"))
                oneri = entry.get("oneri_" + LANG, entry.get("oneri"))
                return desc, entry["tip"], oneri
    return None, None, None
