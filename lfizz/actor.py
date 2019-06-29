# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time
from strike_invoicer import StrikeInvoicer
from print import print_green, print_chill_light_blue

QUANTITY_CHANGE_THRESHOLD = 0.0001

SECONDS_APPROACHING_EXPIRY = 60 * 5 # 5 minutes

BOOT_SCREEN_DURATION = 8

class Actor(object):
    def __init__(self, reactor, app_state, electrical, eink, strike_invoicer):
        self.reactor = reactor
        self.app_state = app_state
        self.electrical = electrical
        self.eink = eink
        self.strike_invoicer = strike_invoicer
        self.boot_screen_ends = time.time() + BOOT_SCREEN_DURATION
        self.has_invoice = False

    def trigger_coin_mech(self):
        self.electrical.trigger_coin_mech()

    def get_new_invoice(self):
        self.strike_invoicer.kick_invoice_request()

    def check_expiry(self):
        now = time.time()
        expiry = self.app_state.facts['current_expiry']
        expiry = expiry if expiry else (now + 3600)
        #print("check expiry: %d now: %d" % (expiry, now))

        if (now + SECONDS_APPROACHING_EXPIRY) > expiry:
            self.new_invoice()
            return
        #print("not expired")


    def check_exchange_rate(self):
        new_rate = self.app_state.facts['exchange_rate']
        old_sats = self.app_state.facts['current_satoshis']
        fiat_price = self.app_state.static_facts['fiat_price']
        #print("exchange change")
        #print("new rate: %0.8f" % (new_rate))
        #print("old_sats: %d" % (old_sats if old_sats else 0))
        #print("fiat price: %0.4f" % fiat_price)
        new_sats = StrikeInvoicer.calc_satoshis(new_rate, fiat_price)
        #print("new sats: %d" % (new_sats))
        change = float(new_sats) / float(old_sats)
        quantity_change = abs(1.0 - change)
        print_chill_light_blue("quantity change: %0.6f" % quantity_change)

        if quantity_change > QUANTITY_CHANGE_THRESHOLD:
            print("new invoice")
            self.new_invoice()
            return
        #print("keep this invoice")

    def new_invoice(self):
        print_green("getting new invoice")
        # TODO left off here - haven't run code!
        a = self.app_state
        a.facts['last_bolt11'] = a.facts['current_bolt11']
        a.facts['last_id'] = a.facts['current_id']
        a.facts['last_expiry'] = a.facts['current_expiry']
        a.facts['last_satoshis'] = a.facts['current_satoshis']
        self.strike_invoicer.kick_invoice_request()

    def prompt_drink_selection(self):
        self.eink.output_select_drink()

    def announce_new_invoice(self, bolt11):
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
        self.has_invoice = True

    def output_first_boot(self):
        self.eink.output_first_boot()

    def poke_stats(self):
        if time.time() > self.boot_screen_ends:
            return
        if self.has_invoice:
            return
        f = self.app_state.facts
        ip = f['ip']
        exchange_rate = f['exchange_rate']
        invoice = f['current_bolt11']
        self.eink.output_boot_up(ip, exchange_rate, invoice)
