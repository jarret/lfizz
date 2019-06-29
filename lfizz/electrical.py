# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time

from twisted.internet import reactor
import RPi.GPIO as GPIO
from print import print_green, print_light_blue

COIN_MECH_RELAY = 7
INSERT_CHANGE_LIGHT = 8


class Electrical(object):
    def __init__(self, reactor):
        self.actor = None

        #GPIO.setmode(GPIO.BOARD)
        GPIO.setup(COIN_MECH_RELAY, GPIO.OUT)

        GPIO.setup(INSERT_CHANGE_LIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(INSERT_CHANGE_LIGHT, GPIO.BOTH,
                              callback=self._both_cb, bouncetime=1000)

    def set_actor(self, actor):
        self.actor = actor

    def trigger_coin_mech(self):
        GPIO.output(COIN_MECH_RELAY, GPIO.LOW)
        #print("sleeping")
        time.sleep(2)
        GPIO.output(COIN_MECH_RELAY, GPIO.HIGH)

    def _both_cb(self, button_no):
        time.sleep(0.3)
        r = GPIO.input(button_no)
        if r:
            reactor.callFromThread(self.falling, button_no)
        else:
            reactor.callFromThread(self.rising, button_no)

    def falling(self, button_no):
        print_green("electrical falling %s" % button_no)

    def rising(self, button_no):
        print_green("electrical rising %s" % button_no)
        self.actor.get_new_invoice()
