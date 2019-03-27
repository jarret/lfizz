#!/usr/bin/env python3
# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


from twisted.internet import reactor
from twisted.internet.task import LoopingCall


class LFizz(object):
    def __init__(self):
        self.count = 0
        self.count_loop = LoopingCall(self.output_count)
        self.count_loop.start(1.0, now=False)

    def output_count(self):
        print("the count is: %d" % self.count)
        self.count += 1

    def run(self):
        reactor.run()


if __name__ == '__main__':
    lf = LFizz()
    lf.run()
