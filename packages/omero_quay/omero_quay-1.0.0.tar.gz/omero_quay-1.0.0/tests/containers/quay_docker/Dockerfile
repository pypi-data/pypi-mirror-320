FROM mambaorg/micromamba:bookworm

USER root
ARG CI_COMMIT_BRANCH
ENV CI_COMMIT_BRANCH=${CI_COMMIT_BRANCH}

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git
RUN adduser $MAMBA_USER users

USER $MAMBA_USER

RUN git clone -b $CI_COMMIT_BRANCH https://gitlab.in2p3.fr/fbi-data/omero-quay.git

WORKDIR omero-quay/
RUN git pull

RUN micromamba install -y -f environment.yml -n base && \
    micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1

RUN pip install --no-cache-dir -e .[dev]
COPY quay.yml /tmp/quay.yml
ENV QUAY_CONF=/tmp/quay.yml
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh"]
