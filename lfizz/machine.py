# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import logging

from twisted.internet.task import LoopingCall


MACHINE_STATES = {'INIT', "INVOICING", "VENDING", "ERROR"}

class Machine(object):
    def __init__(self, reactor, app_state, eink, leds):
        self.reactor = reactor
        self.app_state = app_state
        self.eink = eink
        self.leds = leds
        self.toggle = 0
        self.state = "INIT"
        self.electrical = None
        self.idle_poke = LoopingCall(self.change_idle_led)
        self.idle_poke.start(60.0, now=False)

    def change_idle_led(self):
        if self.state not in {"INVOICING", "INIT"}:
            return
        new_mode = self.leds.new_idle_mode()
        self.leds.set_mode(new_mode)

    def set_electrical(self, electrical):
        self.electrical = electrical

    def change_state(self, new_state):
        assert new_state in MACHINE_STATES
        self.state = new_state

        if new_state in {"INVOICING", "INIT"}:
            self.leds.set_mode(self.leds.new_idle_mode())
        elif new_state == "VENDING":
            self.leds.set_mode("IMPLODE")
        elif new_state == "ERROR":
            self.leds.set_mode("ERROR")
        else:
            self.leds.set_mode("EXIT")

    def bolt11_on_screen(self, bolt11):
        logging.info("bolt11 on screen: %s" % bolt11)
        f = self.app_state.facts
        if not f['current_bolt11']:
            logging.info("no current bolt11 to display")

        bolt11 = f['current_bolt11']
        satoshis = f['current_satoshis']
        exchange_rate = f['exchange_rate']
        exchange_rate_timestamp = f['exchange_rate_timestamp']
        sf = self.app_state.static_facts
        fiat_currency = sf['fiat_currency']
        fiat_price = sf['fiat_price']
        timezone = sf['timezone']
        self.eink.draw_qr(bolt11, satoshis, exchange_rate,
                          exchange_rate_timestamp, fiat_currency,
                          fiat_price, timezone)

    def post_bolt11(self, bolt11):
        logging.info("produced bolt11: %s" % bolt11)
        if self.state in {"INVOICING", "INIT"}:
            self.bolt11_on_screen(bolt11)
            self.change_state("INVOICING")
        if self.state is "ERROR":
            logging.error("system is errored")
            return

    def post_paid_event(self):
        if self.state == "ERROR":
            logging.error("system is errored")
            return
        if self.state != "INVOICING":
            return
        logging.info("invoice was paid: VEND DRINK!")
        self.change_state('VENDING')
        self.eink.draw_select_drink()
        self.electrical.trigger_coin_mech()

    def post_vend_finished(self):
        logging.info("drink finished vending")
        if self.state == "VENDING":
            self.change_state('INVOICING')
            f = self.app_state.facts
            self.bolt11_on_screen(f['current_bolt11'])
        else:
            print("disregarding vend finished - wasn't expecting it")

    def post_error(self):
        self.change_state('ERROR')
        self.eink.draw_error()

    ##########################################################################

    def run(self):
        #self.reactor.callLater(10.0, self.draw_stuff)
        pass
