# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


import requests
import json

from twisted.internet import threads


BITPAY_RATE_URL = "https://bitpay.com/api/rates/BTC"
HEADERS = {'User-Agent':      'a-bitcoin-driven-soda-machine',
           'From':            'jarret.dyrbye@gmail.com',
           'Accept-Encoding': 'gzip',
          }

#POLL_SLEEP = 60 * 10 # every 10 minutes
POLL_SLEEP = 10 # every 10 seconds


class CadPrice(object):
    """ Periodically fetches the CADBTC exchange rate from BitPay for the
        applicaton to use. """
    def __init__(self, reactor, app_state):
        self.reactor = reactor
        self.app_state = app_state

    def _pull_price_thread_func():
        try:
            response = requests.request('GET', url=BITPAY_RATE_URL,
                                        headers=HEADERS)
            prices = json.loads(response.text)
            for p in prices:
                if p['code'] == 'CAD':
                    return p['rate']
            return None
        except:
            return None

    def _pull_price_callback(self, result):
        if result:
            self.app_state.update_price(result)
        else:
            self.app_state.update_price_fetch_error()
        self.reactor.callLater(POLL_SLEEP, self._pull_price_defer)

    def _pull_price_defer(self):
        d = threads.deferToThread(CadPrice._pull_price_thread_func)
        d.addCallback(self._pull_price_callback)

    #######################################################################

    def run(self):
        self.reactor.callLater(1.0, self._pull_price_defer)

    def stop(self):
        pass
