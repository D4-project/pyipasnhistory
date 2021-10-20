.. PyLookyloo documentation master file, created by
   sphinx-quickstart on Tue Mar 23 12:28:17 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyIPASNHistory's documentation!
===========================================

This is the client API for `IP ASN History <https://github.com/D4-project/IPASN-History>`_:


Installation
------------

The package is available on PyPi, so you can install it with::

  pip install pyipasnhistory


Usage
-----

You can use `ipasnhistory` as a python script::

	$ ipasnhistory -h
	usage: ipasnhistory [-h] [--url URL] (--meta | --file FILE | --ip IP) [--source SOURCE] [--address_family ADDRESS_FAMILY] [--date DATE] [--first FIRST]
						[--last LAST]

	Run a query against IP ASN History

	optional arguments:
	  -h, --help            show this help message and exit
	  --url URL             URL of the instance.
	  --meta                Get meta information.
	  --file FILE           Mass process queries from a file.
	  --ip IP               IP to lookup
	  --source SOURCE       Source to query (currently, only "caida" and "ripe_rrc00" are supported)
	  --address_family ADDRESS_FAMILY
							Can be either v4 or v6
	  --date DATE           Exact date to lookup. Fallback to most recent available.
	  --first FIRST         First date in the interval
	  --last LAST           Last date in the interval

Or as a library:

.. toctree::
   :glob:

   api_reference


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
