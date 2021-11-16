# syntax=docker/dockerfile:1.2

FROM python:3.9.7-alpine3.14
LABEL MAINTAINER="Hoodly Twokeys <hoodlytwokeys@gmail.com>"

WORKDIR /app
COPY . .
RUN apk add --no-cache --virtual .deps build-base && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .deps

ENTRYPOINT [ "python", "DNSValidator.py" ]
