import sys
import math

density_water=997.0 #kg/m^3
density_air=1.225 #kg/m^3
density_cylinder= 1000.0 #kg/m^3 -> ABS PLASTIC
g=9.81 #m/s^2

radius_inner=1.5 #in
thickness=.125 #in
height_cylinder=6.0 #in
height_waterline=.95 # %OF HULL HEIGHT
load=1 #lbs

def outputShipDimensions():
    print("HULL H: "+str(height_cylinder)+" in")
    print("RADIUS (i): "+str(radius_inner)+" in")
    print("THICKNESS: "+str(thickness)+" in")
    print("WL: "+str(height_waterline)+" in")
    print("LOAD: "+str(load)+" lb")

def hollow_cylinder():
    #Conversions of in->m
    t=thickness*2.54/100.0
    r=radius_inner*2.54/100.0
    h=height_cylinder*2.54/100.0
    h_w=height_cylinder*height_waterline*2.54/100.0
    l=load*4.45

    weight_cylinder=density_cylinder*g*(2*math.pi*t*(r+t)**2+math.pi*h*(2*r*t+t**2))+l
    print("    HULL WEIGHT: "+str(weight_cylinder/4.45)+" lb")

    weight_disp=math.pi*(r+t)**2*h_w*density_water*g
    print("    DISPLACEMENT: "+str(weight_disp/4.45)+" lb")

    weight_ballast=weight_disp-weight_cylinder
    print("    BALLAST WEIGHT: "+str(weight_ballast/4.45)+" lb")

    h_b=weight_ballast/(g*density_water*math.pi*(r**2+2*r*t+t**2))
    print("    HEIGHT BALLAST: "+str(h_b*39.37)+" in")

outputShipDimensions()
print("---------------------")
hollow_cylinder()