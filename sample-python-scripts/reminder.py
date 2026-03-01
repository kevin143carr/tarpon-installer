# popup_reminder.py
import os
from tkinter import messagebox

def popup_message(inputstr, comment, window=None):
    inputstr = inputstr + '' + comment
    if os.environ.get("TARPL_HEADLESS", "").strip().lower() in {"1", "true", "yes", "on"}:
        print(inputstr)
        return

    if window is not None:
        messagebox.showinfo("Reminder", inputstr, parent=window)
    else:
        messagebox.showinfo("Reminder", inputstr)
