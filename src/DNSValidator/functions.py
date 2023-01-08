import sys
import string
import random
import logging
import dns.resolver

import pathlib as pl

from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, wait

from .environment import baselinechecks, baselinesrvs
from .CustomLogger import colors as c

##->> Configure logging
logger = logging.getLogger('DNSValidator')

##->> Random string of length
def get_rand_str(lng: int) -> str:
    return ''.join(random.choice(string.ascii_lowercase) for i in range(lng))

##->> Get known_good_dns_servers
def get_baselines(rootDom: str, servers: Optional[List[str]]=baselinesrvs, checks: Optional[List[str]]=baselinechecks) -> dict:
    logger.info(f'Checking baseline servers...', extra={'msgC':''})

    baselines = dict()
    for server in servers:
        baselines[server] = list()
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [server]

        for target in checks:
            d = dict()

            try:
                rans = resolver.resolve(target, 'A')
            except dns.exception.Timeout:
                if not quiet: logger.error(f'Baseline server timeout {server}')
                continue

            for rr in rans:
                d['ipaddr'] = str(rr)

            try:
                nxans = resolver.resolve(f'{get_rand_str(10)}.{target}', 'A')
                d['nxdomain'] = False
            except dns.resolver.NXDOMAIN:
                d['nxdomain'] = True
            except dns.exception.Timeout:
                if not quiet: logger.error(f'Baseline server timeout {server}')
                continue

            baselines[server].append({ target: d })

    ipset = set([ baselines[key][0][rootDom]['ipaddr'] for key in baselines.keys() ])
    nxset = set([ baselines[key][0][rootDom]['nxdomain'] for key in baselines.keys() ])

    try:
        assert ( len(ipset) == 1 ) and ( len(nxset) == 1 ) and ( list(nxset)[0] == True )
        return baselines, list(ipset)[0]

    except AssertionError as e:
        logger.critical(f'Failed to validate baseline responses')
        sys.exit(1)

def check_server(server: str, rootDom: str) -> str:
    from .environment import nxdomainchecks
    srvstr = f'{c["cyan"]}{server}{c["reset"]}'

    if not quiet: logger.info(f'Checking server {srvstr}', extra={'msgC':''})
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [server]

    ##->> Validate the server
    nxstr = get_rand_str(10)

    #-> Validate NXDOMAIN checks
    for nxdomain in nxdomainchecks:
        try:
            q = f'{nxstr}.{nxdomain}'
            a = resolver.resolve(q, 'A')
            #-> NXDomain Exception was not returned, we got records when we shouldn't have.
            #-> Skip the server.
            logger.warning(f'DNS poisoning detected, skipping server {srvstr}')
            return
        except dns.resolver.NXDOMAIN:
            pass
        except Exception as e:
            if not quiet: logger.error(f'Error checking DNS Poisoning on server {srvstr}')
            if verbose: logger.info(f'{" ".join(str(e).split())}', extra={'msgC':''})
            return

    #-> Validate IP Address check
    # Make sure NXDOMAIN is returned on root-domain
    try:
        q = f'{nxstr}.{rootDom}'
        rans = resolver.resolve(q, 'A')
    except dns.resolver.NXDOMAIN:
        pass
    except dns.exception.Timeout:
        if not quiet: logger.error(f'IP Address validation timeout on server {srvstr}')
        return
    except Exception as e:
        if not quiet: logger.error(f'Error validating server {srvstr}')
        if verbose: logger.debug(f'{" ".join(str(e).split())}')
        return

    # Make sure root-domain IP is the same as trusted-servers
    try:
        q = f'{rootDom}'
        rans = resolver.resolve(q, 'A')
        try:
            assert [str(rr) for rr in rans][0] == goodip
            logger.info(f'Successfully validated server {srvstr}', extra={'msgC':c["green"]})
            return server
        except AssertionError as e:
            if not quiet: logger.error(f'Invalid response, skipping server {srvstr}')
            return
    except dns.exception.Timeout:
        if not quiet: logger.error(f'IP Address validation timeout on server {srvstr}')
        return
    except Exception as e:
        if not quiet: logger.error(f'Error validating server {srvstr}')
        if verbose: logger.debug(f'{" ".join(str(e).split())}')
        return

def run(servers: List[str], workers: int, rootDom: str, fileName: str, vocal: bool=False, silent: bool=False) -> None:
    global quiet
    global verbose
    global goodip

    quiet = silent
    verbose = vocal

    _, goodip = get_baselines(rootDom)

    futures = list()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for server in servers:
            future = executor.submit(check_server, server, rootDom)
            futures.append(future)

    futures, _ = wait(futures)

    validServers = list()
    for future in futures:
        validServers.append(future.result())

    validServers = list(filter(lambda x: x != None, validServers))
    if validServers:
        logger.info(f'[{c["green"]}Done{c["reset"]}] found {c["cyan"]}{len(validServers)}{c["reset"]} valid servers', extra={'msgC':''})
        with pl.Path(fileName).open('w') as fout:
            for server in validServers:
                fout.write(f'{server}\n')
    else:
        logger.critical(f'[{c["red"]}Error{c["reset"]}] found {c["bred"]}0{c["reset"]} valid servers')
