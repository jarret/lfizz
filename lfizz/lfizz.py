#!/usr/bin/env python3
# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from twisted.application.service import Service
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import RPi.GPIO as GPIO

LED = 11


class LFizz(Service):
    def __init__(self):
        super().__init__()
        self.on = False
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(LED, GPIO.OUT)
        self.led_loop = LoopingCall(self.flip_led)
        self.led_loop.start(0.5, now=False)
        print("sadf")

    def flip_led(self):
        print("sdafdsasadf")
        if self.on:
            self.on = False
            GPIO.output(LED, GPIO.LOW)
            print("led off")
        else:
            self.on = True
            GPIO.output(LED, GPIO.HIGH)
            print("led on")

    def startService(self):
        super().startService()
        reactor.run()

    def stopService(self):
        super().stopService()
        reactor.stop()

#if __name__ == '__main__':
#    lf = LFizz()
#    reactor.run()
