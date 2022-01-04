""" __Doc__ File handle class """
from setuptools import find_packages, setup
from dnsvalidator.__version__ import __version__

setup(
    name="DNSValidator",
    version=__version__,
    url="https://github.com/frost19k/DNSValidator",
    license="GPLv3",
    description="Filters a list of IPv4 DNS Servers by verifying them against baseline servers.",
    author="Hoodly Twokeys",
    author_email="hoodlytwokeys@gmail.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': ['dnsvalidator=dnsvalidator.DNSValidator:main']
    },
    install_requires=open('requirements.txt').read().splitlines(),
    include_package_data=False,
    zip_safe=False
)
