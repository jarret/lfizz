# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import datetime
import requests
import json
import pytz

from twisted.internet import threads


STRIKE_URL = 'https://api.strike.acinq.co/api/v1/charges'

class Strike(object):
    def create_charge(api_key, satoshis, description):
        #try:
        data = {'amount':      satoshis,
                'description': description,
                'currency':    'btc'}
        headers = {'Content-Type': 'application/json'}
        auth = (api_key, '')
        response = requests.request('POST', url=STRIKE_URL,
                                    data=json.dumps(data), headers=headers, auth=auth)
        return json.loads(response.text)
        #except:
        #    return None



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
        self.invoice = None

    def calc_satoshis(exchange_rate, price):
        self.email = self.app_state.static_facts['email']
        return round((price / exchange_rate) * SATOSHIS_PER_BTC)

    def fmt_timestamp(timestamp, timezone):
        dt = datetime.datetime.fromtimestamp(timestamp,
                                             tz=pytz.timezone(timezone))
        return dt.strftime('%b %d, %H:%M:%S')

    def gen_description(details):
        rate = details['exchange_rate']
        t = StrikeInvoicer.fmt_timestamp(details['exchange_rate_timestamp'],
                                         details['timezone'])
        return ("One soda. $%0.2f %s calculated at rate $%0.2f BTC%s "
                "fetched at %s") % (details['price'], details['currency'],
                                    rate, details['currency'], t)

    def new_invoice(details):
        if not details['exchange_rate']:
            print("no price info")
            return
        sats = StrikeInvoicer.calc_satoshis(details['exchange_rate'],
                                            details['price'])
        description = StrikeInvoicer.gen_description(details)
        print("satoshis: %d - description: %s" % (sats, description))
        return Strike.create_charge(details['api_key'], sats, description)

    def _new_invoice_thread_func(details):
        print("thread func")
        i = StrikeInvoicer.new_invoice(details)
        return i

    def _new_invoice_callback(self, result):
        print("callback: %s" % result)
        self.invoice = result
        self.app_state.static_facts['current_bolt11'] = self.invoice
        self.reactor.callLater(5, self._new_invoice_defer)
        pass

    def _new_invoice_defer(self):
        details = {'price':         self.price,
                   'currency':      self.currency,
                   'timezone':      self.timezone,
                   'api_key':       self.api_key,
                   'exchange_rate': self.app_state.facts['exchange_rate'],
                   'exchange_rate_timestamp': self.app_state.facts['exchange_rate_timestamp'],
                  }
        if not self.invoice:
            d = threads.deferToThread(StrikeInvoicer._new_invoice_thread_func,
                                      details)
            d.addCallback(self._new_invoice_callback)

    def run(self):
        self.reactor.callLater(1.0, self._new_invoice_defer)

    def stop(self):
        pass
