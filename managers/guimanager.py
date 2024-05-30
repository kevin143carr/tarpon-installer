import sys
import platform
import tkinter as tk
if sys.version_info[:3] < (3,9):
    from ttkbootstrap import ttk
else:
    import ttkbootstrap as ttk
from tkinter import font    
from tkscrolledframe import ScrolledFrame
from PIL import Image as Image, ImageTk as Itk
import logging
from iniinfo import iniInfo

logger = None

class GuiManager:
    bar = None
    taskitem = None
    section = None
    themename = "superhero"
    
    def optionsDialog(parent: tk.Tk, ini_info: iniInfo) -> None:
        optionsWindow = tk.Toplevel(parent)
        optionsWindow.geometry("600x300")
        # window.title(ini_info.installtitle)
        optionsWindow.resizable(False,False)
        optionsWindow.focusmodel(model="active")
        optionsWindow.after(100, lambda: optionsWindow.focus_force())

        # This centers the window
        optionsWindow.wait_visibility()
        x = parent.winfo_x() + parent.winfo_width()//2 - optionsWindow.winfo_width()//2
        y = parent.winfo_y() + parent.winfo_height()//2 - optionsWindow.winfo_height()//2
        optionsWindow.geometry(f"+{x}+{y}")

        functionFrame = ttk.Frame(optionsWindow, height=240, width=340)
        functionFrame.pack(side="top", expand=0, fill="both")
        
        scrolledFrame = ScrolledFrame(functionFrame,scrollbars = "vertical")
        scrolledFrame.pack(fill=tk.BOTH, padx=20, expand = "yes", pady=5)

        scrolledFrame.bind_arrow_keys(functionFrame)
        scrolledFrame.bind_scroll_wheel(functionFrame)
        inner_frame = scrolledFrame.display_widget(tk.Frame)  

        for row in range(len(ini_info.options)):
            vals = ini_info.options.keys()
            value = list(vals)[row]

            if value not in ini_info.optionvals:
                ini_info.optionvals[value]=tk.StringVar(value='0')

            lb = ttk.Label(inner_frame, text=ini_info.options[value])
            cb = ttk.Checkbutton(inner_frame, variable=ini_info.optionvals[value], onvalue='1', offvalue='0')
            lb.grid(row=row,
                    column=1, stick="W")
            cb.grid(row=row,
                    column=0, stick="W")

        optionbutton = ttk.Button(optionsWindow, text="Close", width=20, command=optionsWindow.destroy)
        optionbutton.pack()
        
    def buildLeftFrame(self, window, functiontitle, ini_info: iniInfo, installfunc):
        self.taskitem = tk.StringVar()
        
        # Load image
        image = Image.open(ini_info.logoimage)  # Replace "image_path.jpg" with the path to your image
        image = image.resize((300, 300))
        photo = Itk.PhotoImage(image)
        
        # Create the first frame with a red background
        left_frame = ttk.Frame(window, width=400, height=420)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Display image
        label = ttk.Label(left_frame, image=photo)
        label.image = photo  # Keep a reference to avoid garbage collection
        label.pack(padx=10, pady=5)
        
        # Create a LabelFrame below the image with yellow background
        control_frame = ttk.Frame(left_frame, relief=tk.RAISED, borderwidth=1)
        control_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Create a Label inside the control frame for status
        status_label = ttk.Label(control_frame, wraplength = 350, textvariable=self.taskitem,width=40, anchor="w", justify="left")        
        status_label.pack(padx=5, pady=5, anchor="w")
               
        self.taskitem.set("INSTALL TASK:")        

        install_button = ttk.Button(control_frame, text=ini_info.buttontext, command=lambda: installfunc(ini_info, install_button, window))
        install_button.pack(fill=tk.X, pady=5, padx=5, side=tk.BOTTOM, anchor="s")
           
    def on_focus_in(self, event, entry: str)->None:
        movetoval =  int(entry)/(entry_boxes)
        canvas.yview_moveto(movetoval)
        
    def buildRightFrame(self, window, functiontitle, ini_info: iniInfo, installfunc)->None:
        global canvas, entry_boxes
        
        isosx = platform.system() == "Darwin"
        
        self.section = tk.StringVar()
        
        right_frame = ttk.Frame(window, width=400, height=420)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        title_frame = ttk.Frame(right_frame, relief=tk.RAISED, borderwidth=1)
        title_frame.pack(padx=5, pady=5, expand=True, side=tk.TOP, fill=tk.BOTH, anchor="n")
        title_label = ttk.Label(title_frame, text=ini_info.installtitle,width=40, anchor="center", font="Arial 17 bold")
        title_label.pack(pady=(5, 5))

        self.section.set("SECTION:")
        # Create a Label inside the control frame for status
        section_label = ttk.Label(title_frame, textvariable=self.section, width=300, anchor="w", justify="left")
        section_label.pack(padx=5, pady=(5, 5))
        
        self.bar = ttk.Progressbar(title_frame,orient=tk.HORIZONTAL,length=310)
        self.bar.pack()        
        
        functionTitleLabel = ttk.Label(title_frame,text=functiontitle, anchor="center", font="Arial 16 bold")
        functionTitleLabel.pack(padx=5, pady=10, anchor="center")
        
        options_button = ttk.Button(title_frame, text="Options", width=18, command=lambda: GuiManager.optionsDialog(window, ini_info))
        options_button.pack(fill=tk.X, pady=5, padx=10, side=tk.BOTTOM, anchor="s")
        
        scrolledFrame = ScrolledFrame(title_frame,scrollbars = "vertical")
        scrolledFrame.pack(fill=tk.BOTH, padx=10, expand = "yes", pady=5)

        inner_frame = scrolledFrame.display_widget(tk.Frame)        
        scrolledFrame.bind_arrow_keys(inner_frame)
        scrolledFrame.bind_scroll_wheel(inner_frame)
       
        window.update()     
        canvas = scrolledFrame._canvas
        canvas.update_idletasks()          
        widthofframe = canvas.winfo_width()
        entryboxlen = self.calculateEntryBoxWidth(window, ini_info.userinput, widthofframe)        

        # Add some labels and entry boxes to the inner frame
        userinputkeys = list(ini_info.userinput.keys())
        for i in range(len(ini_info.userinput)):
            var = tk.StringVar()
            keyvalue = userinputkeys[i]
            label = ttk.Label(inner_frame, text=ini_info.userinput[keyvalue], justify="left")
            label.grid(row=i, column=0, pady=5, padx=5, sticky="w")
            if isosx:
                entry = ttk.Entry(inner_frame, justify="left", textvariable=var)
            else:
                entry = ttk.Entry(inner_frame, justify="left", textvariable=var, width=entryboxlen)
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            
            # Bind the focus in event to the on_focus_in function for each entry box
            entry.bind("<FocusIn>", lambda event, entry="{}".format(i): self.on_focus_in(event, entry))
            ini_info.userinput[keyvalue] = var                      
        
        entry_boxes = len(ini_info.userinput)    

        if (len(ini_info.options) == 0):
            options_button.config(state=tk.DISABLED)
            
    def calculateEntryBoxWidth(self, window, userinput: dict, widthofframe: int) -> int:
            
        right_frame = ttk.Frame(window)
            
        # right_frame.withdraw()  # Hide the root window
        average_char_width = font.Font().measure('1')  
                
        maxlabelwidth = 0
        userinputkeys = list(userinput.keys())
        for i in range(len(userinput)):        
            key = userinputkeys[i]
            widthoflabel = font.Font().measure(userinput[key])
            if(widthoflabel > maxlabelwidth):
                maxlabelwidth = widthoflabel
                
        charwidthofframe = widthofframe//average_char_width
        charwidthoflabel =  maxlabelwidth//average_char_width
        
        entrycharactersize = max(1, charwidthofframe-charwidthoflabel)
        
        right_frame.destroy()        
        return   entrycharactersize + (average_char_width)            
        
    def buildGUI(self, window, functiontitle, ini_info: iniInfo, installfunc):
        global logger
        logger = logging.getLogger("logger")
        geometrystr: str = ""
        self.themename = ini_info.themename
        
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        width = 820
        height = 420
        x = int((screen_width/2) - (width/2))
        y = int((screen_height/2) - (height/1.5))
        
        geometrystr = f"{width}x{height}+{x}+{y}"
                    
        window.geometry(geometrystr)
        window.title(ini_info.installtitle)
        window.resizable(False,False)
        window.focusmodel(model="passive")
        self.buildLeftFrame(window, functiontitle, ini_info, installfunc)
        self.buildRightFrame(window, functiontitle, ini_info, installfunc)
