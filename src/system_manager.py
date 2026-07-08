import subprocess
import re


class SystemManager:
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
        # Direct systemctl first
        result = subprocess.run(
            ["systemctl"] + args,
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return True, result.stdout + result.stderr
        # Auth failure? Try pkexec for GUI password dialog
        stderr_lower = result.stderr.lower()
        if any(w in stderr_lower for w in ("authentication", "permission", "not authorized", "interactive")):
            result = subprocess.run(
                ["pkexec", "systemctl"] + args,
                capture_output=True, text=True
            )
            return result.returncode == 0, result.stdout + result.stderr
        return False, result.stdout + result.stderr

    def get_service_status(self, name):
        result = subprocess.run(
            ["systemctl", "is-enabled", name],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    def get_journal_log(self, name, lines=50):
        result = subprocess.run(
            ["journalctl", "-u", name, "--no-pager", "-n", str(lines)],
            capture_output=True, text=True
        )
        return result.stdout if result.returncode == 0 else result.stderr

    def get_disabled_services(self):
        output = subprocess.check_output(
            ["systemctl", "list-unit-files", "--type=service", "--state=disabled", "--no-pager", "--no-legend"],
            text=True
        )
        services = []
        for line in output.strip().splitlines():
            parts = line.split()
            if parts:
                services.append({"name": parts[0], "state": parts[1] if len(parts) > 1 else "disabled"})
        return services

    def get_masked_services(self):
        output = subprocess.check_output(
            ["systemctl", "list-unit-files", "--type=service", "--state=masked", "--no-pager", "--no-legend"],
            text=True
        )
        services = []
        for line in output.strip().splitlines():
            parts = line.split()
            if parts:
                services.append({"name": parts[0], "state": parts[1] if len(parts) > 1 else "masked"})
        return services

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
