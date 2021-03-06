# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from print import print_chill_green, print_red

STATES = {"INIT", "BOOTSTRAP", "DISPLAY_HEALTH", "INVOICING",
          "PAYMENT_RECEIVED"}

class AppState(object):
    def __init__(self, config):
        self.static_facts = {
            'fiat_currency':  config['Vending']['FiatCurrency'],
            'fiat_price':     float(config['Vending']['FiatPrice']),
            'opennode_api_key': config['OpenNode']['ApiKey'],
            'timezone':       config['Time']['Timezone'],
            }
        self.facts = {'exchange_rate':           None,
                      'exchange_rate_timestamp': None,
                      'ip':                      None,
                      'current_bolt11':          None,
                      'current_id':              None,
                      'current_satoshis':        1,
                      'current_expiry':          None,
                      'last_bolt11':             None,
                      'last_id':                 None,
                      'last_expiry':             None,
                      'last_satoshis':           1,
                     }
        self.state = None
        self.set_state("INIT")

    ###########################################################################

    def set_state(self, new_state):
        assert new_state in STATES
        self.state = new_state

    ###########################################################################

    def update_exchange_rate(self, new_rate, timestamp):
        self.facts['exchange_rate'] = new_rate
        self.facts['exchange_rate_timestamp'] = timestamp
        print_chill_green("updated price: $%0.2f" % self.facts['exchange_rate'])
        #print("facts: %s" % self.facts)

    def exchange_rate_fetch_error(self):
        self.facts['exchange_rate'] = None
        self.facts['exchange_rate_timestamp'] = None
        self.set_state("BOOTSTRAP")
        print_red("exchange rate fetch error")

    ###########################################################################

    def update_network_ip(self, new_ip):
        self.facts['ip'] = new_ip
        #print("updated ip: %s" % self.facts['ip'])
        #print("facts: %s" % self.facts)

    def network_ip_fetch_error(self):
        self.facts['ip'] = None
        self.set_state("BOOTSTRAP")
        print_red("network fetch error")
