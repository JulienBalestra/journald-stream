FROM debian:latest

ADD jds_kafka.py /opt/jds_kafka.py

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python &&
    apt-get install -y python-pip && \
    apt-get install -y libsystemd-dev && \
    apt-get install -y python-systemd  && \
    pip install --upgrade kafka-python && \
    apt-get clean autoclean && \
    apt-get autoremove -y


ENTRYPOINT ["/opt/jd_kafka.py"]



