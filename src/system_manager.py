import subprocess
import re
import os
import shutil

class SystemManager:
    # --- Service & Device Management ---
    def get_services(self):
        output = subprocess.check_output(
            ["systemctl", "list-units", "--type=service", "--all", "--no-pager", "--no-legend"],
            text=True
        )
        services = []
        for line in output.strip().splitlines():
            line = line.strip().lstrip("\u25cf").strip()
            parts = line.split()
            if len(parts) >= 4:
                services.append({
                    "name": parts[0],
                    "load": parts[1],
                    "active": parts[2],
                    "sub": parts[3],
                    "description": " ".join(parts[4:]) if len(parts) > 4 else ""
                })
        return services

    def get_unit_file_states(self):
        output = subprocess.check_output(
            ["systemctl", "list-unit-files", "--type=service", "--no-pager", "--no-legend"],
            text=True
        )
        states = {}
        for line in output.strip().splitlines():
            parts = line.split()
            if len(parts) >= 2:
                states[parts[0]] = parts[1]
        return states

    def get_blame_data(self):
        output = subprocess.check_output(["systemd-analyze", "blame"], text=True)
        data = []
        for line in output.strip().splitlines():
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                time_str, name = parts
                data.append({"name": name, "time": time_str})
        return data, output

    def get_total_boot_time(self):
        output = subprocess.check_output(["systemd-analyze"], text=True)
        match = re.search(r"[\d.]+(?:s|ms|min)", output)
        return match.group(0) if match else output.strip(), output

    def enable_service(self, name):
        return self._run_auth(["enable", name])

    def disable_service(self, name):
        return self._run_auth(["disable", name])

    def start_service(self, name):
        return self._run_auth(["start", name])

    def stop_service(self, name):
        return self._run_auth(["stop", name])

    def mask_service(self, name):
        return self._run_auth(["mask", name])

    def unmask_service(self, name):
        return self._run_auth(["unmask", name])

    def _run_auth(self, args):
        # Run using pkexec without redirecting output so it can access terminal TTY if needed
        try:
            result = subprocess.run(
                ["pkexec", "systemctl"] + args
            )
            if result.returncode == 0:
                return True, "İşlem başarılı."
            else:
                return False, "Yetkilendirme başarısız oldu veya işlem iptal edildi."
        except FileNotFoundError:
            pass
        
        # Fallback: direct systemctl
        result = subprocess.run(
            ["systemctl"] + args,
            capture_output=True, text=True
        )
        return result.returncode == 0, result.stderr or result.stdout

    def get_service_status(self, name):
        result = subprocess.run(
            ["systemctl", "is-enabled", name],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    def get_journal_log(self, name, lines=100):
        result = subprocess.run(
            ["journalctl", "-u", name, "--no-pager", "-n", str(lines)],
            capture_output=True, text=True
        )
        return result.stdout if result.returncode == 0 else result.stderr

    def get_device_units(self):
        output = subprocess.check_output(
            ["systemctl", "list-units", "--type=device", "--all", "--no-pager", "--no-legend"],
            text=True
        )
        units = []
        for line in output.strip().splitlines():
            line = line.strip().lstrip("\u25cf").strip()
            parts = line.split()
            if len(parts) >= 4:
                units.append({
                    "name": parts[0],
                    "load": parts[1],
                    "active": parts[2],
                    "sub": parts[3],
                    "description": " ".join(parts[4:]) if len(parts) > 4 else ""
                })
        return units

    # --- Autostart Management (Faz 4) ---
    def get_autostart_dir(self):
        path = os.path.expanduser("~/.config/autostart")
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return path

    def get_autostart_entries(self):
        autostart_dir = self.get_autostart_dir()
        entries = []
        if not os.path.exists(autostart_dir):
            return entries

        for filename in os.listdir(autostart_dir):
            if filename.endswith(".desktop"):
                filepath = os.path.join(autostart_dir, filename)
                entries.append(self.parse_desktop_file(filepath))
        return entries

    def parse_desktop_file(self, filepath):
        info = {
            "name": "",
            "exec": "",
            "icon": "system-run",
            "comment": "",
            "enabled": True,
            "delay": 0,
            "filepath": filepath,
            "filename": os.path.basename(filepath)
        }
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                in_desktop_entry = False
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line == "[Desktop Entry]":
                        in_desktop_entry = True
                        continue
                    if line.startswith("[") and line.endswith("]"):
                        in_desktop_entry = False
                        continue
                    if in_desktop_entry and "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip()
                        if key == "Name":
                            info["name"] = val
                        elif key == "Exec":
                            # Parse delay from Exec if structured like sleep X && command
                            m = re.match(r"^sleep\s+(\d+)\s*(?:&&|;)\s*(.*)$", val)
                            if m:
                                info["delay"] = int(m.group(1))
                                info["exec"] = m.group(2)
                            else:
                                info["exec"] = val
                        elif key == "Icon":
                            info["icon"] = val if val else "system-run"
                        elif key == "Comment":
                            info["comment"] = val
                        elif key in ("X-GNOME-Autostart-enabled", "X-KDE-Autostart-enabled"):
                            info["enabled"] = (val.lower() != "false")
                        elif key == "Hidden":
                            if val.lower() == "true":
                                info["enabled"] = False
                        elif key == "X-GNOME-Autostart-Delay":
                            try:
                                info["delay"] = int(val)
                            except ValueError:
                                pass
        except Exception:
            pass

        if not info["name"]:
            info["name"] = os.path.splitext(os.path.basename(filepath))[0]
        return info

    def add_autostart_entry(self, name, command, comment="", icon="system-run", delay=0):
        # Generate safe filename
        safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).lower()
        if not safe_name:
            safe_name = "custom-app"
        
        filename = f"{safe_name}.desktop"
        autostart_dir = self.get_autostart_dir()
        filepath = os.path.join(autostart_dir, filename)
        
        # Ensure name uniqueness
        counter = 1
        while os.path.exists(filepath):
            filename = f"{safe_name}-{counter}.desktop"
            filepath = os.path.join(autostart_dir, filename)
            counter += 1

        self.save_autostart_entry(filepath, name, command, comment, icon, True, delay)
        return filepath

    def save_autostart_entry(self, filepath, name, command, comment="", icon="system-run", enabled=True, delay=0):
        exec_val = command
        # If there is a delay, write it to X-GNOME-Autostart-Delay
        # We also support GNOME delay via key. We can do both key and Exec sleep wrapper to ensure compatibility
        if delay > 0:
            exec_val = f"sleep {delay} && {command}"

        content = [
            "[Desktop Entry]",
            "Type=Application",
            f"Name={name}",
            f"Exec={exec_val}",
            f"Icon={icon}",
            f"Comment={comment}",
            f"X-GNOME-Autostart-enabled={'true' if enabled else 'false'}",
            f"X-GNOME-Autostart-Delay={delay}"
        ]
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(content) + "\n")

    def remove_autostart_entry(self, filepath):
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def toggle_autostart_entry(self, filepath, enabled):
        info = self.parse_desktop_file(filepath)
        # Restore full exec (which includes sleep if there was a delay)
        cmd = info["exec"]
        self.save_autostart_entry(filepath, info["name"], cmd, info["comment"], info["icon"], enabled, info["delay"])

    def update_autostart_delay(self, filepath, delay):
        info = self.parse_desktop_file(filepath)
        cmd = info["exec"]
        self.save_autostart_entry(filepath, info["name"], cmd, info["comment"], info["icon"], info["enabled"], delay)

    def get_installed_applications(self):
        apps = []
        sys_apps_dir = "/usr/share/applications"
        if not os.path.exists(sys_apps_dir):
            return apps
        
        for filename in os.listdir(sys_apps_dir):
            if filename.endswith(".desktop"):
                filepath = os.path.join(sys_apps_dir, filename)
                try:
                    info = self.parse_desktop_file(filepath)
                    # Filter out non-application entries or files without executable
                    if info["name"] and info["exec"] and not info["exec"].startswith("NoDisplay"):
                        # Don't show system-critical settings managers in standard list unless requested
                        apps.append(info)
                except Exception:
                    pass
        # Sort alphabetically
        apps.sort(key=lambda x: x["name"].lower())
        return apps

    # --- Batch Profile Management (Faz 5) ---
    def apply_profile_batch(self, enable_list, disable_list):
        commands = []
        if enable_list:
            svc_str = " ".join(enable_list)
            commands.append(f"systemctl enable {svc_str}")
            commands.append(f"systemctl start {svc_str}")
        if disable_list:
            svc_str = " ".join(disable_list)
            commands.append(f"systemctl disable {svc_str}")
            commands.append(f"systemctl stop {svc_str}")
            
        if not commands:
            return True, "Herhangi bir değişiklik yapılması gerekmiyor."
            
        shell_cmd = " && ".join(commands)
        try:
            result = subprocess.run(
                ["pkexec", "sh", "-c", shell_cmd]
            )
            if result.returncode == 0:
                return True, "Profil başarıyla uygulandı."
            else:
                return False, "Yetkilendirme başarısız oldu veya işlem iptal edildi."
        except Exception as e:
            return False, str(e)

    def get_system_info(self):
        # OS Info
        os_name = "Linux"
        if os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("NAME="):
                            os_name = line.split("=")[1].strip().strip('"')
                        elif line.startswith("VERSION_ID="):
                            v = line.split("=")[1].strip().strip('"')
                            os_name = f"{os_name} {v}"
            except Exception:
                pass
        
        # Kernel release
        import platform
        kernel = platform.release()
        
        # RAM usage
        ram_str = "Bilinmiyor"
        if os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo", "r", encoding="utf-8") as f:
                    mem = {}
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 2:
                            mem[parts[0].rstrip(":")] = int(parts[1])
                total = mem.get("MemTotal", 0) / 1024 / 1024  # GB
                avail = mem.get("MemAvailable", 0) / 1024 / 1024  # GB
                used = total - avail
                ram_str = f"{used:.1f} GB / {total:.1f} GB"
            except Exception:
                pass
                
        # Uptime
        uptime_str = "Bilinmiyor"
        if os.path.exists("/proc/uptime"):
            try:
                with open("/proc/uptime", "r", encoding="utf-8") as f:
                    uptime_seconds = float(f.readline().split()[0])
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                if hours > 0:
                    uptime_str = f"{hours} saat {minutes} dakika"
                else:
                    uptime_str = f"{minutes} dakika"
            except Exception:
                pass
                
        return {
            "os": os_name,
            "kernel": kernel,
            "ram": ram_str,
            "uptime": uptime_str
        }

    def get_dependencies(self, name):
        result = subprocess.run(
            ["systemctl", "list-dependencies", name, "--no-pager"],
            capture_output=True, text=True
        )
        return result.stdout if result.returncode == 0 else result.stderr

