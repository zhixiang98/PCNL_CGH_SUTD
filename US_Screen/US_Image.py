class US_IMAGE():
    def __init__(self):
        #---Pixel Coordinates---
        self.Origin_Pixel_X , self.Origin_Pixel_Y = 0,0
        self.Target_Pixel_X, self.Target_Pixel_Y = 0,0
        self.Surface_Pixel_X, self.Surface_Pixel_Y =0,0

        self.Needle_Start_Pixel_X, self.Needle_Start_Pixel_Y = 0,0
        self.Needle_End_Pixel_X, self.Needle_End_Pixel_Y = 0, 0

        self.Projected_Needle_Start_Pixel_X, self.Projected_Needle_Start_Pixel_Y = 0, 0
        self.Projected_Needle_End_Pixel_X, self.Projected_Needle_End_Pixel_Y = 0, 0

        #---Ultrasound Coordinates---
        self.Origin_US_X, self.Origin_US_Y = 0, 0
        self.Needle_Start_US_X, self.Needle_Start_US_Y = 0, 0
        self.Needle_End_US_X, self.Needle_End_US_Y = 0, 0
        self.Surface_US_X, self.Surface_US_Y = 0, 0

        #--- Important values---
        self.Theta = 0
        self.Alpha = 0
        self.x_distance = 0 #x_distance is from the fixed point of actuator to needle
        self.d_distance = 0 #d_distance is the horizontal distance from the probe to the needle

