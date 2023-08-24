import tkinter
import constants as c
from PCNL_CGH_SUTD.UR_Robot import UR_ROBOT


class Overview(tkinter.Frame, UR_ROBOT):

    def __init__(self, parent, cont):
        tkinter.Frame.__init__(self, parent)
        self.cont = cont
        self.delay = c.REFRESH_DELAY

        self.origin_pixel_x, self.origin_pixel_y = 0,0
