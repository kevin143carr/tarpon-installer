import sys
import platform
import tkinter as tk
from tkinter import scrolledtext
if sys.version_info[:3] < (3, 9):
    try:
        from ttkbootstrap import ttk
    except ImportError:
        import ttkbootstrap as ttk
else:
    import ttkbootstrap as ttk
from tkinter import font    
from tkscrolledframe import ScrolledFrame
from PIL import Image as Image, ImageTk as Itk
import logging
from iniinfo import iniInfo
from tarpl.tarplapi import TarpL
from tarpl.tarplapi import TarpLreturn
from tarpl.tarplclasses import TarpLAPIEnum

logger = None


class GuiManager:
    def __init__(self) -> None:
        self.bar = None
        self.taskitem = None
        self.section = None
        self.startinfo = None
        self.themename = "superhero"
        self._tarpL = TarpL()
        self.canvas = None
        self.entry_boxes = 0
    
    def on_checkbox_toggle(self, changed_key, otheroption, ini_info):
        print("{}, {}".format(changed_key, otheroption))
        if ini_info.optionvals[changed_key].get() == '1':
            ini_info.optionvals[otheroption].set('1')        
        
        # Example rule: if "OptionA" is checked, check "OptionB"
        # You can add more logic here if needed    
    
    def optionsDialog(self, parent: tk.Tk, ini_info: iniInfo) -> None:
        # Pop up the options chooser and center it over the parent window.
        optionsWindow = tk.Toplevel(parent)
        optionsWindow.resizable(False, False)
        optionsWindow.focusmodel(model="active")
        optionsWindow.after(100, lambda: optionsWindow.focus_force())
        optionsWindow.title("Installation Options")
    
        # Main content frame
        content_frame = ttk.Frame(optionsWindow, padding=(18, 16, 18, 12))
        content_frame.pack(side="top", fill="both", expand=True)

        heading = ttk.Label(content_frame, text="Installation Options", font=("Arial", 14, "bold"))
        heading.pack(anchor="w")

        subtitle = ttk.Label(
            content_frame,
            text="Choose any optional actions for this run.",
            justify="left",
        )
        subtitle.pack(anchor="w", pady=(2, 12))
    
        # Scrolling content area
        functionFrame = ttk.Frame(content_frame)
        functionFrame.pack(side="top", fill="both", expand=True)
    
        scrolledFrame = ScrolledFrame(functionFrame, scrollbars="vertical")
        scrolledFrame.pack(fill=tk.BOTH, expand=True)
    
        scrolledFrame.bind_arrow_keys(functionFrame)
        scrolledFrame.bind_scroll_wheel(functionFrame)
        inner_frame = scrolledFrame.display_widget(ttk.Frame)
    
        # Build the option list with optional Tarpl behaviors.
        for row, value in enumerate(ini_info.options):
            if value not in ini_info.optionvals:
                ini_info.optionvals[value] = tk.StringVar(value='0')
    
            isTarpL = self._tarpL.CheckForTarpL(ini_info.options[value])
            if isTarpL and 'ALSOCHECKOPTION' in ini_info.options[value]:
                optionparams = ini_info.options[value].split('::')
                label_text = optionparams[2]
                other_option_key = optionparams[1]
                                
                if other_option_key not in ini_info.optionvals:
                    ini_info.optionvals[other_option_key] = tk.StringVar(value='0')
    
                lb = ttk.Label(inner_frame, text=label_text)
                cb = ttk.Checkbutton(
                    inner_frame,
                    variable=ini_info.optionvals[value],
                    onvalue='1',
                    offvalue='0',
                    command=lambda actionstr=ini_info.options[value],
                                   val=value,
                                   other=other_option_key: self._tarpL.ExecuteTarpL(
                        actionstr, ini_info, optionone=val, optiontwo=other
                    )
                )
            else:
                lb = ttk.Label(inner_frame, text=ini_info.options[value], justify="left", wraplength=300)
                cb = ttk.Checkbutton(
                    inner_frame,
                    variable=ini_info.optionvals[value],
                    onvalue='1',
                    offvalue='0'
                )
    
            cb.grid(row=row, column=0, sticky="nw", padx=(0, 8), pady=6)
            lb.grid(row=row, column=1, sticky="w", pady=6)
    
        # Bottom frame for the close button, centered
        bottom_frame = ttk.Frame(optionsWindow)
        bottom_frame.pack(side="bottom", fill="x", pady=(0, 14))
    
        optionbutton = ttk.Button(bottom_frame, text="Close", width=20, command=optionsWindow.destroy)
        optionbutton.pack(anchor="center")
    
        # Allow the window to size itself based on content
        optionsWindow.update_idletasks()
    
        # Center the window on screen
        window_width = optionsWindow.winfo_width()
        window_height = optionsWindow.winfo_height()
        screen_width = optionsWindow.winfo_screenwidth()
        screen_height = optionsWindow.winfo_screenheight()
    
        x = max(0, min(parent.winfo_x() + parent.winfo_width() // 2 - window_width // 2,
                       screen_width - window_width))
        y = max(0, min(parent.winfo_y() + parent.winfo_height() // 2 - window_height // 2,
                       screen_height - window_height))
    
        optionsWindow.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def showFinalErrorsDialog(self, parent: tk.Tk, errors) -> None:
        error_window = tk.Toplevel(parent)
        error_window.title("Installation Errors")
        error_window.resizable(True, True)
        error_window.transient(parent)
        error_window.grab_set()

        content_frame = ttk.Frame(error_window, padding=(18, 16, 18, 12))
        content_frame.pack(fill=tk.BOTH, expand=True)

        heading = ttk.Label(content_frame, text="Installation Errors", font=("Arial", 14, "bold"))
        heading.pack(anchor="w")

        subtitle = ttk.Label(
            content_frame,
            text="The following errors were recorded during this install.",
            justify="left",
            wraplength=520,
        )
        subtitle.pack(anchor="w", pady=(2, 10))

        error_text = scrolledtext.ScrolledText(content_frame, width=72, height=12, wrap=tk.WORD)
        error_text.pack(fill=tk.BOTH, expand=True)
        error_text.insert("1.0", "\n\n".join(errors))
        error_text.configure(state=tk.DISABLED)

        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(12, 0))

        close_button = ttk.Button(button_frame, text="Close", width=18, command=error_window.destroy)
        close_button.pack(anchor="e")

        error_window.update_idletasks()
        error_window.minsize(error_window.winfo_width(), error_window.winfo_height())
        error_window.wait_window()

    def showDiagnosticsDialog(self, parent: tk.Tk, diagnostics) -> None:
        diagnostic_window = tk.Toplevel(parent)
        diagnostic_window.title("Diagnostics")
        diagnostic_window.resizable(True, True)
        diagnostic_window.transient(parent)
        diagnostic_window.grab_set()

        content_frame = ttk.Frame(diagnostic_window, padding=(18, 16, 18, 12))
        content_frame.pack(fill=tk.BOTH, expand=True)

        heading = ttk.Label(content_frame, text="Diagnostics", font=("Arial", 14, "bold"))
        heading.pack(anchor="w")

        subtitle = ttk.Label(
            content_frame,
            text="Post-install diagnostics results.",
            justify="left",
            wraplength=520,
        )
        subtitle.pack(anchor="w", pady=(2, 10))

        results_frame = ttk.Frame(content_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        results_frame.columnconfigure(1, weight=1)

        for row, result in enumerate(diagnostics):
            color = "#2e7d32" if result["status"] == "PASS" else "#c62828"
            icon_canvas = tk.Canvas(results_frame, width=16, height=16, highlightthickness=0)
            icon_canvas.grid(row=row, column=0, sticky="nw", padx=(0, 10), pady=4)
            icon_canvas.create_oval(2, 2, 14, 14, fill=color, outline=color)

            label = ttk.Label(results_frame, text=result["label"], justify="left", wraplength=360)
            label.grid(row=row, column=1, sticky="w", pady=4)

            status_label = ttk.Label(results_frame, text="[{}]".format(result["status"]), foreground=color)
            status_label.grid(row=row, column=2, sticky="e", padx=(12, 0), pady=4)

        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(12, 0))

        close_button = ttk.Button(button_frame, text="Close", width=18, command=diagnostic_window.destroy)
        close_button.pack(anchor="e")

        diagnostic_window.update_idletasks()
        diagnostic_window.minsize(diagnostic_window.winfo_width(), diagnostic_window.winfo_height())
        diagnostic_window.wait_window()
        
    def buildLeftFrame(self, window, functiontitle, ini_info: iniInfo, installfunc):
        # Left side: visible branding plus progress and current task status.
        self.taskitem = tk.StringVar()
        if self.section is None:
            self.section = tk.StringVar(value="[STARTUP]")
        
        # Load image (GUI logo)
        image = Image.open(ini_info.logoimage)
        image = image.resize((270, 270))
        photo = Itk.PhotoImage(image)
        
        left_frame = ttk.Frame(window, padding=(18, 18, 12, 18))
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        image_frame = ttk.Frame(left_frame)
        image_frame.pack(fill=tk.X, pady=(0, 14))

        label = ttk.Label(image_frame, image=photo, anchor="center")
        label.image = photo
        label.pack(anchor="center")

        spacer = ttk.Frame(left_frame)
        spacer.pack(fill=tk.BOTH, expand=True)
        
        progress_frame = ttk.Labelframe(left_frame, text="Progress", padding=(12, 10, 12, 12))
        progress_frame.pack(side=tk.BOTTOM, fill=tk.X)
        progress_frame.columnconfigure(0, weight=1)

        section_row = ttk.Frame(progress_frame)
        section_row.grid(row=0, column=0, sticky="ew")
        section_row.columnconfigure(1, weight=1)

        section_heading = ttk.Label(section_row, text="Current Section", font=("Arial", 10, "bold"))
        section_heading.grid(row=0, column=0, sticky="w")

        section_label = ttk.Label(
            section_row,
            textvariable=self.section,
            wraplength=180,
            anchor="w",
            justify="left",
        )
        section_label.grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=290, mode="determinate")
        self.bar.grid(row=1, column=0, sticky="ew", pady=(4, 10))

        task_heading = ttk.Label(progress_frame, text="Current Task", font=("Arial", 10, "bold"))
        task_heading.grid(row=2, column=0, sticky="w")

        status_label = ttk.Label(
            progress_frame,
            wraplength=290,
            textvariable=self.taskitem,
            anchor="w",
            justify="left",
        )
        status_label.grid(row=3, column=0, sticky="ew", pady=(2, 0))

        self.taskitem.set("Waiting to begin installation.")

        install_button = ttk.Button(
            progress_frame,
            text=ini_info.buttontext,
            command=lambda: installfunc(ini_info, install_button, window),
        )
        install_button.grid(row=4, column=0, sticky="ew", pady=(12, 0))
           
    def on_focus_in(self, event, entry: str)->None:
        # Auto-scroll to keep the focused entry visible.
        if not self.canvas or self.entry_boxes == 0:
            return
        movetoval = int(entry) / self.entry_boxes
        self.canvas.yview_moveto(movetoval)
        
    def buildRightFrame(self, window, functiontitle, ini_info: iniInfo, installfunc)->None:
        # Right side: title, startup summary, options trigger, and dynamic input form.
        isosx = platform.system() == "Darwin"
        
        right_frame = ttk.Frame(window, padding=(12, 18, 18, 18))
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(right_frame)
        header_frame.pack(fill=tk.X, anchor="n")

        title_label = ttk.Label(
            header_frame,
            text=ini_info.installtitle,
            anchor="w",
            justify="left",
            font=("Arial", 16, "bold"),
            wraplength=360,
        )
        title_label.pack(anchor="w")

        if ini_info.startinfo:
            self.startinfo = ttk.Label(
                header_frame,
                text=ini_info.startinfo,
                anchor="w",
                justify="left",
                wraplength=360,
            )
            self.startinfo.pack(anchor="w", pady=(6, 12))

        controls_frame = ttk.Frame(right_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        functionTitleLabel = ttk.Label(
            controls_frame,
            text=functiontitle,
            anchor="w",
            justify="left",
            font=("Arial", 12, "bold"),
            wraplength=260,
        )
        functionTitleLabel.pack(side=tk.LEFT, fill=tk.X, expand=True)

        options_button = ttk.Button(
            controls_frame,
            text="Options",
            width=16,
            command=lambda: self.optionsDialog(window, ini_info),
        )
        options_button.pack(side=tk.RIGHT, padx=(12, 0))

        input_frame = ttk.Labelframe(right_frame, text="Required Inputs", padding=(12, 10, 12, 12))
        input_frame.pack(fill=tk.BOTH, expand=True)

        scrolledFrame = ScrolledFrame(input_frame, scrollbars = "vertical")
        scrolledFrame.pack(fill=tk.BOTH, expand = "yes")

        inner_frame = scrolledFrame.display_widget(ttk.Frame)
        scrolledFrame.bind_arrow_keys(inner_frame)
        scrolledFrame.bind_scroll_wheel(inner_frame)
       
        window.update()     
        self.canvas = scrolledFrame._canvas
        self.canvas.update_idletasks()
        widthofframe = self.canvas.winfo_width()
        entryboxlen = self.calculateEntryBoxWidth(window, ini_info.userinput, widthofframe)        

        # Add labels + entry boxes for each USERINPUT key.
        userinputkeys = list(ini_info.userinput.keys())
        for i in range(len(ini_info.userinput)):
            var = tk.StringVar()
            keyvalue = userinputkeys[i]
            label = ttk.Label(inner_frame, text=ini_info.userinput[keyvalue], justify="left", wraplength=180)
            label.grid(row=i, column=0, pady=6, padx=(0, 10), sticky="w")
            if isosx:
                entry = ttk.Entry(inner_frame, justify="left", textvariable=var)
            else:
                entry = ttk.Entry(inner_frame, justify="left", textvariable=var, width=entryboxlen)
            entry.grid(row=i, column=1, pady=6, sticky="ew")

            # Prefill defaults if provided in the INI (prompt || default).
            if keyvalue in getattr(ini_info, "userinput_defaults", {}):
                var.set(ini_info.userinput_defaults[keyvalue])
            
            # Bind the focus in event to the on_focus_in function for each entry box
            entry.bind("<FocusIn>", lambda event, entry="{}".format(i): self.on_focus_in(event, entry))
            ini_info.userinput[keyvalue] = var                      

        inner_frame.columnconfigure(1, weight=1)
        
        self.entry_boxes = len(ini_info.userinput)

        if (len(ini_info.options) == 0):
            options_button.config(state=tk.DISABLED)
            
    def calculateEntryBoxWidth(self, window, userinput: dict, widthofframe: int) -> int:
        # Size entries to fit the widest label within the frame width.
            
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
        # Main GUI window sizing and title setup.
        global logger
        logger = logging.getLogger("logger")
        geometrystr: str = ""
        self.themename = ini_info.themename
        
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        width = 920
        height = 510
        x = int((screen_width/2) - (width/2))
        y = int((screen_height/2) - (height/1.5))
        
        geometrystr = f"{width}x{height}+{x}+{y}"
                    
        window.geometry(geometrystr)
        window.title(ini_info.installtitle)
        window.resizable(False,False)
        window.focusmodel(model="passive")
        self.buildLeftFrame(window, functiontitle, ini_info, installfunc)
        self.buildRightFrame(window, functiontitle, ini_info, installfunc)
