# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time


class Actor(object):
    def __init__(self, reactor, electrical, strike_invoicer):
        self.reactor = reactor
        self.electrical = electrical
        self.strike_invoicer = strike_invoicer

    def trigger_coin_mech(self):
        self.electrical.trigger_coin_mech()

    def get_new_invoice(self):
        self.strike_invoicer.kick_invoice_request()
