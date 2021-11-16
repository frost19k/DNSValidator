#!/usr/bin/env python3

import os
import re
import sys
import string
import signal
import random
import urllib3
import argparse
import numpy as np
import dns.resolver


from concurrent.futures import ThreadPoolExecutor
from CustomLogger import CustomLogger, CustomFormatter

## Configr Logging
logger = CustomLogger('DNSValidator')
c = CustomFormatter.colors

goodip = ""
responses = dict()
validServers = list()

baselines = [
    "1.1.1.1",
    "8.8.8.8",
    "9.9.9.9"
]

positivebaselines = [
    "bet365.com",
    "telegram.com"
]

nxdomainchecks = [
    "bet365.com",
    "facebook.com",
    "google.com",
    "paypal.com",
    "telegram.com",
    "wikileaks.com"
]

def rand():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(10))

def resolve():
    pass

def resolve_address(server, resolversFile):
    ## Skip if not IPv4
    if not re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", server):
        logger.warning(f'{server}: Skipping IPv6 server')
        return

    logger.info(f'{server}: Checking...', extra={'msgC':''})

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [server]

    ## Try to resolve our positive baselines before going any further
    for nxdomaincheck in nxdomainchecks:
        ## Make sure random subdomains are NXDOMAIN
        try:
            positivehn = "{rand}.{domain}".format(
                rand=rand(),
                domain=nxdomaincheck
            )

            posanswer = resolver.resolve(positivehn, 'A')

            ## NXDomain Exception was not returned, we got records when we shouldn't have.
            ## Skip the server.
            logger.warning(f'{server}: DNS poisoning detected, skipping')
            return

        except dns.resolver.NXDOMAIN:
            pass

        except Exception as e:
            logger.warning(f'{server}: Error when checking for DNS poisoning, passing')
            return

    ## Check for NXDomain on the root-domain we're checking
    try:
        nxquery = f"{rand()}.bet365.com"
        nxanswer = resolver.resolve(nxquery, 'A')
    except dns.resolver.NXDOMAIN:
        gotnxdomain = True
    except:
        logger.error(f'{server}: Error when checking NXDOMAIN, skipping')
        return

    nxdommatches = 0
    resolvematches = 0

    for goodresponse in responses:
        if responses[goodresponse]["goodip"] == goodip:
            resolvematches += 1
        if responses[goodresponse]["nxdomain"] == gotnxdomain:
            nxdommatches += 1

    if resolvematches == 3 and nxdommatches == 3:
        logger.info(f'{server}: Provided valid response', extra={'msgC':c['green']})
        validServers.append(server)
        with open(resolversFile, 'a+') as fout:
            fout.writelines(server + '\n')
    else:
        logger.error(f'{server}: Invalid response received, rejected')

def main():
    global goodip

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input", help="File containing Public DNS Server",
        action="store", type=str, required=False, default=''
    )
    parser.add_argument(
        "-o", "--output", help="Output File to store validated DNS Servers",
        action="store", type=str, required=True
    )
    parser.add_argument(
        "-t", "--threads", help="Concurrent threads to run",
        action="store", type=int, required=False, default=2
    )

    args = parser.parse_args()

    ## Perform resolution on each of the 'baselines'
    for baseline in baselines:
        logger.info('Resolving baselines...', extra={'msgC':''})

        baseline_server = dict()
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [baseline]

        ## Check our baseline against this server
        try:
            goodanswer = resolver.resolve("bet365.com", 'A')
        except dns.exception.Timeout:
            logger.critical('DNS Timeout for baseline server')
            sys.exit(1)

        for rr in goodanswer:
            baseline_server["goodip"] = str(rr)
            goodip = str(rr)

        ## checks for often poisoned domains
        baseline_server["pos"] = dict()
        for positivebaseline in positivebaselines:
            posanswer = resolver.resolve(positivebaseline, 'A')
            for rr in posanswer:
                baseline_server["pos"][positivebaseline] = str(rr)

        try:
            nxdomanswer = resolver.resolve("dnsvalidator" + "bet365.com", 'A')
            baseline_server["nxdomain"] = False
        except dns.resolver.NXDOMAIN:
            baseline_server["nxdomain"] = True
        except dns.exception.Timeout:
            logger.critical('DNS Timeout for baseline server')
            sys.exit(1)

        responses[baseline] = baseline_server

    ## Fetch Public DNS Servers if INPUT is not provided
    if args.input:
        with open(args.input, 'r') as fin:
            servers = fin.read().splitlines()
    else:
        logger.info('No input provided, fetching nameservers from https://public-dns.info', extra={'msgC':''})

        http = urllib3.PoolManager()
        r = http.request('Get', 'https://public-dns.info/nameservers.txt')
        servers = r.data.decode().splitlines()
        filter = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        servers = [ip for ip in servers if filter.match(ip)]

    servers = np.array(servers)
    servers = list(servers[servers != ''])

    if os.path.exists(args.output):
        os.remove(args.output)

    ## Loop through the list
    with ThreadPoolExecutor(max_workers=int(args.threads)) as executor:
        for server in servers:
            executor.submit(resolve_address, server, args.output)

    logger.info(f'Finished. Discovered {len(validServers)} servers', extra={'msgC':c['purple']})

## Declare signal handler to immediately exit on KeyboardInterrupt
def signal_handler(signal, frame):
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    main()
