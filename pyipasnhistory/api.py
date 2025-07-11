#!/usr/bin/env python3

from __future__ import annotations

import json
import requests

from importlib.metadata import version
from typing import Any
from urllib.parse import urljoin, urlparse

import ipaddress

from urllib3.util import Retry
from requests.adapters import HTTPAdapter


class IPASNHistory():

    def __init__(self, root_url: str | None=None, useragent: str | None=None,
                 *, proxies: dict[str, str] | None=None) -> None:
        '''Initialize the IPASNHistory client.

        :param root_url: URL of the IPASNHistory instance to query. Defaults to 'https://ipasnhistory.circl.lu/'.
        :param useragent: User-Agent to use for the requests.
        :param proxies: Proxies to use for the requests.
        '''
        self.root_url = root_url if root_url else 'https://ipasnhistory.circl.lu/'
        if not urlparse(self.root_url).scheme:
            self.root_url = 'http://' + self.root_url
        if not self.root_url.endswith('/'):
            self.root_url += '/'
        self.session = requests.session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.headers['user-agent'] = useragent if useragent else f'PyIPASNHIstory / {version("pyipasnhistory")}'
        if proxies:
            self.session.proxies.update(proxies)

    @property
    def is_up(self) -> bool:
        '''Test if the given instance is accessible'''
        try:
            r = self.session.head(self.root_url)
        except requests.exceptions.ConnectionError:
            return False
        return r.status_code == 200

    def meta(self):
        '''Get meta information from the remote instance'''
        r = requests.get(urljoin(self.root_url, 'meta'))
        return r.json()

    def mass_cache(self, list_to_cache: list[dict[str, Any]]):
        '''Cache a list of IP queries. The next call on the same IPs will be very quick.'''
        to_query = []
        for entry in list_to_cache:
            if 'precision_delta' in entry:
                entry['precision_delta'] = json.dumps(entry.pop('precision_delta'))
            to_query.append(entry)

        r = self.session.post(urljoin(self.root_url, 'mass_cache'), json=to_query)
        return r.json()

    def mass_query(self, list_to_query: list[dict[str, Any]]) -> dict[str, Any]:
        '''Query a list of IPs.'''
        to_query = []
        for entry in list_to_query:
            if 'precision_delta' in entry:
                entry['precision_delta'] = json.dumps(entry.pop('precision_delta'))
            to_query.append(entry)
        r = self.session.post(urljoin(self.root_url, 'mass_query'), json=to_query)
        return r.json()

    def asn_meta(self, asn: int | None=None, source: str | None=None, address_family: str='v4',
                 date: str | None=None, first: str | None=None, last: str | None=None,
                 precision_delta: dict | None=None):
        '''Get all the prefixes annonced by an AS'''
        to_query: dict[str, Any] = {'address_family': address_family}
        if source:
            to_query['source'] = source
        if asn:
            to_query['asn'] = asn
        if date:
            to_query['date'] = date
        elif first:
            to_query['first'] = first
            if last:
                to_query['last'] = last
        if precision_delta:
            to_query['precision_delta'] = json.dumps(precision_delta)

        r = self.session.post(urljoin(self.root_url, 'asn_meta'), json=to_query)
        return r.json()

    def _aggregate_details(self, details: dict) -> list:
        '''Aggregare the response when the asn/prefix tuple is the same over a period of time.'''
        to_return = []
        current: dict[str, Any] = {}
        for timestamp, asn_prefix in details.items():
            if not current:
                # First loop
                current = {'first_seen': timestamp, 'last_seen': timestamp,
                           'asn': asn_prefix['asn'], 'prefix': asn_prefix['prefix']}
                continue
            if current['asn'] == asn_prefix['asn'] and current['prefix'] == asn_prefix['prefix']:
                current['last_seen'] = timestamp
            else:
                to_return.append(current)
                current = {'first_seen': timestamp, 'last_seen': timestamp,
                           'asn': asn_prefix['asn'], 'prefix': asn_prefix['prefix']}
        to_return.append(current)
        return to_return

    def query(self, ip: str, source: str | None=None, address_family: str | None=None,
              date: str | None=None, first: str | None=None, last: str | None=None,
              precision_delta: dict | None=None, aggregate: bool=False):
        '''Launch a query.

        :param ip: IP to lookup
        :param source: Source to query (caida or ripe_rrc00)
        :param address_family: v4 or v6. If None: use ipaddress to figure it out.
        :param date: Exact date to lookup. Fallback to most recent available.
        :param first: First date in the interval
        :param last: Last date in the interval
        :param precision_delta: Max delta allowed between the date queried and the one we have in the database. Expects a dictionary to pass to timedelta.
                                Example: {days=1, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0}
        :param aggregate: (only if more than one response) Aggregare the responses if the prefix and the ASN are the same
        '''

        try:
            if '/' in ip:
                # The user passed a prefix... getting the 1st IP in it.
                network = ipaddress.ip_network(ip)
                first_ip = network[0]
                address_family = f'v{first_ip.version}'
                ip = str(first_ip)

            if not address_family:
                ip_parsed = ipaddress.ip_address(ip)
                address_family = f'v{ip_parsed.version}'
        except ValueError:
            return {'meta': {'source': source},
                    'error': f'The IP address is invalid: "{ip}"',
                    'reponse': {}}

        to_query = {'ip': ip, 'address_family': address_family}
        if source:
            to_query['source'] = source
        if date:
            to_query['date'] = date
        elif first:
            to_query['first'] = first
            if last:
                to_query['last'] = last
        if precision_delta:
            to_query['precision_delta'] = json.dumps(precision_delta)
        r = self.session.post(urljoin(self.root_url, 'ip'), json=to_query)
        response = r.json()
        if aggregate:
            response['response'] = self._aggregate_details(response['response'])
        return response
