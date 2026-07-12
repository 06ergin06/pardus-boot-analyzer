import os
import re

class AutostartManager:
    def __init__(self, system_manager):
        self.system_manager = system_manager

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
            "comment": "",
            "icon": "system-run",
            "delay": 0,
            "enabled": True,
            "filepath": filepath
        }
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return info

        for line in lines:
            line = line.strip()
            if line.startswith("Name="):
                info["name"] = line.split("=", 1)[1]
            elif line.startswith("Exec="):
                exec_val = line.split("=", 1)[1]
                # Check delay logic
                if "sleep" in exec_val and "&&" in exec_val:
                    # e.g., sh -c "sleep 5 && myapp"
                    match = re.search(r"sleep\s+(\d+)\s*&&\s*\"?(.*?)\"?$", exec_val)
                    if match:
                        info["delay"] = int(match.group(1))
                        info["exec"] = match.group(2).rstrip('"')
                    else:
                        info["exec"] = exec_val
                else:
                    info["exec"] = exec_val
            elif line.startswith("Comment="):
                info["comment"] = line.split("=", 1)[1]
            elif line.startswith("Icon="):
                info["icon"] = line.split("=", 1)[1]
            elif line.startswith("X-GNOME-Autostart-enabled="):
                val = line.split("=", 1)[1].lower()
                info["enabled"] = (val == "true")
            elif line.startswith("X-GNOME-Autostart-Delay="):
                try:
                    info["delay"] = int(line.split("=", 1)[1])
                except ValueError:
                    pass
        return info

    def add_autostart_entry(self, name, command, comment="", icon="system-run", delay=0):
        filename = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()
        filename = filename.replace(" ", "_").lower() + ".desktop"
        filepath = os.path.join(self.get_autostart_dir(), filename)
        
        # If it exists, append a suffix to avoid overwriting
        counter = 1
        while os.path.exists(filepath):
            filename = filename.replace(".desktop", f"_{counter}.desktop")
            filepath = os.path.join(self.get_autostart_dir(), filename)
            counter += 1

        self.save_autostart_entry(filepath, name, command, comment, icon, True, delay)
        return filepath

    def save_autostart_entry(self, filepath, name, command, comment="", icon="system-run", enabled=True, delay=0):
        # Format executable command with optional sleep delay wrapper
        if delay > 0:
            final_command = f'sh -c "sleep {delay} && {command}"'
        else:
            final_command = command

        lines = [
            "[Desktop Entry]",
            "Type=Application",
            f"Name={name}",
            f"Exec={final_command}",
            f"Comment={comment}",
            f"Icon={icon}",
            f"X-GNOME-Autostart-enabled={'true' if enabled else 'false'}"
        ]
        if delay > 0:
            lines.append(f"X-GNOME-Autostart-Delay={delay}")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def remove_autostart_entry(self, filepath):
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def toggle_autostart_entry(self, filepath, enabled):
        info = self.parse_desktop_file(filepath)
        self.save_autostart_entry(filepath, info["name"], info["exec"], info["comment"], info["icon"], enabled, info["delay"])

    def update_autostart_delay(self, filepath, delay):
        info = self.parse_desktop_file(filepath)
        self.save_autostart_entry(filepath, info["name"], info["exec"], info["comment"], info["icon"], info["enabled"], delay)

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
                    if info["name"] and info["exec"] and not info["exec"].startswith("NoDisplay"):
                        apps.append(info)
                except Exception:
                    pass
        apps.sort(key=lambda x: x["name"].lower())
        return apps
