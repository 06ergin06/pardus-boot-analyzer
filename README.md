# Pardus Başlangıç Yöneticisi (Pardus Boot Analyzer)

Pardus Başlangıç Yöneticisi, sisteminizin açılış süresini analiz etmek, başlangıçta çalışan gereksiz servisleri ve uygulamaları optimize etmek amacıyla geliştirilmiş yerel bir GTK+3 masaüstü uygulamasıdır. GNOME İnsan Arayüz Yönergeleri (HIG) standartlarına tam uyumlu olarak tasarlanmıştır.

## Özellikler

*   **Açılış Süresi Analizi:** Sisteminizin açılışındaki donanım, önyükleyici (loader), çekirdek (kernel) ve kullanıcı alanı (userspace) yüklenme sürelerini grafiksel olarak görüntüler.
*   **Hizmet Optimizasyonu (systemd):** Sistem servislerinin açılış sürelerini sıralar ve tek tıkla kapatılabilecek güvenli servisleri tespit ederek hızlandırma potansiyeli sunar.
*   **Açılış ve Anlık Durum Ayrımı:** Servislerin başlangıç ayarlarını (açılışta çalışsın/çalışmasın) ve o anki çalışma durumlarını (şimdi başlat/durdur) ayrı ayrı yönetebilmenizi sağlar. Çift yönlü işlem önerileri sunar.
*   **Özel Profil Yönetimi:** Ağ, Sunucu, Ofis gibi hazır optimizasyon profillerini uygulayabilir veya kendi özel servisinizi ekleyip yedekleyebilirsiniz.
*   **Başlangıç Uygulamaları:** Kullanıcı oturumu başladığında otomatik çalışan uygulamaları listeleyebilir, yenilerini ekleyebilir veya kaldırabilirsiniz.
*   **PDF Raporlama:** Sistem açılış sürelerini, donanım bilgilerini, en yavaş çalışan 5 servisi ve önerilen optimizasyonları içeren profesyonel bir PDF raporu oluşturur.
*   **Yerel Log İzleyici:** Yetki gerektiğinde otomatik olarak yönetici doğrulaması talep ederek servislerin systemd günlük kayıtlarını (journalctl) gösterir.

## Gereksinimler

Uygulamanın çalışması için aşağıdaki paketlerin sisteminizde kurulu olması gerekmektedir:

*   python3
*   python3-gi (PyGObject)
*   gir1.2-gtk-3.0
*   python3-cairo

Pardus/Debian üzerinde yüklemek için:
```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0 python3-cairo
```

## Kurulum ve Çalıştırma

### Kaynak Koddan Çalıştırma

Depoyu klonladıktan sonra proje dizininde şu komutla uygulamayı çalıştırabilirsiniz:
```bash
python3 main.py
```

### Debian Paketi (.deb) Kurulumu

Hazır derlenmiş paketi yüklemek için:
```bash
sudo dpkg -i pardus-boot-analyzer_1.0.0_all.deb
sudo apt install -f  # Eksik bağımlılıklar varsa tamamlamak için
```

## Debian Paketi Oluşturma

Projeyi yeniden derlemek ve paketlemek için dizindeki paketleme betiğini çalıştırabilirsiniz:
```bash
./build_deb.sh
```
Bu betik temizleme, dosya kopyalama, masaüstü kısayolu (.desktop) oluşturma ve paketleme adımlarını otomatik olarak gerçekleştirir.

## Geliştirici

*   **İbrahim Hakkı Ergin** (ibrahimh.ergin@gmail.com)
