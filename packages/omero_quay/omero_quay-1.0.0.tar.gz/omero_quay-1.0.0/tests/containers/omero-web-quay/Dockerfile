FROM ubuntu:22.04

ENV LANG="en_US.utf-8"
ENV DEBIAN_FRONTEND="noninteractive"

ARG CI_COMMIT_BRANCH
ENV CI_COMMIT_BRANCH=${CI_COMMIT_BRANCH}


RUN mkdir /opt/setup
WORKDIR /opt/setup
ADD playbook.yml requirements.yml /opt/setup/

RUN apt update



RUN apt install -y \
    apt-utils\
    unzip\
    wget\
    build-essential\
    bc\
    ansible\
    sudo\
    ca-certificates\
    dumb-init\
    libbz2-dev\
    libssl-dev\
    curl\
    zeroc-ice-utils\
    && ansible-galaxy install -p /opt/setup/roles -r requirements.yml \
    && apt autoclean -y \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/*

RUN curl -fsSL https://deb.nodesource.com/setup_23.x -o nodesource_setup.sh
RUN chmod u+x ./nodesource_setup.sh
RUN ./nodesource_setup.sh

RUN apt-get install -y nodejs

RUN npm install -g n
#RUN npm audit fix
#RUN npm install
#RUN ./node_modules/webpack/bin/webpack.js --mode production

ENV OMERODIR=/opt/omero/web/OMERO.web/
RUN ansible-playbook playbook.yml \
    && apt -y autoclean \
    && apt -y autoremove \
    && rm -rf /var/lib/apt/lists/* /tmp/*

ADD entrypoint.sh /usr/local/bin/
RUN rm -rf /startup/*
ADD 50-config.py 60-default-web-config.sh 98-cleanprevious.sh 99-run.sh /startup/
RUN chmod -R 755 /startup
ADD ice.config /opt/omero/web/OMERO.web/etc/

USER root
ENV ICE_CONFIG=/opt/omero/web/OMERO.web/etc/ice.config



#RUN pip install wheel
RUN /opt/omero/web/venv3/bin/pip install \
    wheel \
    omero-figure \
    omero-iviewer \
    omero-fpbioimage \
    omero-mapr \
    #omero-parade \
    omero-autotag \
    omero-tagsearch \
    omero-weberror \
    python-irodsclient \
    whitenoise \
    pytest \
    pytest-mock \
    pyyaml \
    tables \
    # parade-crossfilter\
    pytest-django

# Add custom OMERO parade 
RUN wget -O /tmp/omero-parade.zip https://codeload.github.com/mmongy/omero-parade/zip/refs/heads/master
RUN unzip /tmp/omero-parade.zip -d /tmp
RUN mv /tmp/omero-parade-master /tmp/omero-parade
WORKDIR /tmp/omero-parade
RUN ls -al
RUN /opt/omero/web/venv3/bin/pip install .

# Add OMERO frontend elements
COPY ./images /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/webclient/static/webclient/image/
COPY ./style/ome.login.css /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/webgateway/static/webgateway/css/ome.login.css
COPY ./style/login.html /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/webclient/templates/webclient/login.html


# Add custom omero-quay
RUN wget -O /tmp/omero-quay.zip https://gitlab.in2p3.fr/fbi-data/omero-quay/-/archive/${CI_COMMIT_BRANCH:-validate_excel}/omero-quay-${CI_COMMIT_BRANCH:-validate_excel}.zip
RUN unzip /tmp/omero-quay.zip -d /tmp
RUN mv /tmp/omero-quay-${CI_COMMIT_BRANCH:-validate_excel} /tmp/omero-quay
WORKDIR /tmp/omero-quay
RUN ls -al
RUN /opt/omero/web/venv3/bin/pip install -e .[server]

ADD 01-default-webapps.omero /opt/omero/web/config/

USER omero-web
ENV ICE_CONFIG=/opt/omero/web/OMERO.web/etc/ice.config

EXPOSE 4080
VOLUME ["/opt/omero/web/OMERO.web/var"]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
