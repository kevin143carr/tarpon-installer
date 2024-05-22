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
        
    def showPopListbox(self, items, parentwindow):        
        boxw = tk.Toplevel(parentwindow)
        hasselected = tk.BooleanVar()
        
        hasselected.set(False)
        
        boxw.geometry("400x300")
        boxw.title("Please Select One")
        listbox = tk.Listbox(boxw, selectmode=tk.SINGLE)
        listbox.insert(0, *items)
        listbox.pack()
        get_selection_button = ttk.Button(boxw, 
            text="Get selection",
            command= lambda: self.get_selection(boxw, hasselected, listbox)
        )
        get_selection_button.pack()
        time.sleep(1)
        boxw.wait_variable(hasselected)
        boxw.destroy()
        return self.rtnval
