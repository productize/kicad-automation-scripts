KiCad automation scripts
========================

A bunch of scripts to automate [KiCad] processes using a combination of the
KiCAD Python library and UI automation with [xdotool].

This work is based in big parts on Scott Bezek's scripts in his
[split-flap display project][split-flap].
For more info see his [excellent blog posts][scot's blog].

Currently tested and working:

- Exporting schematics to PDF and SVG
- Exporting layouts to PDF and SVG
- Running ERC on schematics

## Instalation

# Using Docker

Build the docker image and run it:

```
docker build -t kicad-automation .
docker run --rm -it -v <path to a kicad project>/kicad-project -v`pwd`:/kicad-automation-scriptskicad-automation-scripts
```

Or fetch it from [Dockerhub]:

```
docker run --rm -it -v <path to a kicad project>/kicad-project productize/kicad-automation-scripts
```

# Installation on your own machine:

If you want to use these scripts directly on your system, you should be able to
get it to work by installing the folowing dependencies:

This tool has the folowing dependencies:
- KiCad
- python
- python-pip
- xvfb
- recordmydesktop
- xdotool
- xclip

The Python dependencies (excluding KiCad) are listed in
[eeschema/requirements.txt][eeschema/requirements.txt] an can be installed with

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

### Export a schematic to PDF or SVG

```
python -m kicad-automation.eeschema.schematic export /kicad-project/<some-schematic>.sch <build_dir> <svg or pdf> <all-pages (True or False)>
```

### Run ERC:

```
python -m kicad-automation.eeschema.schematic run_erc /kicad-project/<some-schematic>.sch <build_dir> <svg or pdf> <all-pages (True or False)>
```

[KiCad]: http://kicad-pcb.org/
[xdotool]: https://github.com/jordansissel/xdotool
[split-flap]: https://github.com/scottbez1/splitflap
[scot's blog]: https://scottbezek.blogspot.be/2016/04/scripting-kicad-pcbnew-exports.html
[Dockerhub]: https://hub.docker.com/r/productize/kicad-automation-scripts
