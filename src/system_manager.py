import subprocess
import re
import os
import shutil
import json

class SystemManager:
    def __init__(self):
        self.password = None
        self._blame_data_cache = None
        self._total_boot_time_cache = None
        self._unit_file_states_cache = None
        self._system_info_cache = None

    def clear_cache(self):
        self._blame_data_cache = None
        self._total_boot_time_cache = None
        self._unit_file_states_cache = None
        self._system_info_cache = None

    # --- Service & Device Management ---
    def get_services(self):
        output = subprocess.check_output(
            ["systemctl", "list-units", "--all", "--no-pager", "--no-legend"],
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
        if self._unit_file_states_cache is not None:
            return self._unit_file_states_cache
        output = subprocess.check_output(
            ["systemctl", "list-unit-files", "--type=service", "--no-pager", "--no-legend"],
            text=True
        )
        states = {}
        for line in output.strip().splitlines():
            parts = line.split()
            if len(parts) >= 2:
                states[parts[0]] = parts[1]
        self._unit_file_states_cache = states
        return states

    def get_blame_data(self):
        if self._blame_data_cache is not None:
            return self._blame_data_cache
        my_env = os.environ.copy()
        my_env["LC_ALL"] = "C"
        output = subprocess.check_output(["systemd-analyze", "blame"], text=True, env=my_env)
        data = []
        for line in output.strip().splitlines():
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                time_str, name = parts
                data.append({"name": name, "time": time_str})
        self._blame_data_cache = (data, output)
        return self._blame_data_cache

    def get_total_boot_time(self):
        if self._total_boot_time_cache is not None:
            return self._total_boot_time_cache
        my_env = os.environ.copy()
        my_env["LC_ALL"] = "C"
        output = subprocess.check_output(["systemd-analyze"], text=True, env=my_env)
        
        # If there is a "=", the total boot time is after "="
        if "=" in output:
            parts = output.split("=")
            match = re.search(r"([\d.]+(?:s|ms|min))", parts[-1])
            if match:
                self._total_boot_time_cache = (match.group(1), output.strip())
                return self._total_boot_time_cache
                
        match = re.search(r"([\d.]+(?:s|ms|min))", output)
        res = match.group(1) if match else output.strip()
        self._total_boot_time_cache = (res, output.strip())
        return self._total_boot_time_cache

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

    def verify_sudo_password(self, password):
        try:
            result = subprocess.run(
                ["sudo", "-S", "-v"],
                input=password + "\n",
                capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _run_auth(self, args):
        cmd_args = ["--no-pager", "--no-ask-password"] + args
        if not self.password:
            # Fallback: direct systemctl
            try:
                result = subprocess.run(
                    ["systemctl"] + cmd_args,
                    capture_output=True, text=True,
                    timeout=15
                )
                return result.returncode == 0, result.stderr or result.stdout
            except subprocess.TimeoutExpired:
                return False, "İşlem zaman aşımına uğradı (servis yanıt vermiyor)."
            except Exception as e:
                return False, str(e)
            
        try:
            result = subprocess.run(
                ["sudo", "-S", "systemctl"] + cmd_args,
                input=self.password + "\n",
                capture_output=True, text=True,
                timeout=15
            )
            if result.returncode == 0:
                return True, "İşlem başarılı."
            else:
                err = result.stderr or result.stdout
                if "incorrect password" in err.lower() or "şifre" in err.lower():
                    self.password = None
                return False, err
        except subprocess.TimeoutExpired:
            return False, "İşlem zaman aşımına uğradı (şifre yanlış veya servis yanıt vermiyor)."
        except Exception as e:
            return False, str(e)

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
        out = result.stdout.strip()
        if (not out or "-- no entries --" in out.lower() or "permission" in out.lower()) and self.password is not None:
            try:
                res = subprocess.run(
                    ["sudo", "-S", "journalctl", "-u", name, "--no-pager", "-n", str(lines)],
                    input=self.password, capture_output=True, text=True
                )
                if res.returncode == 0:
                    return res.stdout
            except Exception:
                pass
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
        if not self.password:
            return False, "Yönetici şifresi girilmedi."
            
        try:
            result = subprocess.run(
                ["sudo", "-S", "sh", "-c", shell_cmd],
                input=self.password + "\n",
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return True, "Profil başarıyla uygulandı."
            else:
                err = result.stderr or result.stdout
                if "incorrect password" in err.lower() or "şifre" in err.lower():
                    self.password = None
                return False, err
        except Exception as e:
            return False, str(e)

    def get_system_info(self):
        if self._system_info_cache is None:
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
            
            import platform
            kernel = platform.release()
            
            ram_str = "Bilinmiyor"
            if os.path.exists("/proc/meminfo"):
                try:
                    with open("/proc/meminfo", "r", encoding="utf-8") as f:
                        mem = {}
                        for line in f:
                            parts = line.split()
                            if len(parts) >= 2:
                                mem[parts[0].rstrip(":")] = int(parts[1])
                    total = mem.get("MemTotal", 0) / 1024 / 1024
                    avail = mem.get("MemAvailable", 0) / 1024 / 1024
                    used = total - avail
                    ram_str = f"{used:.1f} GB / {total:.1f} GB"
                except Exception:
                    pass
            self._system_info_cache = (os_name, kernel, ram_str)
        else:
            os_name, kernel, ram_str = self._system_info_cache
            
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

    def get_reverse_dependencies(self, name):
        try:
            result = subprocess.run(
                ["systemctl", "list-dependencies", "--reverse", name, "--no-pager"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                return []
            
            deps = []
            lines = result.stdout.strip().splitlines()
            if len(lines) > 1:
                for line in lines[1:]:
                    cleaned = line.replace("●", "").replace("├─", "").replace("└─", "").replace("│", "").strip()
                    if cleaned.endswith(".service"):
                        deps.append(cleaned)
            return deps
        except Exception:
            return []

    def create_backup(self):
        try:
            states = self.get_unit_file_states()
            backup_dir = os.path.expanduser("~/.config/pardus-boot-analyzer/backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            import datetime
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
            pretty_date = now.strftime("%d.%m.%Y %H:%M:%S")
            
            filepath = os.path.join(backup_dir, f"backup_{date_str}.json")
            data = {
                "timestamp": date_str,
                "name": f"Geri Dönüş Noktası ({pretty_date})",
                "services": states
            }
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True, filepath
        except Exception as e:
            return False, str(e)

    def get_backups(self):
        backup_dir = os.path.expanduser("~/.config/pardus-boot-analyzer/backups")
        if not os.path.exists(backup_dir):
            return []
        
        backups = []
        for name in os.listdir(backup_dir):
            if name.endswith(".json") and name.startswith("backup_"):
                fpath = os.path.join(backup_dir, name)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        data["filepath"] = fpath
                        backups.append(data)
                except Exception:
                    pass
        # Sort by timestamp descending
        backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return backups

    def restore_backup(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            backup_states = data["services"]
            current_states = self.get_unit_file_states()
            
            enable_list = []
            disable_list = []
            
            for svc, state in backup_states.items():
                if svc not in current_states:
                    continue
                curr = current_states[svc]
                if state in ("enabled", "enabled-runtime") and curr not in ("enabled", "enabled-runtime"):
                    enable_list.append(svc)
                elif state in ("disabled", "static", "indirect", "masked") and curr in ("enabled", "enabled-runtime"):
                    disable_list.append(svc)
                    
            if not enable_list and not disable_list:
                return True, "Sistem zaten bu yedek durumuna uygun."
                
            return self.apply_profile_batch(enable_list, disable_list)
        except Exception as e:
            return False, str(e)

