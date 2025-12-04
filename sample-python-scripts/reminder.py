# popup_reminder.py
import tkinter as tk
from tkinter import messagebox

def popup_message(inputstr, comment):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    inputstr =  inputstr + '' + comment
    messagebox.showinfo("Reminder", inputstr)
    root.destroy()