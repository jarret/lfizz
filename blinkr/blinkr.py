#!/usr/bin/env python3

import time
import random
import json
import logging

from queue import Queue

import board
from neopixel import NeoPixel

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from txzmq import ZmqEndpoint, ZmqEndpointType
from txzmq import ZmqFactory
from txzmq import ZmqSubConnection

from ocd import Ocd
from ant import Ant
from rainbow import Rainbow
from flash import Flash
from quit import Quit
from implode import Implode


ZMQ_ENDPOINT = "tcp://127.0.0.1:7777"

ZMQ_TAG = "blinkr".encode("utf8")

N_PIXELS = 338
BRIGHTNESS = 0.3
DATA_PIN = board.D18

MODES = {"RAINBOW", "ANT", "OCD", "FLASH", "IMPLODE", "QUIT"}

###############################################################################

class Blinkr(object):
    def __init__(self):
        self.queue = Queue()

        self.zmq_factory = ZmqFactory()
        endpoint = ZmqEndpoint(ZmqEndpointType.connect, ZMQ_ENDPOINT)
        connection = ZmqSubConnection(self.zmq_factory, endpoint)
        connection.gotMessage = self.set_mode
        connection.subscribe(ZMQ_TAG)

    ###########################################################################

    def set_mode(self, message, tag):
        mode = message.decode("utf8")
        print("got: %s" % mode)
        if mode not in MODES:
            logging.error("bad mode: %s" % s)
            return
        self.queue.put(mode)
    ###########################################################################

    def thread_body(queue):
        pixels = NeoPixel(DATA_PIN, N_PIXELS, brightness=BRIGHTNESS,
                          auto_write=False)
        updates = {'RAINBOW': Rainbow(pixels),
                   'ANT':     Ant(pixels),
                   'OCD':     Ocd(pixels),
                   'FLASH':   Flash(pixels),
                   'IMPLODE': Implode(pixels),
                   'QUIT':    Quit(pixels)}
        assert set(updates.keys()) == MODES
        mode = "OCD"
        while True:
            try:
                new_mode = queue.get_nowait()
                assert new_mode in MODES, "unknown mode %s" % mode
                if new_mode != mode:
                    updates[new_mode].setup()
                mode = new_mode
            except:
                pass
            sleep = updates[mode].exec_update()
            if mode == "QUIT":
                break
            time.sleep(sleep)

    def start_thread(self):
        reactor.callInThread(Blinkr.thread_body, self.queue)

    def start(self):
        reactor.callLater(0.1, self.start_thread)

    def stop(self):
        self.queue.put("QUIT")


if __name__ == "__main__":
    b = Blinkr()
    b.start()
    reactor.addSystemEventTrigger("before", "shutdown", b.stop)
    reactor.run()
