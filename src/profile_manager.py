import os
import json
from src.locale_mgr import tr
import subprocess

class ProfileManager:
    def __init__(self, system_manager):
        self.system_manager = system_manager

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
            return True, tr("profile_no_changes")
            
        shell_cmd = " && ".join(commands)
        if not self.system_manager.password:
            return False, tr("err_no_password")
            
        try:
            result = subprocess.run(
                ["sudo", "-S", "sh", "-c", shell_cmd],
                input=self.system_manager.password + "\n",
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return True, tr("profile_applied")
            else:
                err = result.stderr or result.stdout
                if "incorrect password" in err.lower() or "şifre" in err.lower():
                    self.system_manager.password = None
                return False, err
        except Exception as e:
            return False, str(e)

    def create_backup(self):
        try:
            states = self.system_manager.get_unit_file_states()
            backup_dir = os.path.expanduser("~/.config/pardus-boot-analyzer/backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            import datetime
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
            pretty_date = now.strftime("%d.%m.%Y %H:%M:%S")
            
            filepath = os.path.join(backup_dir, f"backup_{date_str}.json")
            data = {
                "timestamp": date_str,
                "name": tr("restore_point_name").format(pretty_date),
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
        backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return backups

    def restore_backup(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            backup_states = data["services"]
            current_states = self.system_manager.get_unit_file_states()
            
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
                return True, tr("profile_already_matching_backup")
                
            return self.apply_profile_batch(enable_list, disable_list)
        except Exception as e:
            return False, str(e)
