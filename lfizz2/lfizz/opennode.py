# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import datetime
import requests
import json
import time
import pytz
import logging

from twisted.internet import threads

from print import print_red, print_yellow
from print import print_chill_purple, print_mega_white
from print import print_chill_light_blue

###############################################################################

OPEN_NODE_CHARGE_URL = 'https://api.opennode.co/v1/charges/'

OPEN_NODE_POLL_URL = 'https://api.opennode.co/v1/charge/'

OPEN_NODE_RATE_URL = "https://api.opennode.co/v1/rates"

class OpenNode(object):
    def create_charge(api_key, satoshis, description):
        try:
            data = {'amount':      satoshis,
                    'description': description}
            headers = {'Content-Type':  'application/json',
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
            url = OPEN_NODE_POLL_URL + charge_id
            response = requests.request('GET', url=url, headers=headers)
            return json.loads(response.text)
        except:
            return None

    def poll_exchange():
        response = requests.request('GET', url=OPEN_NODE_RATE_URL)
        return json.loads(response.text)


###############################################################################

QUANTITY_CHANGE_THRESHOLD = 0.000001

SATOSHIS_PER_BTC = 100000000

class Invoicer(object):
    def __init__(self, reactor, app_state, machine):
        self.reactor = reactor
        self.app_state = app_state
        self.machine = machine
        self.api_key = self.app_state.static_facts['opennode_api_key']
        self.email = self.app_state.static_facts['email']
        self.price = self.app_state.static_facts['fiat_price']
        self.currency = self.app_state.static_facts['fiat_currency']
        self.timezone = self.app_state.static_facts['timezone']

    ###########################################################################

    def deprecate_current_invoice(self):
        self.app_state.facts['last_bolt11'] = (
            self.app_state.facts['current_bolt11'])
        self.app_state.facts['last_id'] = (self.app_state.facts['current_id'])
        self.app_state.facts['last_satoshis'] = (
            self.app_state.facts['current_satoshis'])
        self.app_state.facts['last_expiry'] = (
            self.app_state.facts['current_expiry'])

    def retire_last_invoice(self):
        self.app_state.facts['last_bolt11'] = None
        self.app_state.facts['last_id'] = None
        self.app_state.facts['last_satoshis'] = None
        self.app_state.facts['last_expiry'] = None

    def set_current_invoice(self, bolt11, invoice_id, sats, expiry):
        e = datetime.datetime.fromtimestamp(expiry,
                                            tz=pytz.timezone("US/Mountain"))
        estr = e.strftime('%b %d, %H:%M:%S')

        logging.debug("setting current: %s %s %dsat %s" % (bolt11[-5:],
            invoice_id[-5:], sats, estr))
        self.app_state.facts['current_bolt11'] = bolt11
        self.app_state.facts['current_id'] = invoice_id
        self.app_state.facts['current_satoshis'] = sats
        self.app_state.facts['current_expiry'] = expiry

    ###########################################################################

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
            logging.errro("no price info")
            return None
        sats = Invoicer.calc_satoshis(details['exchange_rate'],
                                      details['price'])
        description = Invoicer.gen_description(details)
        charge = OpenNode.create_charge(details['api_key'], sats, description)
        return charge

    def _new_invoice_thread_func(details):
        return Invoicer.new_invoice(details)

    def _new_invoice_callback(self, result):
        if not result:
            # try again?
            self.reactor.callLater(3, self.new_invoice_defer)
            return

        i = result['data']
        if self.app_state.facts['current_bolt11'] != None:
            self.deprecate_current_invoice()
        self.set_current_invoice(i['lightning_invoice']['payreq'],
                                 i['id'], i['amount'],
                                 i['lightning_invoice']['expires_at'])
        self.produce_bolt11(i['lightning_invoice']['payreq'])

    def new_invoice_defer(self):
        if not self.app_state.facts['exchange_rate']:
            logging.error("don't have the price yet!")
            return

        details = {'price':         self.price,
                   'currency':      self.currency,
                   'timezone':      self.timezone,
                   'api_key':       self.api_key,
                   'exchange_rate': self.app_state.facts['exchange_rate'],
                   'exchange_rate_timestamp':
                        self.app_state.facts['exchange_rate_timestamp'],
                  }
        d = threads.deferToThread(Invoicer._new_invoice_thread_func, details)
        d.addCallback(self._new_invoice_callback)

    ############################################################################

    def produce_bolt11(self, bolt11):
        self.machine.post_bolt11(bolt11)

    def produce_paid_event(self):
        self.eink.post_paid_event()

    ############################################################################

    def _current_check_paid_callback(self, result):
        if not result:
            logging.error("could not check invoice paid?")
            return
        logging.debug("current invoice: %s" % result)

        if result == "paid":
            self.produce_paid_event()
            self.deprecate_current_invoice()
            self.reactor.callLater(0.1, self.new_invoice_defer)
            self.reactor.callLater(5.0, self.current_check_paid_defer)
        elif result == "expired":
            self.deprecate_current_invoice()
            self.reactor.callLater(0.1, self.new_invoice_defer)
            self.reactor.callLater(5.0, self.current_check_paid_defer)
        else:
            self.reactor.callLater(2.0, self.current_check_paid_defer)

    def _last_check_paid_callback(self, result):
        if not result:
            logging.error("could not check last paid?")
            return
        logging.debug("last invoice: %s" % result)

        if result == "paid":
            self.produce_paid_event()
            self.retire_last_invoice()
        if result == "expired":
            self.retire_last_invoice()
        self.reactor.callLater(2.0, self.last_check_paid_defer)


    def _check_paid_thread_func(details):
        try:
            data = OpenNode.poll_charge(details['api_key'],
                                        details['charge_id'])
        except Exception as e:
            logging.exception("could not check paid! %s" % e)
            return None
        return data['data']['status']

    def current_check_paid_defer(self):
        if not self.app_state.facts['current_id']:
            logging.error("no current invoice")
            return
        current_details = {'api_key':   self.api_key,
                           'charge_id': self.app_state.facts['current_id']}
        d = threads.deferToThread(Invoicer._check_paid_thread_func,
                                  current_details)
        d.addCallback(self._current_check_paid_callback)

    def last_check_paid_defer(self):
        if not self.app_state.facts['last_id']:
            logging.debug("no last invoice")
            self.reactor.callLater(2.0, self.last_check_paid_defer)
            return
        last_details = {'api_key':   self.api_key,
                        'charge_id': self.app_state.facts['last_id']}
        d = threads.deferToThread(Invoicer._check_paid_thread_func,
                                  last_details)
        d.addCallback(self._last_check_paid_callback)

    ############################################################################

    def _check_invoice_exchange_rate(self):
        if not self.app_state.facts['current_id']:
            return
        new_sats = Invoicer.calc_satoshis(
            self.app_state.facts['exchange_rate'],
            self.app_state.static_facts['fiat_price'])
        old_sats = self.app_state.facts['current_satoshis']
        logging.info("old sats: %d  new sats %d" % (old_sats, new_sats))

        change = float(new_sats) / float(old_sats)
        quantity_change = abs(1.0 - change)
        logging.info("quantity change: %0.6f" % quantity_change)
        if quantity_change > QUANTITY_CHANGE_THRESHOLD:
            self.deprecate_current_invoice()
            self.reactor.callLater(0.1, self.new_invoice_defer)

    def _get_exchange_callback(self, result):
        if not result:
            logging.error("could not get exchange rate?")
            return
        logging.info("rate: %s" % result)
        self.app_state.facts['exchange_rate'] = result
        self.app_state.facts['exchange_rate_timestamp'] = time.time()

        self._check_invoice_exchange_rate()
        self.reactor.callLater(10.0, self.get_exchange_defer)

    def _get_exchange_thread_func():
        try:
            data = OpenNode.poll_exchange()
        except Exception as e:
            loggin.exception("could not get exchange rate! %s" % e)
            return None
        return data['data']['BTCCAD']['CAD']


    def get_exchange_defer(self):
        d = threads.deferToThread(Invoicer._get_exchange_thread_func)
        d.addCallback(self._get_exchange_callback)

    ############################################################################

    def run(self):
        self.reactor.callLater(1.0, self.get_exchange_defer)
        self.reactor.callLater(3.0, self.new_invoice_defer)
        self.reactor.callLater(4.0, self.current_check_paid_defer)
        self.reactor.callLater(4.0, self.last_check_paid_defer)
