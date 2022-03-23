# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM python:latest

LABEL Name=dev_chat Version=0.0.1

WORKDIR /dev_chat
#ADD . /
COPY requirements.txt /dev_chat/


RUN apt-get install libpq-dev
# Using pip:
RUN pip install -r requirements.txt
