import re

##->> IPv4 regex
regex = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)[.]){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')

##->> Baseline server whsoe answer we trust
baselinesrvs = [
    '1.1.1.1', #-> OpenDNS
    '8.8.8.8', #-> Google
    '9.9.9.9', #-> Quad9
]


##->> Baseline domains to validate against
baselinechecks = [
    'bet365.com',
    'telegram.com'
]

##->> Domains to check form DNS Poisoning
nxdomainchecks = [
    'facebook.com',
    'google.com',
    'microsoft.com'
]
