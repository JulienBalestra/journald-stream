FROM debian:latest

ENV JDS="/opt/jds_kafka.py"
ADD jds_kafka.py $JDS

ADD entrypoint.sh /entrypoint.sh

ARG PY_SD_API=/opt/python-systemd
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python python-pip python-dev && \
    apt-get install -y libsystemd-dev git pkgconf && \
    git clone https://github.com/systemd/python-systemd.git $PY_SD_API && \
    cd $PY_SD_API && make && make install && cd /tmp && \
    pip install --upgrade kafka-python && \
    apt-get clean autoclean && \
    apt-get autoremove -y && rm -Rf $PY_SD_API


ENTRYPOINT ["/entrypoint.sh"]



