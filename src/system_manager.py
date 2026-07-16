import subprocess
import re
import os
import shutil
import json

from src.autostart_manager import AutostartManager
from src.profile_manager import ProfileManager
from src.locale_mgr import tr

class SystemManager:
    def __init__(self):
        self.password = None
        self.root_process = None
        self._blame_data_cache = None
        self._total_boot_time_cache = None
        self._unit_file_states_cache = None
        self._system_info_cache = None
        
        # Instantiate sub-managers
        self.autostart = AutostartManager(self)
        self.profiles = ProfileManager(self)

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
                
        # Merge inactive/unloaded unit files from list-unit-files so they don't disappear when stopped and disabled
        try:
            file_output = subprocess.check_output(
                ["systemctl", "list-unit-files", "--no-pager", "--no-legend"],
                text=True
            )
            existing_names = {s["name"] for s in services}
            for line in file_output.strip().splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    if name not in existing_names and not name.endswith("@.service") and "@" not in name:
                        # Add as inactive/dead service
                        services.append({
                            "name": name,
                            "load": "loaded",
                            "active": "inactive",
                            "sub": "dead",
                            "description": ""
                        })
        except Exception:
            pass
            
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
        
        first_line = output.strip().splitlines()[0]
        
        # If there is a "=", the total boot time is after "="
        if "=" in first_line:
            target = first_line.split("=")[-1].strip()
        else:
            # Otherwise, it is after "finished in"
            if "finished in" in first_line:
                target = first_line.split("finished in")[-1].strip()
            else:
                target = first_line
                
        # Match time format from the target string (e.g. "1min 8.634s" or "35.473s")
        match = re.search(r"(\d+(?:\.\d+)?\s*(?:s|ms|min|m|h)(?:\s+\d+(?:\.\d+)?\s*(?:s|ms|min|m|h))*)", target)
        res = match.group(1) if match else target
        
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

    def __del__(self):
        if hasattr(self, "root_process") and self.root_process:
            try:
                self.root_process.stdin.write("exit\n")
                self.root_process.stdin.flush()
                self.root_process.wait(timeout=1)
            except Exception:
                try:
                    self.root_process.kill()
                except Exception:
                    pass

    def verify_sudo_password(self, password):
        try:
            if hasattr(self, "root_process") and self.root_process:
                try:
                    self.root_process.kill()
                except Exception:
                    pass
                self.root_process = None
                
            proc = subprocess.Popen(
                ["sudo", "-S", "bash"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            proc.stdin.write(password + "\n")
            proc.stdin.flush()
            
            proc.stdin.write("echo 'SUDO_OK'\n")
            proc.stdin.flush()
            
            authenticated = False
            for line in proc.stdout:
                if "SUDO_OK" in line:
                    authenticated = True
                    break
            
            if authenticated:
                self.root_process = proc
                self.password = password
                return True
            else:
                proc.kill()
                return False
        except Exception:
            return False

    def run_root_command(self, cmd_str):
        if hasattr(self, "root_process") and self.root_process and self.root_process.poll() is None:
            try:
                marker = "CMD_FINISHED_MARKER"
                self.root_process.stdin.write(f"{cmd_str} 2>&1\n")
                self.root_process.stdin.write(f"echo 'CMD_EXIT:'$? '{marker}'\n")
                self.root_process.stdin.flush()
                
                output_lines = []
                exit_code = 0
                for line in self.root_process.stdout:
                    if marker in line:
                        parts = line.strip().split()
                        if len(parts) >= 1 and parts[0].startswith("CMD_EXIT:"):
                            try:
                                exit_code = int(parts[0].split(":")[1])
                            except Exception:
                                exit_code = 1
                        break
                    output_lines.append(line)
                
                output_text = "".join(output_lines).strip()
                return exit_code == 0, output_text
            except Exception as e:
                return False, str(e)
        else:
            if not self.password:
                return False, tr("err_no_password")
            try:
                result = subprocess.run(
                    ["sudo", "-S", "sh", "-c", cmd_str],
                    input=self.password + "\n",
                    capture_output=True, text=True,
                    timeout=15
                )
                if result.returncode == 0:
                    return True, result.stdout.strip()
                else:
                    err = result.stderr or result.stdout
                    if "incorrect password" in err.lower() or "şifre" in err.lower():
                        self.password = None
                    return False, err.strip()
            except subprocess.TimeoutExpired:
                return False, tr("err_timeout_auth")
            except Exception as e:
                return False, str(e)

    def _run_auth(self, args):
        cmd_args = ["--no-pager", "--no-ask-password"] + args
        cmd_str = "systemctl " + " ".join(cmd_args)
        ok, msg = self.run_root_command(cmd_str)
        if ok:
            return True, tr("success_operation")
        else:
            return False, msg

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

    def get_dependencies(self, name):
        try:
            result = subprocess.run(
                ["systemctl", "list-dependencies", name, "--no-pager"],
                capture_output=True, text=True
            )
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

    def get_reverse_dependencies(self, name):
        try:
            result = subprocess.run(
                ["systemctl", "list-dependencies", name, "--reverse", "--no-pager"],
                capture_output=True, text=True
            )
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

    # --- Autostart Delegation ---
    def get_autostart_dir(self):
        return self.autostart.get_autostart_dir()

    def get_autostart_entries(self):
        return self.autostart.get_autostart_entries()

    def parse_desktop_file(self, filepath):
        return self.autostart.parse_desktop_file(filepath)

    def add_autostart_entry(self, name, command, comment="", icon="system-run", delay=0):
        return self.autostart.add_autostart_entry(name, command, comment, icon, delay)

    def save_autostart_entry(self, filepath, name, command, comment="", icon="system-run", enabled=True, delay=0):
        return self.autostart.save_autostart_entry(filepath, name, command, comment, icon, enabled, delay)

    def remove_autostart_entry(self, filepath):
        return self.autostart.remove_autostart_entry(filepath)

    def toggle_autostart_entry(self, filepath, enabled):
        return self.autostart.toggle_autostart_entry(filepath, enabled)

    def update_autostart_delay(self, filepath, delay):
        return self.autostart.update_autostart_delay(filepath, delay)

    def get_installed_applications(self):
        return self.autostart.get_installed_applications()

    # --- Profiles / Backup Delegation ---
    def apply_profile_batch(self, enable_list, disable_list):
        return self.profiles.apply_profile_batch(enable_list, disable_list)

    def create_backup(self):
        return self.profiles.create_backup()

    def get_backups(self):
        return self.profiles.get_backups()

    def restore_backup(self, filepath):
        return self.profiles.restore_backup(filepath)

    def get_system_info(self):
        if self._system_info_cache is None:
            os_name = "Linux"
            if os.path.exists("/etc/os-release"):
                try:
                    with open("/etc/os-release", "r") as f:
                        for line in f:
                            if line.startswith("PRETTY_NAME="):
                                os_name = line.split("=", 1)[1].strip().strip('"')
                                break
                except Exception:
                    pass
            
            kernel = "Unknown"
            try:
                kernel = subprocess.check_output(["uname", "-r"], text=True).strip()
            except Exception:
                pass
                
            ram = "Unknown"
            if os.path.exists("/proc/meminfo"):
                try:
                    with open("/proc/proc/meminfo" if False else "/proc/meminfo", "r") as f:
                        for line in f:
                            if line.startswith("MemTotal:"):
                                total_kb = int(line.split()[1])
                                ram = f"{total_kb / 1024 / 1024:.1f} GB"
                                break
                except Exception:
                    pass
            
            uptime = tr("unknown")
            if os.path.exists("/proc/uptime"):
                try:
                    with open("/proc/uptime", "r") as f:
                        uptime_seconds = float(f.readline().split()[0])
                        hours = int(uptime_seconds // 3600)
                        minutes = int((uptime_seconds % 3600) // 60)
                        if hours > 0:
                            uptime = f"{hours} {tr('unit_hours')} {minutes} {tr('unit_mins')}"
                        else:
                            uptime = f"{minutes} {tr('unit_mins')}"
                except Exception:
                    pass
                    
            self._system_info_cache = {
                "os": os_name,
                "kernel": kernel,
                "ram": ram,
                "uptime": uptime
            }
        return self._system_info_cache
