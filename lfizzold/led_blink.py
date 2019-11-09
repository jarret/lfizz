# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from twisted.internet.task import LoopingCall

import RPi.GPIO as GPIO

LED = 11

class LedBlink(object):
    def __init__(self):
        self.on = False
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(LED, GPIO.OUT)
        self.led_loop = LoopingCall(self.flip_led)

    def flip_led(self):
        if self.on:
            self.on = False
            GPIO.output(LED, GPIO.LOW)
        else:
            self.on = True
            GPIO.output(LED, GPIO.HIGH)

    def run(self):
        self.led_loop.start(0.5, now=False)

    def stop(self):
        self.led_loop.stop()
