#!/usr/bin/env python3
# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import sys
import configparser
from twisted.application.service import Service
from twisted.internet import reactor

#from led_blink import LedBlink
from app_state import AppState
from fiat_price import FiatPrice
from network_ip import NetworkIp

class LFizz(Service):
    def __init__(self, config_file):
        super().__init__()
#        self.led_blink = LedBlink()
        if not os.path.exists(config_file):
            sys.exit("please add a config file at %s" % config_file)
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        if self.config['Strike']['ApiKey'] == 'sk_your_api_key':
            sys.exit("please set your Strike API key in %s" % config_file)
        print(self.config)
        self.app_state = AppState(self.config)
        self.fiat_price = FiatPrice(reactor, self.app_state)
        self.network_ip = NetworkIp(reactor, self.app_state)

    ###########################################################################

    def run_lfizz(self):
#        self.led_blink.run()
        self.fiat_price.run()
        self.network_ip.run()
        reactor.run()

    def stop_lfizz(self):
#        self.led_blink.stop()
        self.fiat_price.stop()
        self.network_ip.stop()
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
    lf = LFizz("/etc/lfizz.conf")
    lf.run_lfizz()
