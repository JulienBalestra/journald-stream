FROM debian:latest

ADD jds_kafka.py /opt/jds_kafka.py
ADD PY_SD_API /opt/python-systemd

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python python-pip && \
    apt-get install -y libsystemd-dev git pkgconf && \
    git clone https://github.com/systemd/python-systemd.git $PY_SD_API && \
    cd $PY_SD_API && make && make install && \
    pip install --upgrade kafka-python && \
    apt-get clean autoclean && \
    apt-get autoremove -y


ENTRYPOINT ["/opt/jd_kafka.py"]



