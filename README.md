# Pardus Başlangıç Yöneticisi / Pardus Boot Analyzer

Pardus Başlangıç Yöneticisi, sisteminizin açılış süresini analiz etmek, başlangıçta çalışan gereksiz servisleri ve uygulamaları optimize etmek amacıyla geliştirilmiş bir masaüstü uygulamasıdır.

Pardus Boot Analyzer is a desktop application developed to analyze your system's boot time and optimize unnecessary services and applications running at startup.

---

## Türkçe

### Özellikler

*   **Açılış Süresi Analizi:** Sisteminizin açılışındaki donanım, önyükleyici (loader), çekirdek (kernel) ve kullanıcı alanı (userspace) yüklenme sürelerini grafiksel olarak görüntüler.
*   **Hizmet Optimizasyonu (systemd):** Sistem servislerinin açılış sürelerini sıralar ve tek tıkla kapatılabilecek güvenli servisleri tespit ederek hızlandırma potansiyeli sunar.
*   **Açılış ve Anlık Durum Ayrımı:** Servislerin başlangıç ayarlarını (açılışta çalışsın/çalışmasın) ve o anki çalışma durumlarını (şimdi başlat/durdur) ayrı ayrı yönetebilmenizi sağlar. Çift yönlü işlem önerileri sunar.
*   **Özel Profil Yönetimi:** Ağ, Sunucu, Ofis gibi hazır optimizasyon profillerini uygulayabilir veya kendi özel servisinizi ekleyip yedekleyebilirsiniz.
*   **Başlangıç Uygulamaları:** Kullanıcı oturumu başladığında otomatik çalışan uygulamaları listeleyebilir, yenilerini ekleyebilir veya kaldırabilirsiniz.
*   **PDF Raporlama:** Sistem açılış sürelerini, donanım bilgilerini, en yavaş çalışan 5 servisi ve önerilen optimizasyonları içeren profesyonel bir PDF raporu oluşturur.
*   **Yerel Log İzleyici:** Yetki gerektiğinde otomatik olarak yönetici doğrulaması talep ederek servislerin systemd günlük kayıtlarını (journalctl) gösterir.

### Gereksinimler

Uygulamanın çalışması için aşağıdaki paketlerin sisteminizde kurulu olması gerekmektedir:

*   python3
*   python3-gi (PyGObject)
*   gir1.2-gtk-3.0
*   python3-cairo

Pardus/Debian üzerinde yüklemek için:
```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0 python3-cairo
```

### Kurulum ve Çalıştırma

#### Kaynak Koddan Çalıştırma

Depoyu klonladıktan sonra proje dizininde şu komutla uygulamayı çalıştırabilirsiniz:
```bash
python3 main.py
```

#### Debian Paketi (.deb) Kurulumu

Hazır derlenmiş paketi yüklemek için:
```bash
sudo dpkg -i pardus-boot-analyzer_1.0.0_all.deb
sudo apt install -f
```

#### Debian Paketi Oluşturma

Projeyi yeniden derlemek ve paketlemek için dizindeki paketleme betiğini çalıştırabilirsiniz:
```bash
./build_deb.sh
```

---

## English

### Features

*   **Boot Time Analysis:** Graphically displays loading times for firmware, loader, kernel, and userspace.
*   **Service Optimization (systemd):** Lists boot times of system services and highlights safe services that can be disabled for faster boot.
*   **Boot & Current State Separation:** Allows managing service startup configuration (start at boot / do not start) and current runtime state (start now / stop now) independently. Offers dual-action prompt options.
*   **Custom Profile Management:** Apply presets like Network, Server, Office, or add and backup your custom services.
*   **Startup Applications:** List, add, or remove applications configured to auto-start when the user session begins.
*   **PDF Reporting:** Generates a PDF report containing boot times, hardware info, top 5 slowest services, and optimization recommendations.
*   **Native Log Viewer:** Displays systemd journal logs (journalctl) with automatic administrator privilege prompt when needed.

### Requirements

The following packages must be installed on your system:

*   python3
*   python3-gi (PyGObject)
*   gir1.2-gtk-3.0
*   python3-cairo

To install them on Pardus/Debian:
```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0 python3-cairo
```

### Installation and Usage

#### Running from Source Code

After cloning the repository, run the application from the project directory:
```bash
python3 main.py
```

#### Debian Package (.deb) Installation

To install the pre-compiled package:
```bash
sudo dpkg -i pardus-boot-analyzer_1.0.0_all.deb
sudo apt install -f
```

#### Creating Debian Package

To compile and package the project:
```bash
./build_deb.sh
```
