import platform
import subprocess
from tkinter import messagebox


def _linux_reboot_command(delay_seconds: int) -> list[str]:
    return [
        "sh",
        "-c",
        f'echo "REBOOTING in {delay_seconds} seconds"; sleep {delay_seconds}; reboot',
    ]


def _windows_reboot_command(delay_seconds: int) -> list[str]:
    return [
        "shutdown",
        "/r",
        "/t",
        str(delay_seconds),
    ]


def _schedule_reboot(delay_seconds: int) -> None:
    system_name = platform.system()
    if system_name == "Windows":
        command = _windows_reboot_command(delay_seconds)
    else:
        command = _linux_reboot_command(delay_seconds)

    subprocess.Popen(
        command,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def prompt_and_schedule_reboot(delay_seconds, window=None) -> None:
    delay = int(delay_seconds)
    prompt = "Do you wish to reboot your system now?"

    if window is not None:
        should_reboot = messagebox.askyesno("User Question", prompt, parent=window)
    else:
        should_reboot = messagebox.askyesno("User Question", prompt)

    if should_reboot:
        _schedule_reboot(delay)
