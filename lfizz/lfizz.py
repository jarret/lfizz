#!/usr/bin/env python3
# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from twisted.application.service import Service
from twisted.internet import reactor
from twisted.internet.task import LoopingCall


class LFizz(Service):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.count_loop = LoopingCall(self.output_count)
        self.count_loop.start(1.0, now=False)

    def output_count(self):
        print("the count is: %d" % self.count)
        self.count += 1

    def startService(self):
        super().startService()
        reactor.run()

    def stopService(self):
        super().stopService()
        reactor.stop()

#if __name__ == '__main__':
#    lf = LFizz()
#    lf.run()
