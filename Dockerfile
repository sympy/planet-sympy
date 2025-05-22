FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LC_CTYPE=C.UTF-8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        openssh-client \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && pip3 install --upgrade setuptools pip \
    && pip3 install --no-cache-dir feedparser schedule requests

RUN groupadd -r swuser -g 433 && \
    mkdir /home/swuser && \
    useradd -u 431 -r -g swuser -d /home/swuser -s /sbin/nologin \
         -c "Docker image user" swuser && \
    chown -R swuser:swuser /home/swuser
WORKDIR /home/swuser

ADD config config
ADD static static
ADD planet.py planet.py
RUN chmod +x planet.py && \
    chown -R swuser:swuser config static planet.py

USER swuser

CMD ["python3", "./planet.py", "scheduler"]