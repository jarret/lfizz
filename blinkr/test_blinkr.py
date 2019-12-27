#!/usr/bin/env python3
import sys
import time

from twisted.internet import reactor

from txzmq import ZmqEndpoint, ZmqEndpointType
from txzmq import ZmqFactory
from txzmq import ZmqSubConnection, ZmqPubConnection


PUBLISH_ENDPOINT = "tcp://127.0.0.1:7777"

TAG = "blinkr".encode("utf8")

factory = ZmqFactory()

pub_endpoint = ZmqEndpoint(ZmqEndpointType.bind, PUBLISH_ENDPOINT)
pub_connection = ZmqPubConnection(factory, pub_endpoint)


def publish(mode):
    print("publishing: %s" % mode)
    msg = mode.encode("utf8")
    pub_connection.publish(msg, tag=TAG)
    time.sleep(0.01)
    reactor.stop()

reactor.callLater(1.0, publish, sys.argv[1])
reactor.run()



