KiCad automation scripts
========================

A bunch of scripts to automate [KiCad] processes using a combination of the
PCBNew Python library and UI automation with [xdotool].

This work is based in big parts on Scott Bezek's scripts in his
[split-flap display project][split-flap].
For more info see his [excellent blog posts][scot's blog].

Currently tested and working:

- Exporting schematics to PDF and SVG
- Exporting layouts to PDF and SVG
- Running ERC on schematics
- Running DRC on layouts

## Versions

This repository has a branch per supported major KiCad version, prefixed with
`kicad-`. Note that installation instructions and supported features can be
different per version.

The master branch and latest Docker tag will always be the latest supported
stable KiCad version.

## Installation

### Using Docker

Build and run the docker image:

```
docker build -t kicad-automation-scripts .
docker run --rm -it -v <path to a kicad project>:/kicad-project kicad-automation-scripts
```

Or fetch it from [Dockerhub]:

```
docker run --rm -it -v <path to a kicad project>:/kicad-project productize/kicad-automation-scripts
```

### Installation on your own machine:

If you want to use these scripts directly on your system, you should be able to
get it to work by installing the folowing dependencies:

This tool has the following dependencies:
- KiCad
- python
- python-pip
- xvfb
- recordmydesktop
- xdotool
- xclip

The Python dependencies (excluding KiCad) are listed in
[eeschema/requirements.txt][eeschema/requirements.txt] and can be installed with

```
pip install -r eeschema/requirements.txt
```

### Installation on Ubuntu/Debian:

```
sudo apt-get install -y kicad python python-pip xvfb recordmydesktop xdotool xclip
```

## Usage

In the Docker image or on a system with all required dependencies installed you
can use the following commands:

### Run schematic ERC:

```
python -m kicad-automation.eeschema.schematic run_erc /kicad-project/<some-schematic>.sch <build_dir> <svg or pdf> <all-pages (True or False)>
```

### Export a schematic to PDF or SVG

```
python -m kicad-automation.eeschema.schematic export /kicad-project/<some-schematic>.sch <build_dir> <svg or pdf> <all-pages (True or False)>
```

### Run layout DRC:

```
python -m kicad-automation.pcbnew_automation.run_drc /kicad-project/<some-layout>.kicad_pcb <build_dir>
```

### Generate a zip file with gerber files for PCB manufacuring:

```
python -m kicad-automation.pcbnew_automation.plot /kicad-project/<some-layout>.kicad_pcb <plot_dir> [<layers to plot>]
```

### Generate a pdf with the layout layers and drill map file:

```
python -m kicad-automation.pcbnew_automation.plot -f pdf /kicad-project/<some-layout>.kicad_pcb <plot_dir> [<layers to plot>]
```

## Hacking

If you want to test the scripts in this repository and run them inside a docker
image, the base image can be used. This base image contains all the required
dependencies and the required environment for the script to work.

To build and run the base image:

```
docker build -f Dockerfile-base -t kicad-automation-base .
docker run --rm -it -v <path to a kicad project>/kicad-project  -v `pwd`/src:/usr/lib/python2.7/dist-packages/kicad-automation kicad-automation-base
```

Or fetch it from [Dockerhub]:

```
docker run --rm -it -v <path to a kicad project>:/kicad-project -v `pwd`/src:/usr/lib/python2.7/dist-packages/kicad-automation productize/kicad-automation-base
```

The scripts can now be used the same way as in the main image, but changes
on the host will automatically be reflected on the container (though note
that Python does not autoreload libraries).

[KiCad]: http://kicad-pcb.org/
[xdotool]: https://github.com/jordansissel/xdotool
[split-flap]: https://github.com/scottbez1/splitflap
[scot's blog]: https://scottbezek.blogspot.be/2016/04/scripting-kicad-pcbnew-exports.html
[Dockerhub]: https://hub.docker.com/r/productize/kicad-automation-scripts
