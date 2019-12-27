#!/usr/bin/env python3
import sys
import time

from twisted.internet import reactor

from txzmq import ZmqEndpoint, ZmqEndpointType
from txzmq import ZmqFactory
from txzmq import ZmqSubConnection, ZmqPubConnection


PUBLISH_ENDPOINT = "tcp://127.0.0.1:7777"

TAG = "blinkr".encode("utf8")

MODES = {"OCD", "ANT", "RAINBOW"}

class Leds:
    def __init__(self):
        factory = ZmqFactory()
        pub_endpoint = ZmqEndpoint(ZmqEndpointType.bind, PUBLISH_ENDPOINT)
        self.pub_connection = ZmqPubConnection(factory, pub_endpoint)

    def set_mode(self, mode):
        assert mode in MODES, "unknown mode"
        msg = mode.encode("utf8")
        self.pub_connection.publish(msg, tag=TAG)
