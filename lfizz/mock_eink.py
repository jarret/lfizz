# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from print import print_green

class MockEink(object):
    def __init__(self):
        pass

    def output_first_boot(self):
        print_green("=" * 80)
        print_green("= fizzz boot up - finding network...")
        print_green("=" * 80)

    def output_boot_up(self, ip, exchange_rate, invoice):
        print_green("=" * 80)
        print_green("= ip:            %s" % ip)
        print_green("= exchange_rate: %s" % exchange_rate)
        print_green("= invoice:       %s" % invoice)
        print_green("=" * 80)

    def output_qr(self, bolt11):
        print_green("=" * 80)
        print_green("= %s" % bolt11)
        print_green("=" * 80)

    def output_select_drink(self):
        print_green("=" * 80)
        print_green("= select yer drink....")
        print_green("=" * 80)

    def output_error(self):
        print_green("=" * 80)
        print_green("= having problems")
        print_green("=" * 80)
