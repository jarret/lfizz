# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time
import requests
import json

from twisted.internet import threads


BITPAY_RATE_URL = "https://bitpay.com/api/rates/BTC"
HEADERS = {'User-Agent':      'a-bitcoin-driven-soda-machine',
           'Accept-Encoding': 'gzip',
          }

#POLL_SLEEP = 60 * 10 # every 10 minutes
POLL_SLEEP = 10 # every 60 seconds


class FiatPrice(object):
    """ Periodically fetches the CADBTC exchange rate from BitPay for the
        applicaton to use. """
    def __init__(self, reactor, app_state):
        self.reactor = reactor
        self.app_state = app_state
        self.fiat_currency = app_state.static_facts['fiat_currency']
        self.headers = HEADERS.copy()
        self.headers['From'] = self.app_state.static_facts['email']
        self.actor = None

    def set_actor(self, actor):
        self.actor = actor

    def _pull_price_thread_func(fiat_currency, headers):
        try:
            response = requests.request('GET', url=BITPAY_RATE_URL,
                                        headers=headers)
            prices = json.loads(response.text)
            for p in prices:
                if p['code'] == fiat_currency:
                    return p['rate']
            return None
        except:
            return None

    def _pull_price_callback(self, result):
        if result:
            self.app_state.update_exchange_rate(result, time.time())
            self.actor.check_exchange_rate()
            self.actor.check_expiry()
            self.actor.poke_stats()
        else:
            self.app_state.exchange_rate_fetch_error()
        self.reactor.callLater(POLL_SLEEP, self._pull_price_defer)

    def _pull_price_defer(self):
        d = threads.deferToThread(FiatPrice._pull_price_thread_func,
                                  self.fiat_currency, self.headers)
        d.addCallback(self._pull_price_callback)

    #######################################################################

    def run(self):
        self.reactor.callLater(1.0, self._pull_price_defer)

    def stop(self):
        pass
