FROM alpine:3.8
MAINTAINER skyang

RUN apk update && apk add \
    musl \
    musl-utils \
    musl-dev \
    libc-utils \
    gcc \
    libffi-dev \
    py-setuptools \
    python2 \
    python2-dev \
    make \
    libxml2-dev \
    libxslt-dev \
    ca-certificates \
    linux-headers \
    nginx \
    memcached \
    curl \
    grep \
    supervisor \
    socat \
    py2-pip \
    bash \
    coreutils \
    libssh2 \
    libcurl \
    vim \
    ack \
    uwsgi-python \
    openssl \
    openssl-dev
RUN pip install --upgrade pip
RUN pip install falcon falcon-multipart falcon_cors lxml uwsgi requests pydocumentdb pbkdf2 pycrypto python-memcached PyJWT cerberus jmespath

WORKDIR /work
COPY api/ api
COPY controller.py /work/
COPY helper_files helper_files
COPY configs configs

COPY configs/uwsgi.ini /etc/uwsgi/vassals/controller_uwsgi.ini

COPY configs/uwsgi_params uwsgi_params
COPY configs/nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisord.conf

RUN mkdir /run/nginx && chown -R uwsgi.uwsgi /work
RUN touch /run/nginx.pid

COPY certs/server.crt /etc/nginx/controller.crt
COPY certs/server.key /etc/nginx/controller.key

RUN echo 'alias ll="ls -la"' >> ~/.bashrc
RUN echo 'alias nl="cd /var/log/nginx/"' >> ~/.bashrc


CMD [ "supervisord", "-c", "/etc/supervisord.conf" ]
