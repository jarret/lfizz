# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time

import RPi.GPIO as GPIO

from twisted.internet import threads
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from print import print_green, print_light_blue

COIN_MECH_RELAY = 7
INSERT_CHANGE_LIGHT = 8


class Electrical(object):

    def __init__(self, reactor, machine):
        self.reactor = reactor
        self.machine = machine
        self.insert_change_inputs = [0, 0]
        self.insert_change_state = 0

        #GPIO.add_event_detect(INSERT_CHANGE_LIGHT, GPIO.RISING,
        #                      callback=self.rising, bouncetime=500)
        #GPIO.add_event_detect(INSERT_CHANGE_LIGHT, GPIO.FALLING,
        #                      callback=self.falling)

        self.machine.set_electrical(self)
        _ = threads.deferToThread(Electrical.set_high)

        lc = LoopingCall(self.check_input)
        lc.start(1.0)

    def setup_gpio():
        if GPIO.getmode() != GPIO.BOARD:
            GPIO.setmode(GPIO.BOARD)
        GPIO.setup(COIN_MECH_RELAY, GPIO.OUT)
        GPIO.setup(INSERT_CHANGE_LIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def flip_delay_flip():
        GPIO.output(COIN_MECH_RELAY, GPIO.LOW)
        print("sleeping")
        time.sleep(2)
        GPIO.output(COIN_MECH_RELAY, GPIO.HIGH)

    def set_high():
        GPIO.output(COIN_MECH_RELAY, GPIO.HIGH)

    def trigger_coin_mech(self):
        print_green("triggering coin mech")
        _ = threads.deferToThread(Electrical.flip_delay_flip)

    def check_input(self):
        r = GPIO.input(INSERT_CHANGE_LIGHT)
        #print("check: %s" % r)
        self.insert_change_inputs.pop(0)
        self.insert_change_inputs.append(r)
        assert len(self.insert_change_inputs) == 2
        last_input_sum = sum(self.insert_change_inputs)

        if last_input_sum == 2:
            if self.insert_change_state == 1:
                self.insert_change_state = 0;
                self.insert_change_turn_off()
        elif last_input_sum == 1:
            return
        elif last_input_sum == 0:
            if self.insert_change_state == 0:
                self.insert_change_state = 1;
                self.insert_change_turn_on()

    def insert_change_ambiguous(self):
        print("insert change ambiguous")

    def insert_change_turn_on(self):
        print("insert change on")
        self.machine.post_vend_finished()

    def insert_change_turn_off(self):
        print("insert change off")

    #def _both_cb(self, button_no):
    #    r = GPIO.input(button_no)
    #    if r:
    #        reactor.callFromThread(self.falling, button_no)
    #    else:
    #        reactor.callFromThread(self.rising, button_no)

    def falling(self, button_no):
        print_green("electrical falling %s" % button_no)

    def rising(self, button_no):
        print_green("electrical rising %s" % button_no)
        self.machine.post_vend_finished()
