<p align="center">
  <img src="pardus-boot-analyzer.svg" width="128" height="128" alt="Pardus Boot Analyzer Logo">
</p>

# Pardus Boot Analyzer

[Türkçe Sürüm (Turkish Version)](README.md)

Pardus Boot Analyzer is a desktop application developed to analyze your system's boot time and optimize unnecessary services and applications running at startup.

### About the Project
This application was developed independently for the 2026 TEKNOFEST Pardus Bug Catching and Suggestion Competition under the Development Category.

### Developer
* [**İbrahim Hakkı Ergin**](https://github.com/06ergin06)

### Screenshots

| Page | Light Mode | Dark Mode |
| :---: | :---: | :---: |
| **Dashboard** | ![Dashboard Light](screenshots/shared/l1.png) | ![Dashboard Dark](screenshots/shared/d1.png) |
| **Autostart** | ![Autostart Light](screenshots/shared/l2.png) | ![Autostart Dark](screenshots/shared/d2.png) |
| **Services** | ![Services Light](screenshots/shared/l3.png) | ![Services Dark](screenshots/shared/d3.png) |
| **Profiles** | ![Profiles Light](screenshots/shared/l4.png) | ![Profiles Dark](screenshots/shared/d4.png) |

---

## Features

* **Boot Time Analysis:** Graphically displays loading times for firmware, loader, kernel, and userspace.
* **Service Optimization (systemd):** Lists boot times of system services and highlights safe services that can be disabled for faster boot.
* **Boot & Current State Separation:** Allows managing service startup configuration (start at boot / do not start) and current runtime state (start now / stop now) independently. Offers dual-action prompt options.
* **Custom Profile Management:** Apply presets like Network, Server, Office, or add and backup your custom services.
* **Startup Applications:** List, add, or remove applications configured to auto-start when the user session begins.
* **PDF Reporting:** Generates a PDF report containing boot times, hardware info, top 5 slowest services, and optimization recommendations.
* **Native Log Viewer:** Displays systemd journal logs (journalctl) with automatic administrator privilege prompt when needed.

## Requirements

The following packages must be installed on your system:

* python3
* python3-gi (PyGObject)
* gir1.2-gtk-3.0
* python3-cairo

To install them on Pardus/Debian:
```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0 python3-cairo
```

## Installation and Usage

### Running from Source Code

After cloning the repository, run the application from the project directory:
```bash
python3 main.py
```

### Debian Package (.deb) Installation

* **GUI Installation (Pardus):** You can double-click the `.deb` file to easily install it via the **Pardus Package Installer** GUI.
* **Terminal Installation:**
  ```bash
  sudo dpkg -i pardus-boot-analyzer_1.0.5_all.deb
  sudo apt install -f
  ```

### AppImage Portable Package Installation

To run the application as a standalone portable AppImage without installation:
```bash
chmod +x Pardus_Boot_Analyzer-x86_64.AppImage
./Pardus_Boot_Analyzer-x86_64.AppImage
```

### Arch Linux (AUR) Installation

You can install the application on Arch Linux or Arch-based distributions (Manjaro, EndeavourOS, etc.) directly via the AUR:
```bash
yay -S pardus-boot-analyzer-git
```
or
```bash
paru -S pardus-boot-analyzer-git
```

### Creating Debian and AppImage Packages

To compile and package the project:
```bash
./build_deb.sh
./build_appimage.sh
```

## License
This project is licensed under the [GPL-3.0 License](LICENSE).
