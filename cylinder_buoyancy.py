import sys
import math
import numpy

density_water=997.0 #kg/m^3
density_air=1.225 #kg/m^3
density_cylinder= 1000.0 #kg/m^3 -> ABS PLASTIC
# density_cylinder= 8050.0 #kg/m^3 -> STEEL
g=9.81 #m/s^2

radius_outer=1.5 #in
thickness=.25 #in
height_cylinder=8 #in
height_waterline=.925 # % OF HULL HEIGHT
load=1.4 #lbs

def outputShipDimensions():
    print("HULL HEIGHT: "+str(height_cylinder)+" in")
    print("HULL OD: "+str(2*(radius_outer))+" in")
    print("HULL ID: "+str(2*(radius_outer-thickness))+" in")
    print("THICKNESS: "+str(thickness)+" in")
    print("WL: "+str(height_cylinder*height_waterline)+" in ABL")
    print("LOAD: "+str(load)+" lb")

def hollow_cylinder():
    #Conversions of in->m
    t=thickness*2.54/100.0
    r=(radius_outer-t)*2.54/100.0
    h=height_cylinder*2.54/100.0
    h_w=height_cylinder*height_waterline*2.54/100.0
    l=load*4.45

    volume_cylinder=math.pi*t*(r+t)**2+math.pi*(h-r-2*t)*(2*r*t+t**2)+4/6*math.pi*((r+t)**3-r**3)
    weight_cylinder=density_cylinder*g*volume_cylinder+l
    print("    HULL WEIGHT: "+str(weight_cylinder/4.45)+" lb")

    volume_hemisphere=4/6*math.pi**(r+t)**3
    weight_disp=(math.pi*(r+t)**2*(h_w-r-t)+volume_hemisphere)*density_water*g
    print("    DISPLACEMENT: "+str(weight_disp/4.45)+" lb")

    weight_ballast=weight_disp-weight_cylinder
    print("    BALLAST WEIGHT: "+str(weight_ballast/4.45)+" lb")

    weight_water_in_cylinder=weight_ballast-4.0/6.0*math.pi*r**3.0*g*density_water
    if weight_water_in_cylinder>0:
        h_b=weight_water_in_cylinder/(density_water*g*(math.pi*r**2))+r
        print("    HEIGHT BALLAST: "+str(h_b*39.37)+" in")
    else:
        # print("        REQ V:"+str(weight_ballast/(g*density_water)*61023.7)+" in^3")
        a=1
        b=-1*3*r
        c=0
        d=3/math.pi*weight_ballast/(g*density_water)
        count=0
        x=numpy.roots([a,b,c,d])
        for root in x:
            if root>0 and not isinstance(root, complex) and root<r: 
                count+=1
                h_b=root
                print("    HEIGHT BALLAST: "+str(h_b*39.37)+" in")
        
        if count==0:
            print("    HEIGHT BALLAST: undefined")


outputShipDimensions()
print("---------------------")
hollow_cylinder()