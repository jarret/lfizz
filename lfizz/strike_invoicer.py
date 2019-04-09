# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import datetime
import pytz

from twisted.internet import threads

SATOSHIS_PER_BTC = 100000000

class StrikeInvoicer(object):
    def __init__(self, reactor, app_state):
        self.reactor = reactor
        self.app_state = app_state
        self.api_key = self.app_state.static_facts['strike_api_key']
        self.email = self.app_state.static_facts['email']
        self.price = self.app_state.static_facts['fiat_price']
        self.currency = self.app_state.static_facts['fiat_currency']
        self.timezone = self.app_state.static_facts['timezone']

    def calc_satoshis(self):
        rate = self.app_state.facts['exchange_rate']
        price = self.price
        return round((price / rate) * SATOSHIS_PER_BTC)

    def fmt_timestamp(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp,
                                             tz=pytz.timezone(self.timezone))
        return dt.strftime('%b %d, %H:%M:%S')

    def gen_description(self):
        rate = self.app_state.facts['exchange_rate']
        t = self.fmt_timestamp(self.app_state.facts['exchange_rate_timestamp'])
        return ("One soda. $%0.2f %s calculated at rate $%0.2f BTC%s "
                "fetched at %s") % (self.price, self.currency, rate,
                                    self.currency, t)

    def new_invoice(self):
        if not self.app_state.facts['exchange_rate']:
            print("no price info")
            return
        sat = self.calc_satoshis()
        description = self.gen_description()
        print("satoshis: %d - description: %s" % (sat, description))

    def _new_invoice_thread_func():
        print("thread func")
        return "asdf"

    def _new_invoice_callback(self, result):
        print("callback: %s" % result)
        self.new_invoice()
        self.reactor.callLater(5, self._new_invoice_defer)
        pass

    def _new_invoice_defer(self):
        d = threads.deferToThread(StrikeInvoicer._new_invoice_thread_func)
        d.addCallback(self._new_invoice_callback)

    def run(self):
        self.reactor.callLater(1.0, self._new_invoice_defer)

    def stop(self):
        pass
