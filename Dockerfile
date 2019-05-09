ARG base_tag
FROM productize/kicad-automation-base:$base_tag
MAINTAINER Seppe Stas <seppe@productize.be>
LABEL Description="Minimal KiCad image with automation scripts; based on Ubuntu"

COPY src /usr/lib/python2.7/dist-packages/kicad-automation
