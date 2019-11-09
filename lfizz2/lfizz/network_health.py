# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import psutil
import logging

from twisted.internet import threads

POLL_SLEEP = 10 # every 10 seconds

class NetworkHealth(object):
    """ Periodically query the system for the LAN IP address to use
        as an indicator of network health and notify where an admin
        can SSH in for maintainence. """

    def __init__(self, reactor, machine):
        self.reactor = reactor
        self.machine = machine

    def _get_ips():
        # TODO - this might not work as intended in all network
        # deployments. Might need to be done better.
        p = psutil.net_if_addrs()
        for i, addrs in p.items():
            for a in addrs:
                if a[0] == 2:
                    if a[1].startswith("192.168"):
                        yield a[1]

    def _get_ip_thread_func():
        ips = list(NetworkHealth._get_ips())
        if len(ips) > 0:
            return ips[0]
        return None

    def _get_ip_callback(self, result):
        if result:
            logging.info("network seems good: %s" % result)
        else:
            logging.error("network error?")
            self.machine.post_err()
        self.reactor.callLater(POLL_SLEEP, self._get_ip_defer)

    def _get_ip_defer(self):
        d = threads.deferToThread(NetworkHealth._get_ip_thread_func)
        d.addCallback(self._get_ip_callback)

    #######################################################################

    def run(self):
        self.reactor.callLater(1.0, self._get_ip_defer)

    def stop(self):
        pass
