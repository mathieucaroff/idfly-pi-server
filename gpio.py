#/usr/bin/python3
"""
Module de gestion des GPIO des moteurs du dirigeable.
"""

import os
import time
import subprocess
from abc import ABC, abstractmethod
from collections import namedtuple

import pigpio

from util import nop

def _addMotors(igpio):
    pi = igpio.pi
    igpio.forward = MotorPins(pi=pi, directionA=20, directionB=21, pwm=19)
    igpio.down    = MotorPins(pi=pi, directionA=6,  directionB=5,  pwm=13)
    igpio.frontT  = MotorPins(pi=pi, directionA=8,  directionB=7,  pwm=25)
    igpio.backT   = MotorPins(pi=pi, directionA=16, directionB=12, pwm=1)

class MotorPins():
    """Classe de contrôle d'un moteur via deux pins de direction et une PWM."""
    def __init__(self, pi, directionA, directionB, pwm):
        self._pi = pi
        self._directionA = directionA
        self._directionB = directionB
        self._pwm = pwm

        # Mode des GPIO (pins)
        pi.set_mode(directionA, pigpio.OUTPUT) # Direction
        pi.set_mode(directionB, pigpio.OUTPUT) # Direction
        pi.set_mode(pwm, pigpio.OUTPUT) # PWM

        # Initialisation des sorties
        self(value=0)
    
    def __call__(self, value):
        if value >= 0:
            a, b = 0, 1
        else:
            a, b = 1, 0
            value *= -1
        self._pi.write(self._directionA, a)
        self._pi.write(self._directionB, b)
        self._pi.set_PWM_dutycycle(self._pwm, 255 * value / 100)


class BaseIdflyGPIO(ABC):
    pass


class DummyIdflyGPIO(BaseIdflyGPIO):
    forward, down, frontT, backT = [nop] * 4


class IdflyGPIO(BaseIdflyGPIO):
    """
    Classe de contrôle des moteurs du dirigeable IDFLY, via les PWM.
    
    Usage:
        idfly = IdflyGPIO()
        idfly.forward(100)
        idfly.down(-24)
        time.sleep(1)
        idfly.forward(0)
        idfly.down(0)
    """

    def __init__(self):
        runningAsRoot = os.geteuid() == 0
        if runningAsRoot:
            try:
                subprocess.check_call("pgrep pigpiod || (pigpiod && sleep 0.4)", shell=True)
            except subprocess.CalledProcessError:
                print("Cannot start server pigpiod")
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Could not connect the gpio(s). [`pigpio.pi().connected`: `{}`]".format(pi.connected))
        _addMotors(self)
