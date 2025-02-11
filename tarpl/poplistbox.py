import tkinter as tk
from tkinter import messagebox, ttk
import time

class PopListbox:
    rtnval = ""
    
    def get_selection(self, window, hasselected, listbox):
        # This returns a tuple containing the indices (= the position)
        # of the items selected by the user.
        indices = listbox.curselection()
        self.rtnval = listbox.get(indices)
        hasselected.set(True)
        return indices
    
    def showPopListbox(self, items, parent, titletext):        
        root = tk.Toplevel(parent)
        hasselected = tk.BooleanVar()
        
        hasselected.set(False)
        
        root.geometry("400x300")
        root.resizable(False, False)
        
        root.title(titletext)
        # Center the popup to the parent window
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
    
        x_position = parent_x + (parent_width // 2) - (400 // 2)
        y_position = parent_y + (parent_height // 2) - (300 // 2)
        root.geometry(f"400x300+{x_position}+{y_position}")        
        
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        listbox = tk.Listbox(frame, selectmode=tk.SINGLE)
        listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        listbox.insert(0, *items)
        listbox.pack()
        scrollbar = ttk.Scrollbar(listbox, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.config(command = listbox.yview)
        listbox.config(yscrollcommand = scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill = tk.Y)
        
        get_selection_button = ttk.Button(root,
            text="Get selection",
            command= lambda: self.get_selection(root, hasselected, listbox)
        )        
        #get_selection_button.pack(fill=tk.BOTH)
        get_selection_button.pack(pady=5, padx=10, fill=tk.X)
        
        time.sleep(1)
        root.wait_variable(hasselected)
        root.destroy()
        return self.rtnval    
        
