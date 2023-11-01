import tkinter
import constants as c

from US_Screen.US_Screen_Share import US_SCREEN
from UR_Robot.UR_ROBOT import UR_10E



class GUI_APP(tkinter.Tk, US_SCREEN):
    """Class that manages the Frame in general
    ....
    Constants
    -----------
    WINDOW_RESOLUTION: str
        Application window resolution, used "1800 x950" as default
    WINDOW_FRAME: class
        Put the Frame in a tuple

    """

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        # US_SCREEN.__init__(self)
        # US_IMAGE.__init__(self)

        container = tkinter.Frame(self)
        container.grid()
        self.geometry(c.WINDOW_RESOLUTION)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in c.WINDOWS_FRAME:
            page_name = F.__name__
            frame = F(container, self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Overview")  # c.WINDOWS_FRAME[0] should be Overview

        self.my_menu = tkinter.Menu(self)
        self.config(menu=self.my_menu)

        # ----------Adding  a MenuBar to navigate between pages------
        Main = tkinter.Menu(self.my_menu)
        Image_Settings = tkinter.Menu(self.my_menu)
        self.my_menu.add_cascade(label="Overview", menu=Main)
        self.my_menu.add_cascade(label="Image_Setup", menu=Image_Settings)

        Main.add_command(label="Overview", command=lambda: self.show_frame("Overview"))
        Image_Settings.add_command(label="Parameters")
        """#TODO add in a separate window when clicked, currently Image_Settings not in used..."""

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # def open_seconday_window(self):
    #     secondary_window = NewWindow()
    # secondary_window.title("Secondary Window")
    # secondary_window.config(width=300, height=200)
    # Create a button to close (destroy) this window.
    """TODO add in a separate window when clicked, currently Image_Settings not in used..."""


app = GUI_APP()
app.mainloop()
