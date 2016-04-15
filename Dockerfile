FROM ubuntu:14.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
        python-pip \
        python-libxml2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && pip install --upgrade setuptools pip \
    && hash -r \
    && pip install --no-cache-dir feedparser

ADD planet planet
ADD update.sh update.sh
RUN mkdir testrun/
RUN ./update.sh
