# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time

from twisted.internet import reactor

class MockElectrical(object):
    def __init__(self, reactor):
        self.actor = None

    def set_actor(self, actor):
        self.actor = actor

    def trigger_coin_mech(self):
        print("\n------coin mech trigger--------\n")
        print("sleeping")
        time.sleep(2)
        print("\n------coin mech release--------\n")

    def falling(self, button_no):
        print("electrical falling %s" % button_no)

    def rising(self, button_no):
        print("electrical rising %s" % button_no)

