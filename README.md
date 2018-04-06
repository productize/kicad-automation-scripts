KiCad automation scripts
========================

A bunch of scripts to automate [KiCad] processes.

This work is based in big parts on Scott Bezek's scripts in his
[split-flap display project][split-flap].
For more info see his [excellent blog posts][scot's blog].

Currently tested/working:

- Exporting schematics to PDF

## Getting started

First, build the [Docker image with KiCad][docker-kicad]:

```
git clone https://github.com/productize/docker-kicad.git
docker build -t productize/kicad docker-kicad
```

Then, launch the image with `<kicad project>` pointing to a KiCad project on
your filesystem:

```
cd docker-automation-scripts    # So that `pwd` can retrieve the path
docker run --rm -it -v `pwd`:/kicad-automation/ -v <kicad project>:/kicad-project productize/kicad
```

Once the image is launched, run automation scripts inside it:

```
/kicad-automation/eeschema/install-deps.sh
/kicad-automation/eeschema/export_schematic.py /kicad-project/<some-schematic>.sch
```

To use external libraries (e.g. when the `<some schematic>-cache.lib` file is
not present or incomplete), run the image with `<kicad library>` pointing to a
directory with KiCad libraries on your filesystem:

```
docker run --rm -it -v `pwd`:/kicad-automation/ -v <kicad project>:/kicad-project -v <kicad library>:/kicad-library productize/kicad

export PRODUCTIZE_KICAD=/kicad-library # (for Productize projects)
/kicad-automation/eeschema/install-deps.sh
/kicad-automation/eeschema/export_schematic.py /kicad-project/<some-schematic>.sch
```

## Challenges / improvements:

- Some files need other files to be viewed:
	- EESchema library (.lib) files + documentation (.dcm) files
	- EEschema schematic files require library cache files (-cache.lib)
- Linking to schematic sheets
- PCB layout layers

[KiCad]: http://kicad-pcb.org/
[split-flap]: https://github.com/scottbez1/splitflap
[scot's blog]: https://scottbezek.blogspot.be/2016/04/scripting-kicad-pcbnew-exports.html
[docker-kicad]: https://github.com/productize/docker-kicad
