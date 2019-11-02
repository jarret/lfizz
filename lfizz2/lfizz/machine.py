# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import logging

class Machine(object):
    def __init__(self, reactor, app_state, eink):
        self.reactor = reactor
        self.app_state = app_state
        self.eink = eink
        self.toggle = 0

    def post_bolt11(self, bolt11):
        logging.info("produced: %s" % bolt11)
        f = self.app_state.facts
        bolt11 = f['current_bolt11']
        satoshis = f['current_satoshis']
        exchange_rate = f['exchange_rate']
        exchange_rate_timestamp = f['exchange_rate_timestamp']
        sf = self.app_state.static_facts
        fiat_currency = sf['fiat_currency']
        fiat_price = sf['fiat_price']
        timezone = sf['timezone']
        self.eink.output_qr(bolt11, satoshis, exchange_rate,
                            exchange_rate_timestamp, fiat_currency,
                            fiat_price, timezone)

    def post_paid_event(self):
        self.eink.output_select_drink()
        logging.info("invoice was paid: VEND DRINK!")


    def draw_stuff(self):
        print("drawing random stuff")
        if self.toggle % 3 == 0:
            self.eink.draw_random_1()
        elif self.toggle % 3 == 1:
            self.eink.draw_random_2()
        elif self.toggle % 3 == 2:
            self.eink.draw_random_3()
        self.toggle += 1
        self.reactor.callLater(3.0, self.draw_stuff)

    def run(self):
        self.reactor.callLater(3.0, self.draw_stuff)
