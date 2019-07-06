# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import datetime
import requests
import json
import pytz
from bolt11 import Bolt11

from twisted.internet import threads

from print import print_red, print_yellow
from print import print_chill_purple, print_mega_white

###############################################################################

STRIKE_URL = 'https://api.strike.acinq.co/api/v1/charges'

class Strike(object):
    def create_charge(api_key, satoshis, description):
        try:
            data = {'amount':      satoshis,
                    'description': description,
                    'currency':    'btc'}
            headers = {'Content-Type': 'application/json'}
            auth = (api_key, '')
            response = requests.request('POST', url=STRIKE_URL,
                                        data=json.dumps(data), headers=headers,
                                        auth=auth)
            return json.loads(response.text)
        except:
            return None

    def poll_charge(api_key, charge_id):
        #print("polling: %s" % charge_id)
        url = STRIKE_URL + "/" + charge_id
        auth = (api_key, '')
        headers = {'Content-Type': 'application/json'}
        response = requests.request('GET', url=url, headers=headers, auth=auth)
        return json.loads(response.text)


###############################################################################

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
        self.actor = None

    def set_actor(self, actor):
        self.actor = actor

    def calc_satoshis(exchange_rate, price):
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
            print_red("no price info")
            return None, None
        sats = StrikeInvoicer.calc_satoshis(details['exchange_rate'],
                                            details['price'])
        description = StrikeInvoicer.gen_description(details)
        # print("satoshis: %d - description: %s" % (sats, description))
        charge = Strike.create_charge(details['api_key'], sats, description)
        # print(json.dumps(charge, indent=1, sort_keys=True))
        return charge, sats

    def _new_invoice_thread_func(details):
        # print("thread func")
        charge, sats = StrikeInvoicer.new_invoice(details)
        if charge:
            return charge['id'], charge['payment_request'], sats
        else:
            return None

    def _new_invoice_callback(self, result):
        if not result:
            # try again?
            # print("trouble getting invoice!")
            self.reactor.callLater(3, self._new_invoice_defer)
            return
        i, bolt11, sats = result
        # print("callback i: %s bolt11: %s" % (i, bolt11))
        b11 = Bolt11.to_dict(bolt11)
        # print("decoded: %s" % json.dumps(b11, indent=1, sort_keys=True))
        expiry = b11['created_at'] + b11['expiry']
        self.app_state.facts['current_bolt11'] = bolt11
        self.app_state.facts['current_id'] = i
        self.app_state.facts['current_satoshis'] = sats
        self.app_state.facts['current_expiry'] = expiry

        self.actor.announce_new_invoice(bolt11)

    def new_invoice_defer(self):
        details = {'price':         self.price,
                   'currency':      self.currency,
                   'timezone':      self.timezone,
                   'api_key':       self.api_key,
                   'exchange_rate': self.app_state.facts['exchange_rate'],
                   'exchange_rate_timestamp':
                        self.app_state.facts['exchange_rate_timestamp'],
                  }
        d = threads.deferToThread(StrikeInvoicer._new_invoice_thread_func,
                                  details)
        d.addCallback(self._new_invoice_callback)

    def run(self):
        self.reactor.callLater(1.0, self.new_invoice_defer)
        pass

    def stop(self):
        pass


###############################################################################

STRIKE_POLL_TIME = 2

class StrikeWatcher(object):
    def __init__(self, reactor, actor, app_state):
        self.reactor = reactor
        self.app_state = app_state
        self.actor = actor

    ##########################################################################

    def _check_strike_thread_func(api_key, current_id, last_id):
        c = Strike.poll_charge(api_key, current_id) if current_id else None
        l = Strike.poll_charge(api_key, last_id) if last_id else None
        cp = c['paid'] if c else False
        lp = l['paid'] if l else False
        # print("current_paid: %s last_paid: %s" % (cp, lp))
        # print(json.dumps(c, indent=1, sort_keys=True))
        return {'current_paid': cp,
                'last_paid':    lp}


    def _check_strike_callback(self, result):
        if result['current_paid']:
            print_mega_white("current strike paid")
            self.actor.trigger_coin_mech()
            self.app_state.facts['current_id'] = None
            self.app_state.facts['current_bolt11'] = None
            self.actor.get_new_invoice()
            self.actor.prompt_drink_selection()
        elif result['last_paid']:
            print_mega_white("last strike paid")
            self.app_state.facts['last_id'] = None
            self.app_state.facts['last_bolt11'] = None
            self.actor.prompt_drink_selection()
        else:
            print_chill_purple("Strike not paid")
        self.reactor.callLater(STRIKE_POLL_TIME, self._check_strike_defer)

    def _check_strike_defer(self):
        api_key = self.app_state.static_facts['strike_api_key']
        current_id = self.app_state.facts['current_id']
        last_id = self.app_state.facts['last_id']
        print_yellow("checking: %s %s" % (current_id, last_id))
        d = threads.deferToThread(StrikeWatcher._check_strike_thread_func,
                                  api_key, current_id, last_id)
        d.addCallback(self._check_strike_callback)

    ##########################################################################

    def run(self):
        self.reactor.callLater(1.0, self._check_strike_defer)

    def stop(self):
        pass
