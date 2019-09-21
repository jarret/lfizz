#!/usr/bin/env python3
# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import sys
import time
import argparse
import configparser

from twisted.application.service import Service
from twisted.internet import reactor

#from led_blink import LedBlink
from app_state import AppState
#from fiat_price import FiatPrice
#from network_ip import NetworkIp
from opennode import Invoicer

class LFizz(Service):
    def __init__(self, config_file):
        super().__init__()

        self.config = self._parse_config(config_file)
        self.app_state = AppState(self.config)
        self.invoicer = Invoicer(reactor, self.app_state)
       #self.strike_watcher = StrikeWatcher(reactor, self.actor, self.app_state)
        #self.fiat_price = FiatPrice(reactor, self.app_state)
        #self.network_ip = NetworkIp(reactor, self.app_state)


    ###########################################################################

    def _parse_config(self, config_file):
        if not os.path.exists(config_file):
            sys.exit("please add a config file at %s" % config_file)
        config = configparser.ConfigParser()
        config.read(config_file)
        if config['OpenNode']['ApiKey'] == 'sk_your_api_key':
            sys.exit("please set your Node API key in %s" % config_file)
        return config

    ###########################################################################

    def run_lfizz(self):
#        self.led_blink.run()
#        self.fiat_price.run()
#        self.network_ip.run()
        self.invoicer.run()
#        self.strike_watcher.run()
        reactor.run()

    def stop_lfizz(self):
#        self.led_blink.stop()
#        self.fiat_price.stop()
#        self.network_ip.stop()
        self.invoicer.stop()
#        self.strike_watcher.stop()
        reactor.stop()

    ###########################################################################

#    def startService(self):
#        super().startService()
#        self.run_lfizz()
#
#    def stopService(self):
#        super().stopService()
#        self.stop_lfizz()
#        reactor.stop()
#

###############################################################################


DESCRIPTION = "LFizz - capitalist drink dispenser"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-m', '--mock-gpio', action='store_true',
                        help="run without gpio for dev/test on a non-pi system")
    settings = parser.parse_args()

    lf = LFizz("/etc/lfizz.conf")
    lf.run_lfizz()