#!/usr/bin/env python3
# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from twisted.application.service import Service
from twisted.internet import reactor

#from led_blink import LedBlink
from app_state import AppState
from cad_price import CadPrice

class LFizz(Service):
    def __init__(self):
        super().__init__()
#        self.led_blink = LedBlink()
        self.app_state = AppState()
        self.cad_price = CadPrice(reactor, self.app_state)

    ###########################################################################

    def run_lfizz(self):
#        self.led_blink.run()
        self.cad_price.run()
        reactor.run()

    def stop_lfizz(self):
#        self.led_blink.stop()
        self.cad_price.stop()
        reactor.stop()

    ###########################################################################

    def startService(self):
        super().startService()
        self.run_lfizz()

    def stopService(self):
        super().stopService()
        self.stop_lfizz()
        reactor.stop()


###############################################################################

if __name__ == '__main__':
    lf = LFizz()
    lf.run_lfizz()
