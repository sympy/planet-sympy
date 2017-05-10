FROM ubuntu:14.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
        python-pip \
        python-libxml2 \
        openssh-client \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && pip install --upgrade setuptools pip \
    && hash -r \
    && pip install --no-cache-dir feedparser schedule

RUN groupadd -r swuser -g 433 && \
    mkdir /home/swuser && \
    useradd -u 431 -r -g swuser -d /home/swuser -s /sbin/nologin \
         -c "Docker image user" swuser && \
    chown -R swuser:swuser /home/swuser
WORKDIR /home/swuser

ADD sitecustomize.py /usr/lib/python2.7/sitecustomize.py
ADD planet planet
ADD update.sh update.sh
ADD scheduler.py scheduler.py
#ADD .git/refs/heads/master git_revision
RUN chown -R swuser:swuser planet update.sh scheduler.py

USER swuser

RUN mkdir testrun/

CMD ./scheduler.py
