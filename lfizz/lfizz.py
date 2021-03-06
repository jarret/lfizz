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


import RPi.GPIO as GPIO

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from third_party.waveshare.epd4in2 import EPD

from app_state import AppState
from opennode import Invoicer
from eink import Eink
from machine import Machine
from electrical import Electrical
from leds import Leds

from log_setup import setup_logging
from network_health import NetworkHealth

class LFizz(Service):
    def __init__(self, config_file, mock_gpio=False):
        super().__init__()

        if not mock_gpio:
            GPIO.setwarnings(False)
            if GPIO.getmode() != GPIO.BOARD:
                GPIO.setmode(GPIO.BOARD)
            Electrical.setup_gpio()
            Eink.EPD = EPD()

        self.eink = Eink(reactor)
        self.config = self._parse_config(config_file)
        self._setup_logging(self.config)
        self.app_state = AppState(self.config)
        self.leds = Leds()
        self.machine = Machine(reactor, self.app_state, self.eink, self.leds)
        self.network_health = NetworkHealth(reactor, self.machine)
        self.invoicer = Invoicer(reactor, self.app_state, self.machine)
        self.electical = Electrical(reactor, self.machine)


    ###########################################################################

    def _parse_config(self, config_file):
        if not os.path.exists(config_file):
            sys.exit("please add a config file at %s" % config_file)
        config = configparser.ConfigParser()
        config.read(config_file)
        if config['OpenNode']['ApiKey'] == 'sk_your_api_key':
            sys.exit("please set your Node API key in %s" % config_file)
        return config

    def _setup_logging(self, config):
        if not config['Logging']['Enabled']:
            return
        filename = os.path.join(config['Logging']['Dir'], "lfizz.log")
        setup_logging(filename)

    ###########################################################################

    def run_lfizz(self):
        self.network_health.run()
        self.invoicer.run()
        self.machine.run()
        reactor.run()

    def stop_lfizz(self):
        self.invoicer.stop()
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


DESCRIPTION = "LFizz - capitalist drink dispenser"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-m', '--mock-gpio', action='store_true',
                        help="run without gpio for dev/test on a non-pi system")
    settings = parser.parse_args()

    lf = LFizz("/etc/lfizz.conf", settings.mock_gpio)
    lf.run_lfizz()
