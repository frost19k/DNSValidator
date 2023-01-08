# syntax=docker/dockerfile:1.4

FROM python:3.10-slim AS base

ARG wrkdir="/tmp/dnsvalidator"

COPY . ${wrkdir}/

RUN <<eot
cd ${wrkdir}
pip3 install --no-cache-dir -U pip wheel setuptools
pip3 install --no-cache-dir -r requirements.txt
pip3 install --no-cache-dir .
rm -rf ${wrkdir}
eot

WORKDIR /output
ENTRYPOINT [ "dnsvalidator" ]
CMD [ "--help" ]
