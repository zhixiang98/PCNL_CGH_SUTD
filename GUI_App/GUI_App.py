import tkinter
import constants as c
from PCNL_CGH_SUTD.US_Screen.US_Screen_Share import US_Screen
print("HI")

class GUI_App(tkinter.Tk, US_Screen):
    # Manages the App window in general

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        US_Screen.__init(self)
        container = tkinter.Frame(self)
        container.grid()
        self.geometry(c.WINDOW_RESOLUTION)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight= 1)

        self.frames = {}

        for F in c.WINDOWS_FRAME:
            page_name = F.__name__
            frame = F(container, self)
            self.frames[page_name] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame(c.WINDOWS_FRAME[0])


        #----------Adding  a MenuBar to navigate between pages------
        for F in c.MENUS_NAME:
            menu_name = F.__name__
            self.mymenu = tkinter.Menu(self)
            self.config(menu = self.mymenu)
            menu_name = Menu(self.mymenu)
            self.mymenu.add_cascade(label = menu_name, )

        Main= tkinter.Menu(self.)