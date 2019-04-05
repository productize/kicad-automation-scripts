FROM productize/kicad:5.0.1-18.04
MAINTAINER Seppe Stas <seppe@productize.be>
LABEL Description="Minimal KiCad image with automation scripts; based on Ubuntu"

COPY eeschema/requirements.txt .
RUN apt-get -y update && \
    apt-get install -y python python-pip xvfb recordmydesktop xdotool xclip && \
    pip install -r requirements.txt && \
    rm requirements.txt && \
    apt-get -y remove python-pip && \
    rm -rf /var/lib/apt/lists/*

# Use a UTF-8 compatible LANG because KiCad 5 uses UTF-8 in the PCBNew title
# This causes a "failure in conversion from UTF8_STRING to ANSI_X3.4-1968" when
# attempting to look for the window name with xdotool.
ENV LANG C.UTF-8

COPY . /usr/lib/python2.7/dist-packages/kicad-automation

# Copy default configuration and fp_lib_table to prevent first run dialog
COPY ./config/* /root/.config/kicad/
