import io
import ipaddress
import random
import typing

import aiohttp
import discord


class HttpConnector:

    def get_connector(self, force=False):
        raise NotImplementedError("Not Inherited.")


class StaticAioHttpConnector(HttpConnector):

    def __init__(self):
        self._tcp_connector = aiohttp.TCPConnector()

    def get_connector(self, force=False):
        return self._tcp_connector


class RandomRotatableAioHttpConnector(HttpConnector):

    def __init__(self, **kwargs):
        self._ip_ranges = kwargs.get("ip_ranges", [])
        self._ip_random_instance = random.SystemRandom()
        self._ip_random_instance.seed()
        self._tcp_connector = aiohttp.TCPConnector()
        self._rotated_pair = ()
        self._ip_failures = []

    def mark_dead(self, ip_string):
        self._ip_failures.append(ip_string)

    async def get(self, headers=None):
        pass

    def get_connector(self, force=False):
        if "rotate_" in self._ip_mode:
            needs_rotate = False

            # RotateOnBan Strategy
            if "rotate_ban" in self._ip_mode and self._tcp_connector._local_addr[0] in self._ip_failures:
                needs_rotate = True
            elif "rotate_random" in self._ip_mode:
                needs_rotate = True
            elif "rotate_" in self._ip_mode:
                pass
            if needs_rotate or force:
                interfaces = []
                for ip_range in self._ip_ranges:
                    if "/" in ip_range:
                        interfaces.append((ipaddress.ip_network(ip_range), "net"))
                    else:
                        interfaces.append((ipaddress.ip_address(ip_range), "addr"))
                interface = random.choice(interfaces)
                # if isinstance(interface,ipaddress.IPv4Network): # self._rotated_pair
        elif "static" in self._ip_mode:
            return self._tcp_connector

    @property
    def rotated_pair(self):
        return self._rotated_pair
