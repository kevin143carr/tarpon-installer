# popup_reminder.py
import os
import tkinter as tk
from tkinter import messagebox

def popup_message(inputstr, comment):
    inputstr = inputstr + '' + comment
    if os.environ.get("TARPL_HEADLESS", "").strip().lower() in {"1", "true", "yes", "on"}:
        print(inputstr)
        return

    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Reminder", inputstr)
    root.destroy()
