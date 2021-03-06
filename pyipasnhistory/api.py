#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests

from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlparse

import ipaddress


class IPASNHistory():

    def __init__(self, root_url: str='https://ipasnhistory.circl.lu/'):
        self.root_url = root_url
        if not urlparse(self.root_url).scheme:
            self.root_url = 'http://' + self.root_url
        if not self.root_url.endswith('/'):
            self.root_url += '/'
        self.session = requests.session()

    @property
    def is_up(self):
        r = self.session.head(self.root_url)
        return r.status_code == 200

    def meta(self):
        '''Get meta information from the remote instance'''
        r = requests.get(urljoin(self.root_url, 'meta'))
        return r.json()

    def mass_cache(self, list_to_cache: list):
        '''Cache a list of IP queries. The next call on the same IPs will be very quick.'''
        to_query = []
        for entry in list_to_cache:
            if 'precision_delta' in entry:
                entry['precision_delta'] = json.dumps(entry.pop('precision_delta'))
            to_query.append(entry)

        r = self.session.post(urljoin(self.root_url, 'mass_cache'), data=json.dumps(to_query))
        return r.json()

    def mass_query(self, list_to_query: list):
        '''Query a list of IPs.'''
        to_query = []
        for entry in list_to_query:
            if 'precision_delta' in entry:
                entry['precision_delta'] = json.dumps(entry.pop('precision_delta'))
            to_query.append(entry)
        r = self.session.post(urljoin(self.root_url, 'mass_query'), data=json.dumps(to_query))
        return r.json()

    def asn_meta(self, asn: Optional[int]=None, source: Optional[str]=None, address_family: str='v4',
                 date: Optional[str]=None, first: Optional[str]=None, last: Optional[str]=None,
                 precision_delta: Optional[Dict]=None):
        '''Get all the prefixes annonced by an AS'''
        to_query: Dict[str, Any] = {'address_family': address_family}
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

        r = self.session.post(urljoin(self.root_url, 'asn_meta'), data=json.dumps(to_query))
        return r.json()

    def _aggregate_details(self, details: dict):
        '''Aggregare the response when the asn/prefix tuple is the same over a period of time.'''
        to_return = []
        current = None
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

    def query(self, ip: str, source: Optional[str]=None, address_family: Optional[str]=None,
              date: Optional[str]=None, first: Optional[str]=None, last: Optional[str]=None,
              precision_delta: Optional[Dict]=None, aggregate: bool=False):
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
