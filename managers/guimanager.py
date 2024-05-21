import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image as Image, ImageTk as Itk
from tkscrolledframe import ScrolledFrame
import logging

logger = None

class GuiManager:
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

        functionFrame = tk.Frame(optionsWindow, height=240, width=340)
        functionFrame.pack(side="top", expand=0, fill="both")

        scrolledFrame = ScrolledFrame(functionFrame, height=240, width=360)
        scrolledFrame.pack(side="top", expand=0, fill="both")

        scrolledFrame.bind_arrow_keys(functionFrame)
        scrolledFrame.bind_scroll_wheel(functionFrame)
        inner_frame = scrolledFrame.display_widget(tk.Frame)

        for row in range(len(ini_info.options)):
            vals = ini_info.options.keys()
            value = list(vals)[row]

            ini_info.optionvals[value]=tk.StringVar(value='0')

            lb = tk.Label(inner_frame, justify = "left", text=ini_info.options[value])
            cb = tk.Checkbutton(inner_frame, justify = "left", variable=ini_info.optionvals[value], onvalue='1', offvalue='0')
            lb.grid(row=row,
                    column=1, stick="W")
            cb.grid(row=row,
                    column=0, stick="W")

        optionsButton = tk.Button(optionsWindow, text="Close", width=20, font="Arial 10 bold", command=optionsWindow.destroy).place(relx=.5, y=280,anchor=tk.CENTER)


    def buildGUI(self, window, functiontitle, ini_info, installfunc):
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