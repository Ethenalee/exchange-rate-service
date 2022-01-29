FROM python:3.9.6-alpine

WORKDIR /srv/root

RUN apk --update add bash \
    zip \
    openssl \
    openssh \
    python3-dev \
    curl \
    curl-dev \
    libffi-dev \
    make \
    gcc \
    g++ \
    git \
    linux-headers \
    musl-dev \
    pcre-dev \
    libpq \
    postgresql-dev \
    postgresql-client \
    zlib-dev && \
    python -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip

COPY ./requirements/requirements.txt ./

RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    rm -r /root/.cache && \
    mkdir -p /srv/root

# get the db tooling
RUN wget https://github.com/golang-migrate/migrate/releases/download/v4.14.1/migrate.linux-amd64.tar.gz && \
    tar zxvf migrate.linux-amd64.tar.gz && \
    mv migrate.linux-amd64 /usr/local/bin/go-migrate && \
    chmod u+x /usr/local/bin/go-migrate && \
    rm migrate.linux-amd64.tar.gz

# cleanup some tooling
RUN apk del gcc linux-headers musl-dev make libffi-dev g++ git


# Add Scripts
COPY scripts/ /scripts
RUN chmod 755 /scripts/*

# little easier to manage db setup
RUN ln -s /scripts/setup-db /usr/local/bin/setup-db

# copy in code
COPY mount/ /srv/root/

CMD ["/scripts/start.sh"]
