# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#librairies

import pigpio
import time

#initialisation de la librairie pigpio
pi = pigpio.pi()             # exit script if no connection
if not pi.connected:
    exit()

def initialisation () :
    #for pwm...
    pi.set_mode(13, pigpio.OUTPUT)#PWM1
    pi.set_mode(19, pigpio.OUTPUT)#PWM2
    #for direction
    pi.set_mode(21, pigpio.OUTPUT)#Direction PWM1
    pi.set_mode(20, pigpio.INPUT)#Direction PWM1
    pi.set_mode(5, pigpio.OUTPUT)#Direction PWM2
    pi.set_mode(6, pigpio.OUTPUT)#Direction PWM2
    
def avancer_sens_direct ():
    pi.write(21,1)#Bon sens
    pi.write(20,0)
    
    pi.write(5,1)
    pi.write(6,0)
        
    pi.set_PWM_dutycycle(13,  128) # PWM 1/2 on
    pi.set_PWM_dutycycle(19,  128) # PWM 1/2 on
    

initialisation()
while 1 :    
    avancer_sens_direct()
    
