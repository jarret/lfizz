# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import psutil

from twisted.internet import threads

POLL_SLEEP = 10 # every 10 seconds

class NetworkIp(object):
    """ Periodically query the system for the LAN IP address to use
        as an indicator of network health and notify where an admin
        can SSH in for maintainence. """

    def __init__(self, reactor, app_state):
        self.reactor = reactor
        self.app_state = app_state
        self.actor = None

    def set_actor(self, actor):
        self.actor = actor

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
        ips = list(NetworkIp._get_ips())
        if len(ips) > 0:
            return ips[0]
        return None

    def _get_ip_callback(self, result):
        if result:
            self.app_state.update_network_ip(result)
        else:
            self.app_state.update_network_ip_error()
        self.reactor.callLater(POLL_SLEEP, self._get_ip_defer)
        self.actor.poke_stats()

    def _get_ip_defer(self):
        d = threads.deferToThread(NetworkIp._get_ip_thread_func)
        d.addCallback(self._get_ip_callback)

    #######################################################################

    def run(self):
        self.reactor.callLater(1.0, self._get_ip_defer)

    def stop(self):
        pass
