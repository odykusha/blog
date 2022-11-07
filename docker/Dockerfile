FROM python:3.10-slim

#ENV DEBIAN_FRONTEND=noninteractive
#ENV DEBCONF_NONINTERACTIVE_SEEN=true

COPY . /opt/
RUN apt-get update --no-install-recommends && apt-get install -y apt-utils \
    software-properties-common --no-install-recommends  \
    && apt-get install -y `grep -v '#' /opt/packages.txt | xargs` --no-install-recommends  \
    && apt-get autoremove -y && apt-get purge -y --auto-remove && rm -rf /var/lib/apt/lists/*

#

#ADD https://bootstrap.pypa.io/get-pip.py /opt/get-pip.py
#RUN python3.7 /opt/get-pip.py


RUN ln -sf /usr/share/zoneinfo/Europe/Kiev /etc/localtime && locale-gen en_US.UTF-8 ru_RU.UTF-8 ru_UA.UTF-8

RUN python3.10 -m pip install -U -r /opt/requirements.txt --upgrade

RUN useradd qauser --shell /bin/bash --create-home \
  && usermod -a -G sudo qauser \
  && echo 'ALL ALL = (ALL) NOPASSWD: ALL' >> /etc/sudoers \
  && echo 'qauser:secret' | chpasswd
ENV HOME=/home/qauser
USER qauser

WORKDIR /work
