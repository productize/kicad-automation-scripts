FROM productize/kicad
MAINTAINER Seppe Stas <seppe@productize.be>
LABEL Description="Minimal KiCad image with automation scripts; based on Ubuntu"

ADD eeschema/requirements.txt .
RUN apt-get -y update && \
    apt-get install -y python3 python3-pip xvfb recordmydesktop xdotool && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install -r requirements.txt && \
    rm requirements.txt

ADD . /kicad-automation
