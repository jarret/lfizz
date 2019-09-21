# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import datetime
import requests
import json
import pytz

from twisted.internet import threads

from print import print_red, print_yellow
from print import print_chill_purple, print_mega_white

###############################################################################

OPEN_NODE_CHARGE_URL = 'https://api.opennode.co/v1/charges'

OPEN_NODE_RATE_URL = "https://api.opennode.co/v1/rates"

class OpenNode(object):
    def create_charge(api_key, satoshis, description):
        try:
            data = {'amount':      satoshis,
                    'description': description,
                   }
            headers = {'Content-Type': 'application/json',
                       'Authorization': api_key}
            response = requests.request('POST', url=OPEN_NODE_CHARGE_URL,
                                        data=json.dumps(data), headers=headers,
                                       )
            return json.loads(response.text)
        except:
            return None

    def poll_charge(api_key, charge_id):
        try:
            headers = {"Authorization": api_key}
            response = requests.request('GET', url=OPEN_NODE_CHARGE_URL,
                                        headers=headers)
            return json.loads(response.text)
        except:
            return None

    def poll_exchange():
        response = requests.request('GET', url=OPEN_NODE_RATE_URL)
        return json.loads(response.text)


###############################################################################


SATOSHIS_PER_BTC = 100000000

class Invoicer(object):
    def __init__(self, reactor, app_state):
        self.reactor = reactor
        self.app_state = app_state
        self.api_key = self.app_state.static_facts['opennode_api_key']
        self.email = self.app_state.static_facts['email']
        self.price = self.app_state.static_facts['fiat_price']
        self.currency = self.app_state.static_facts['fiat_currency']
        self.timezone = self.app_state.static_facts['timezone']

    def calc_satoshis(exchange_rate, price):
        return round((price / exchange_rate) * SATOSHIS_PER_BTC)

    def fmt_timestamp(timestamp, timezone):
        dt = datetime.datetime.fromtimestamp(timestamp,
                                             tz=pytz.timezone(timezone))
        return dt.strftime('%b %d, %H:%M:%S')

    def gen_description(details):
        rate = details['exchange_rate']
        t = Invoicer.fmt_timestamp(details['exchange_rate_timestamp'],
                                   details['timezone'])
        return ("One soda. $%0.2f %s calculated at rate $%0.2f BTC%s "
                "fetched at %s") % (details['price'], details['currency'],
                                    rate, details['currency'], t)

    def new_invoice(details):
        if not details['exchange_rate']:
            print_red("no price info")
            return None
        sats = Invoicer.calc_satoshis(details['exchange_rate'],
                                      details['price'])
        description = Invoicer.gen_description(details)
        # print("satoshis: %d - description: %s" % (sats, description))
        charge = OpenNode.create_charge(details['api_key'], sats, description)
        # print(json.dumps(charge, indent=1, sort_keys=True))
        return charge

    def _new_invoice_thread_func(details):
        # print("thread func")
        return Invoicer.new_invoice(details)

    def _new_invoice_callback(self, result):
        if not result:
            # try again?
            # print("trouble getting invoice!")
            self.reactor.callLater(3, self.new_invoice_defer)
            return
        i = result
        bolt11 = i['iightning_invoice']['payreq']
        expiry = i['lightning_invoice']['created_at']
        sats = i['lightning_invoice']['amount']

        self.app_state.facts['current_bolt11'] = bolt11
        self.app_state.facts['current_id'] = i
        self.app_state.facts['current_satoshis'] = sats
        self.app_state.facts['current_expiry'] = expiry

    def new_invoice_defer(self):
        details = {'price':         self.price,
                   'currency':      self.currency,
                   'timezone':      self.timezone,
                   'api_key':       self.api_key,
                   'exchange_rate': self.app_state.facts['exchange_rate'],
                   'exchange_rate_timestamp':
                        self.app_state.facts['exchange_rate_timestamp'],
                  }
        print(details)
        d = threads.deferToThread(Invoicer._new_invoice_thread_func, details)
        d.addCallback(self._new_invoice_callback)

    ############################################################################

    def _get_exchange_callback(self, result):
        if not result:
            print_red("could not get exchange rate?")
            return
        self.app_state.facts['exchange_rate']

    def get_exchange_defer(self)
        d = threads.deferToThread(Invoicer._get_exchange_thread_func, details)
        d.addCallback(self._get_exchange_callback)

    ############################################################################

    def run(self):
        self.reactor.callLater(1.0, self.new_invoice_defer)

if __name__ == "__main__":
    v = OpenNode.poll_exchange()['data']['BTCCAD']['CAD']
    print(v)
