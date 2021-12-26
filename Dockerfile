# syntax=docker/dockerfile:1.3-labs

FROM python:3.9.7-alpine3.14
LABEL MAINTAINER="Hoodly Twokeys <hoodlytwokeys@gmail.com>"

COPY . /DNSValidator
RUN <<eot
#!/bin/ash
apk add --upgrade --no-cache --virtual .deps build-base cmake
pip3 install --upgrade --no-cache pip setuptools wheel
pip3 install --no-cache-dir -r /DNSValidator/requirements.txt
apk del .deps
eot

WORKDIR /output
ENTRYPOINT [ "python3", "/DNSValidator/DNSValidator.py" ]
