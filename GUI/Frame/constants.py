REFRESH_DELAY = 20  # Delay for tkinter update cycle. in terms of milliseconds
# --- GENERAL_ATTRIBUTES ---
PADX =5
PADY =5
BUTTON_WIDTH = 15

# --- IMAGE DIMENSIONS --------
IMAGE_HEIGHT = 740
IMAGE_WIDTH =  1432

# --- LABEL_FRAME ATTRIBUTES---
ROBOT_IP_FRAME_TEXT = "Robot Connection"

# ---CANVAS ATTRIBUTES---
CANVAS_BG = 'WHITE'
# CANVAS_HEIGHT = 740
# CANVAS_WIDTH = 1432
CANVAS_HEIGHT = 950
CANVAS_WIDTH = 1950
CANVAS_BD = 0
CANVAS_HIGHLIGHT = 0
CANVAS_RELIEF = "ridge"

#---BUTTON ATTRIBUTES---
ORIGIN_BUTTON_TEXT = "Draw Origin"
SELECT_TARGET_BUTTON_TEXT = "Choose Target"
THETA_BUTTON_TEXT = "Calculate Theta"
DRAW_NEEDLE_BUTTON_TEXT = "Draw Needle Line"
CONVERT_PIXEL2COORDINATES_TEXT = "Convert px to Coord."

RECONNECT_IMAGE_TEXT = "Connect IGTL"
CONNECT_IGT_BUTTON_ROW = 3
CONNECT_IGT_BUTTON_COLUMN = 0


SUBMIT_OUTPUT_BUTTON_TEXT = "Submit"
POPULATE_BUTTON_TEXT = "Auto Field"



#--- ORGANISATION ---
    #Grid Layout
        # -- Image Settings Frame---
CANVAS_ROW = 0
CANVAS_COLUMN = 0

ORIGIN_BUTTON_ROW = 0
ORIGIN_BUTTON_COLUMN = 0

SELECT_TARGET_BUTTON_ROW = 0
SELECT_TARGET_BUTTON_COLUMN =1

THETA_BUTTON_ROW = 0
THETA_BUTTON_COLUMN = 1

DRAW_NEEDLE_BUTTON_ROW =0
DRAW_NEEDLE_BUTTON_COLUMN =2

CONVERT_PIXEL2COORDINATES_ROW =0
CONVERT_PIXEL2COORDINATES_COLUMN =4

DEPTH_COMBO_BOX_ROW = 0
DEPTH_COMBO_BOX_COLUMN = 3
        # -- Robot Output Frame
SUBMIT_OUTPUT_BUTTON_ROW = 3
SUBMIT_OUTPUT_BUTTON_COLUMN = 1

POPULATE_BUTTON_ROW = 3
POPULATE_BUTTON_COLUMN = 3

    #Robot Data Frame
ROBOT_DATA_FRAME_X = IMAGE_WIDTH
ROBOT_DATA_FRAME_Y = 0
ROBOT_DATA_FRAME_WIDTH = (CANVAS_WIDTH-ROBOT_DATA_FRAME_X)
ROBOT_DATA_FRAME_HEIGHT = 300

    #NEEDLE DRIVER FRAME
NEEDLE_DRIVER_FRAME_X = IMAGE_WIDTH
NEEDLE_DRIVER_FRAME_Y = ROBOT_DATA_FRAME_HEIGHT+ROBOT_DATA_FRAME_Y
NEEDLE_DRIVER_FRAME_WIDTH = (CANVAS_WIDTH-NEEDLE_DRIVER_FRAME_X)
NEEDLE_DRIVER_FRAME_HEIGHT = 250

    #ROBOT_TCP_FRAME
ROBOT_TCP_FRAME_X = 0
ROBOT_TCP_FRAME_Y = 50
ROBOT_TCP_FRAME_WIDTH = 525
ROBOT_TCP_FRAME_HEIGHT = 80

    #Coordinates Layout
IMAGE_SETTING_LBL_FRAME_X = 0
IMAGE_SETTING_LBL_FRAME_Y = IMAGE_HEIGHT
IMAGE_SETTING_LBL_FRAME_WIDTH = IMAGE_WIDTH/2
IMAGE_SETTING_LBL_FRAME_HEIGHT = CANVAS_HEIGHT-IMAGE_SETTING_LBL_FRAME_Y

    #Treeview Layout
TREEVIEW_FRAME_X = IMAGE_WIDTH
TREEVIEW_FRAME_Y = NEEDLE_DRIVER_FRAME_Y+NEEDLE_DRIVER_FRAME_HEIGHT
TREEVIEW_WIDTH = (CANVAS_WIDTH-TREEVIEW_FRAME_X) *0.75
TREEVIEW_HEIGHT = CANVAS_HEIGHT-NEEDLE_DRIVER_FRAME_Y-NEEDLE_DRIVER_FRAME_HEIGHT

    #US information
US_INFO_FRAME_X = TREEVIEW_FRAME_X+TREEVIEW_WIDTH
US_INFO_FRAME_Y = NEEDLE_DRIVER_FRAME_Y+NEEDLE_DRIVER_FRAME_HEIGHT
US_INFO_FRAME_WIDTH = (CANVAS_WIDTH-TREEVIEW_FRAME_X)*0.25
US_INFO_FRAME_HEIGHT = CANVAS_HEIGHT-NEEDLE_DRIVER_FRAME_Y-NEEDLE_DRIVER_FRAME_HEIGHT



ROBOT_IP_FRAME_X = 0
ROBOT_IP_FRAME_Y = 10
ROBOT_IP_FRAME_WIDTH = 525
ROBOT_IP_FRAME_HEIGHT = 40
