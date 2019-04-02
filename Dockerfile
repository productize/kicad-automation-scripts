FROM productize/kicad:4.0.7-18.04
MAINTAINER Seppe Stas <seppe@productize.be>
LABEL Description="Minimal KiCad image with automation scripts; based on Ubuntu"

ADD eeschema/requirements.txt .
RUN apt-get -y update && \
    apt-get install -y python python-pip xvfb recordmydesktop xdotool xclip && \
    pip install -r requirements.txt && \
    rm requirements.txt && \
    apt-get -y remove python-pip && \
    rm -rf /var/lib/apt/lists/*

ADD . /usr/lib/python2.7/dist-packages/kicad-automation
