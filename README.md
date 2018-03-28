KiCad automation scripts
========================

A bunch of scripts to automate [KiCad] processes.

This work is based in big parts on Scott Bezek's scripts in his
[split-flap display project][split-flap].
For more info see his [excellent blog posts][scot's blog].

Currently tested/working:

- Exporting schematics to PDF

To test:

```
docker run --rm -it -v `pwd`:/kicad-automation/ -v <kicad project>:/kicad-project -v <kicad library>:/kicad-library productize/kicad
export PRODUCTIZE_KICAD=/kicad-library # (for Productize projects)
/kicad-automation/eeschema/install-deps.sh
/kicad-automation/eeschema/export_schematic.py /kicad-project/<some-schematic>.sch
```

Challenges / improvements:

- Some files need other files to be viewed:
	- EESchema library (.lib) files + documentation (.dcm) files
	- EEschema schematic files require library cache files (-cache.lib)
- Linking to schematic sheets
- PCB layout layers

[KiCad]: http://kicad-pcb.org/
[split-flap]: https://github.com/scottbez1/splitflap
[scot's blog]: https://scottbezek.blogspot.be/2016/04/scripting-kicad-pcbnew-exports.html
