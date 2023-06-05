FROM ubuntu:22.04

ARG UNAME=build
ARG UID=1000
ARG GID=1000

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC \
    apt-get install -y \
        sudo time git make curl wget subversion build-essential gcc file bc cpio gawk flex gettext unzip grep rsync pkg-config \
        openssl libssl-dev libncurses5-dev zlib1g-dev libwayland-dev libkf5config-dev-bin libkf5coreaddons-dev-bin \
        python3 python3-distutils \
        qttools5-dev qttools5-dev-tools qtdeclarative5-dev && \
    apt-get clean

VOLUME ["/ccache"]
VOLUME ["/downloads"]
VOLUME ["/src"]

ENV BR2_DL_DIR="/downloads"
ENV BR2_CCACHE_DIR="/ccache"

RUN groupadd -g $GID -o $UNAME && useradd -m -u $UID -g $GID -o -s /bin/bash $UNAME
USER $UNAME

WORKDIR /src

CMD ["/bin/bash"]