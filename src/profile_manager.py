import os
import json
from src.locale_mgr import tr
import subprocess

class ProfileManager:
    def __init__(self, system_manager):
        self.system_manager = system_manager

    def apply_profile_batch(self, enable_list, disable_list):
        self.system_manager.clear_cache()
        current_unit_states = self.system_manager.get_unit_file_states()
        current_active_states = {}
        for s in self.system_manager.get_services():
            current_active_states[s["name"]] = s["active"]
            
        to_enable = []
        to_start = []
        for svc in enable_list:
            unit_state = current_unit_states.get(svc, "unknown")
            active_state = current_active_states.get(svc, "unknown")
            if unit_state not in ("enabled", "enabled-runtime"):
                to_enable.append(svc)
            if active_state != "active":
                to_start.append(svc)
                
        to_disable = []
        to_stop = []
        for svc in disable_list:
            unit_state = current_unit_states.get(svc, "unknown")
            active_state = current_active_states.get(svc, "unknown")
            if unit_state in ("enabled", "enabled-runtime"):
                to_disable.append(svc)
            if active_state == "active":
                to_stop.append(svc)
                
        commands = []
        if to_enable:
            commands.append(f"systemctl enable {' '.join(to_enable)}")
        if to_start:
            commands.append(f"systemctl start {' '.join(to_start)}")
        if to_disable:
            commands.append(f"systemctl disable {' '.join(to_disable)}")
        if to_stop:
            commands.append(f"systemctl stop {' '.join(to_stop)}")
            
        if not commands:
            return True, tr("profile_applied")
            
        shell_cmd = " && ".join(commands)
        ok, msg = self.system_manager.run_root_command(shell_cmd)
        if ok:
            return True, tr("profile_applied")
        else:
            return False, msg

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
            self.system_manager.clear_cache()
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
