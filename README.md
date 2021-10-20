[![Documentation Status](https://readthedocs.org/projects/pyipasnhistory/badge/?version=latest)](https://pyipasnhistory.readthedocs.io/en/latest/)

# PyIPASNHistory

This is the client API for [IP ASN History](https://github.com/D4-project/IPASN-History).

## Installation

```bash
pip install pyipasnhistory
```

## Usage

### Command line

You can use the `ipasnhistory` command to query the instance.

```bash
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
```

### Library

See [API Reference](https://pyipasnhistory.readthedocs.io/en/latest/api_reference.html)
