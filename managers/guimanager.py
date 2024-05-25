import tkinter as tk
from ttkbootstrap import ttk
from PIL import Image as Image, ImageTk as Itk
import logging

logger = None

class GuiManager:
    bar = None
    taskitem = None
    section = None
        
    border_effects = {
        "flat": tk.FLAT,
        "sunken": tk.SUNKEN,
        "raised": tk.RAISED,
        "groove": tk.GROOVE,
        "ridge": tk.RIDGE
        }    
    
    def optionsDialog(parent, ini_info):
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
        
        # Create a scrollable frame in the blue frame
        scrollable_frame = ttk.Frame(functionFrame)
        scrollable_frame.pack(fill=tk.BOTH, padx=20, pady=5)
        
        # Add a scrollbar
        scrollbar = tk.Scrollbar(scrollable_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Configure the scrollable frame to use the scrollbar
        canvas = tk.Canvas(scrollable_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
    
        # Create a frame inside the canvas to hold the labels and entry boxes
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")        

        for row in range(len(ini_info.options)):
            vals = ini_info.options.keys()
            value = list(vals)[row]

            ini_info.optionvals[value]=tk.StringVar(value='0')

            lb = ttk.Label(inner_frame, text=ini_info.options[value])
            cb = ttk.Checkbutton(inner_frame, variable=ini_info.optionvals[value], onvalue='1', offvalue='0')
            lb.grid(row=row,
                    column=1, stick="W")
            cb.grid(row=row,
                    column=0, stick="W")

        optionsButton = ttk.Button(optionsWindow, text="Close", width=20, command=optionsWindow.destroy).place(relx=.5, y=280,anchor=tk.CENTER)
        # optionsButton.pack()
        
    def buildLeftFrame(self, window, functiontitle, ini_info, installfunc):
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
        control_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a Label inside the control frame for status
        status_label = ttk.Label(control_frame, wraplength = 350, textvariable=self.taskitem,width=40, anchor="w", justify="left")        
        status_label.pack(padx=5, pady=5, anchor="w")
               
        self.taskitem.set("INSTALL TASK:")        

        install_button = ttk.Button(control_frame, text=ini_info.buttontext, command=lambda: installfunc(ini_info, install_button, window))
        install_button.pack(fill=tk.X, pady=5, padx=5, side=tk.BOTTOM, anchor="s")
           
    def on_focus_in(self, event):
        # Get the y-coordinate of the focused widget relative to the canvas
        entry_y = canvas.canvasy(event.widget.winfo_rooty())
        # Get the height of the canvas
        canvas_height = canvas.winfo_height()
        # Determine the scroll direction based on the position of the focused entry box
        if entry_y > canvas_height:
            # Scroll the canvas upward to make the entry box visible
            canvas.yview_scroll(1, "units")
        elif entry_y < 0:
            # Scroll the canvas downward to make the entry box visible
            canvas.yview_scroll(-1, "units")

        
    def buildRightFrame(self, window, functiontitle, ini_info, installfunc):
        global canvas, entry_boxes
        
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
        
        options_button = tk.Button(title_frame, text="Options", width=20, command=lambda: GuiManager.optionsDialog(window, ini_info))
        options_button.pack(fill=tk.X, pady=5, padx=5, side=tk.BOTTOM, anchor="s")        
        
        # Create a scrollable frame in the blue frame
        scrollable_frame = ttk.Frame(title_frame)
        scrollable_frame.pack(fill=tk.BOTH, padx=20, pady=5)
    
        # Add a scrollbar
        scrollbar = tk.Scrollbar(scrollable_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Configure the scrollable frame to use the scrollbar
        canvas = tk.Canvas(scrollable_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
    
        # Create a frame inside the canvas to hold the labels and entry boxes
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")       
    
        entry_boxes = []

        # Add some labels and entry boxes to the inner frame
        userinputkeys = list(ini_info.userinput.keys())
        for i in range(len(ini_info.userinput)):
            var = tk.StringVar()
            keyvalue = userinputkeys[i]
            label = ttk.Label(inner_frame, text=ini_info.userinput[keyvalue], justify="left")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(inner_frame, justify="left", textvariable=var)
            entry.grid(row=i, column=1, padx=5, pady=5)
            
            # Bind the focus in event to the on_focus_in function for each entry box
            entry.bind("<FocusIn>", self.on_focus_in)
            ini_info.userinput[keyvalue] = var                      
                        
        # Bind the scrollbar to the canvas
        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))                       
            
        canvas.bind("<Configure>", update_scroll_region)       


        if (len(ini_info.options) == 0):
            options_button.config(state=tk.DISABLED)
        
        
        
    def buildGUI(self, window, functiontitle, ini_info, installfunc):
        global logger
        logger = logging.getLogger("logger")
                    
        window.geometry("800x420")
        window.title(ini_info.installtitle)
        window.resizable(False,False)
        window.focusmodel(model="passive")
        self.buildLeftFrame(window, functiontitle, ini_info, installfunc)
        self.buildRightFrame(window, functiontitle, ini_info, installfunc)


    def buildGUIOG(self, window, functiontitle, ini_info, installfunc):
        logger = logging.getLogger("logger")
        display_list = []
        optionbuttonresize = 0
        
        count = 0
        if "DISPLAY" in ini_info.username:
            display_list.append("Username")
            count+=1
        if "DISPLAY" in ini_info.password:
            display_list.append("Password")
            count+=1
        if "DISPLAY" in ini_info.host:
            display_list.append("Host IP")
            count+=1
        
        if count > 0:
            output = self.display_dict
            if output == None:
                logger.warning("Installation Cancelled")
                return
        
        window.geometry("800x420")
        window.title(ini_info.installtitle)
        window.resizable(False,False)
        window.focusmodel(model="passive")
        
        for row in range(len(ini_info.options)):
            vals = ini_info.options.keys()
            value = list(vals)[row]
            ini_info.optionvals[value]=tk.StringVar(value='0')
        
        section = tk.StringVar()
        taskitem = tk.StringVar()
        
        PicFrame = tk.Frame(window, height=380, width=380, relief=tk.RAISED, borderwidth=3)
        PicFrame.place(x=10,y=10)
        
        if(ini_info.logoimage != ""):
            try:
                titleimage=Image.open(ini_info.logoimage)
            except Exception as ex:
                logger.error(ex)
                print("Problem loading {} Image File".format(ini_info.logoimage))
                raise SystemExit
        
        titleimage = titleimage.resize((300,300))
        titlepic = Itk.PhotoImage(titleimage)
        piclabel = tk.Label(PicFrame, image=titlepic)
        piclabel.image = titlepic
        piclabel.place(relx=.5, rely=.5, anchor=tk.CENTER)
        
        TitleFrame = tk.Frame(window, height=100, width=390, relief=tk.RAISED, borderwidth=3)
        TitleFrame.place(x=400, y=10)
        TitleLabel = tk.Label(TitleFrame, text=ini_info.installtitle, font="Arial 17 bold")
        TitleLabel.place(relx=.5, y=20, anchor=tk.CENTER)
        tk.Label(TitleFrame,textvariable=section).place(x=10, y=45, anchor="w")
        
        bar = ttk.Progressbar(TitleFrame,orient=tk.HORIZONTAL,length=310)
        bar.place(relx=.5, y=70,anchor=tk.CENTER)
        
        if(len(ini_info.options) > 0):
            optionbuttonresize = 30
        
        functionFrame = tk.Frame(window, height=155 - optionbuttonresize, width=365, relief=tk.RAISED, borderwidth=3)
        functionFrame.place(x=400, y=120)
        
        scrolledFrame = ScrolledFrame(functionFrame, height=155 - optionbuttonresize, width=365)
        scrolledFrame.pack(side="top", expand=0, fill="both")
        
        scrolledFrame.bind_arrow_keys(functionFrame)
        scrolledFrame.bind_scroll_wheel(functionFrame)
        inner_frame = scrolledFrame.display_widget(tk.Frame)
        
        functionTitleLabel = tk.Label(inner_frame,text=functiontitle, font="Arial 12 bold")
        
        row = 0
        functionTitleLabel.grid(row=row, column=0, sticky='W',padx=10, columnspan = 2)
        row += 1
        
        for entrylabel in display_list:
            var = tk.StringVar()
            lb = tk.Label(inner_frame, text=entrylabel, justify = "left")
            lb.grid(row=row, column=0, sticky='W',padx=10)
            en = tk.Entry(inner_frame, textvariable=var, justify = "left")
            en.grid(row=row, column=1, sticky='W',padx=10)
            self.display_dict[entrylabel] = var
            row += 1
        
        for entrylabel in ini_info.userinput:
            var = tk.StringVar()
            lb = tk.Label(inner_frame, justify = "left", text=ini_info.userinput[entrylabel])
            lb.grid(row=row, column=0, sticky='W',padx=10)
        
            en = tk.Entry(inner_frame, justify = "left", text=entrylabel, textvariable=var)
            en.grid(row=row, column=1, sticky='W',padx=10)
            ini_info.userinput[entrylabel] = var
            row += 1
        
        row += 1
        lb = tk.Label(inner_frame, justify = "left", text="")
        lb.grid(row=row, column=0, sticky='W',padx=10)
        row += 1
        lb2 = tk.Label(inner_frame, justify = "left", text="")
        lb2.grid(row=row, column=0, sticky='W',padx=10)
        
        if(len(ini_info.options) > 0):
            optionsButton = tk.Button(window, text="Options", width=20, font="Arial 10 bold", command=lambda: GuiManager.optionsDialog(window, ini_info)).place(x=595, y=290,anchor=tk.CENTER)
        
        taskFrame = tk.Frame(window, height=85, width=390, relief=tk.RAISED, borderwidth=3)
        taskFrame.place(x=400, y=305)
        
        section.set("SECTION:")
        taskitem.set("INSTALL TASK:")
        tk.Label(taskFrame,textvariable=taskitem, wraplength = 350, justify="left").place(x=10, y=17, anchor="w")
        
        InstallButton = tk.Button(taskFrame,text=ini_info.buttontext, width=10, font="Arial 10 bold", command=lambda: installfunc(ini_info, InstallButton, window, bar, section, taskitem))
        InstallButton.place(relx=.5, y=60, anchor=tk.CENTER)