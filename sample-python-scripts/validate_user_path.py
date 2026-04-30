import os
from tkinter import messagebox


def validate_user_path(field_label, path_value, window=None):
    value = (path_value or "").strip()
    invalid = (value == "") or (value == "/") or ("//" in value)

    if not invalid:
        return

    message = (
        f"The location provided for {field_label} was blank or is not supported:\n\n"
        f"{value}\n\n"
        "The installer will now exit. You will need to run the installer again."
    )

    if os.environ.get("TARPL_HEADLESS", "").strip().lower() in {"1", "true", "yes", "on"}:
        print(message)
    elif window is not None:
        messagebox.showerror(field_label, message, parent=window)
    else:
        messagebox.showerror(field_label, message)

    raise SystemExit(1)
