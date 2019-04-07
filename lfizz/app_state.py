# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

STATES = {"INIT", "BOOTSTRAP", "DISPLAY_HEALTH", "INVOICING",
          "PAYMENT_RECEIVED"}


class AppState(object):
    def __init__(self):
        self.facts = {'CADBTC':         6500.00,
                      'ip':             "0.0.0.0",
                      'current_bolt11': None,
                      'last_bolt11':    None,
                     }
        self.set_state("INIT")

    def set_state(self, new_state):
        assert new_state in STATES
        self.state = new_state

    ###########################################################################

    def update_price(self, new_price):
        self.facts['CADBTC'] = new_price
        print("updated price: $%0.2f" % self.facts['CADBTC'])

    def price_fetch_error(self):
        self.set_state("BOOTSTRAP")

    ###########################################################################

    def update_network_ip(self, new_ip):
        self.facts['ip'] = new_ip
        print("updated ip: %s" % self.facts['ip'])

    def network_ip_fetch_error(self):
        self.set_state("BOOTSTRAP")


