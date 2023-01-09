import os
import sys
import signal
import logging
import urllib3
import argparse

import pathlib as pl

from typing import List

from . import functions as fn
from .environment import regex
from .banner import print_banner
from .version import __version__
from .CustomLogger import colors as c

logger = logging.getLogger('DNSValidator')

def get_args(argList: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", help="Print additional error messages (default: false)",
        action="store_true")
    group.add_argument("-q", "--quiet", help="Do not print banner or error messages (default: false)",
        action="store_true")

    parser.add_argument("-i", "--input-file", help="Input file containing DNS server addresses (one per line) (default: public-dns.info/nameservers.txt)",
        action="store", type=str, required=False)
    parser.add_argument("-o", "--output-file", help="Output file name (default: ./resolvers.txt)",
        action="store", type=str, required=False, default='resolvers.txt')
    parser.add_argument("-r", "--root-domain", help="Root domain to compare (non-geolocated) (default: bet365.com)",
        action="store", type=str, required=False, default='bet365.com')
    parser.add_argument("-t", "--threads", help="Concurrent threads to run (default: 2)",
        action="store", type=int, required=False, default=2)

    parser.add_argument('-V', '--version', action='version', version=__version__)

    return parser.parse_args(argList)

def main():
    argvals = None
    argvals = sys.argv[1:]
    args = get_args(argvals)

    ##->> Look Maa!!!
    if not args.quiet: print_banner()

    ##->> Fetch Public DNS Servers if INPUT is not provided
    if args.input_file:
        if pl.Path(args.input_file).exists():
            logger.info(f'Reading nameserver list from file...', extra={'msgC':c['cyan']})
            servers = pl.Path(args.input_file).read_text().splitlines()
            servers = list(filter(lambda x: regex.match(x), servers))
        else:
            logger.error(f'Failed to read nameserver list from file')
            if args.verbose: logger.debug(f'File not found: {args.input_file}')

    else:
        logger.info('No input provided, fetching nameservers from https://public-dns.info', extra={'msgC':c['cyan']})
        http = urllib3.PoolManager()
        r = http.request('Get', 'https://public-dns.info/nameservers.txt')
        servers = r.data.decode().splitlines()
        servers = list(filter(lambda x: regex.match(x), servers))

    ##->> Declare signal handler to immediately exit on KeyboardInterrupt
    def signal_handler(signal, frame):
        os._exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    ##->> Run the script
    fn.run(
        servers=servers,
        workers=args.threads,
        rootDom=args.root_domain,
        fileName=args.output_file,
        silent=args.quiet,
        vocal=args.verbose
    )

    ##->> We're done, mate!
    sys.exit(0)

if __name__ == '__main__':
    main()
