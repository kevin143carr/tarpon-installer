import tkinter as tk
from tkinter import ttk

class PopListbox:
    rtnval = ""
    
    def get_selection(self, window, hasselected, listbox):
        # This returns a tuple containing the indices (= the position)
        # of the items selected by the user.
        indices = listbox.curselection()
        if not indices:
            return indices
        self.rtnval = listbox.get(indices[0])
        hasselected.set(True)
        return indices
    
    def showPopListbox(self, items, parent, titletext):        
        root = tk.Toplevel(parent)
        hasselected = tk.BooleanVar()
        hasselected.set(False)

        dialog_width = 400
        dialog_height = 300
        root.resizable(False, False)
        root.title(titletext)
        root.transient(parent)

        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        list_frame = tk.Frame(frame)
        list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        listbox.insert(tk.END, *items)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.config(command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill = tk.Y)

        get_selection_button = ttk.Button(root,
            text="Get selection",
            command= lambda: self.get_selection(root, hasselected, listbox)
        )
        get_selection_button.pack(pady=5, padx=10, fill=tk.X)

        parent.update_idletasks()
        root.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x_position = parent_x + max((parent_width - dialog_width) // 2, 0)
        y_position = parent_y + max((parent_height - dialog_height) // 2, 0)
        root.geometry(f"{dialog_width}x{dialog_height}+{x_position}+{y_position}")

        root.lift(parent)
        root.grab_set()
        listbox.focus_set()
        if items:
            listbox.selection_set(0)
            listbox.activate(0)

        root.wait_variable(hasselected)
        root.destroy()
        return self.rtnval    
        
