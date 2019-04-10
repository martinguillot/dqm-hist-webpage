# Webpages from DQM Histograms
Script to dump histograms from DQM RelVal datasets on a webpage.

## Requirements

The following Python packages need to be installed on your system:

* [numpy](https://github.com/numpy/numpy)
* [matplotlib](https://github.com/matplotlib/matplotlib)
* [uproot](https://github.com/scikit-hep/uproot)
* [uproot-methods](https://github.com/scikit-hep/uproot-methods)

All of them are avalable on the Python Package Index (PyPI) and can be installed with [pip](https://pypi.org/project/pip/). All requirements are also available in the CMSSW environment.

## Installation

Clone this repository and change in the directory to get ready to go:

```bash
git clone https://github.com/guitargeek/dqm-hist-webpage.git
cd dqm-hist-webpage
```

## Instructions

Le't use this script to generate a website to validate the electron reconstruction in Monte Carlo samples as an example.
You can run the `python dqm-hist-webpage.py --help` to get some guidance:

```
usage: dqm-hist-webpage.py [-h] [--title TITLE] [--target-title TARGET_TITLE]
                           [--reference-title REFERENCE_TITLE]
                           [--plot-directory PLOT_DIRECTORY]
                           [--website WEBSITE] [--website-only]
                           target reference specification

positional arguments:
  target                ROOT DQM file for target
  reference             ROOT DQM file for reference
  specification         text file with histogram specification

optional arguments:
  -h, --help            show this help message and exit
  --title TITLE         title of the validation website
  --target-title TARGET_TITLE
                        title of the target datasest
  --reference-title REFERENCE_TITLE
                        title of the reference dataset
  --plot-directory PLOT_DIRECTORY
                        output directory (./plots/ by default)
  --website WEBSITE     path of the website HTML file
  --website-only        to generate webpage only
```

As the `positional arguments` section indicates, you need to provide at the very least a __target__ and a __reference__ DQM file, as well as a __text file to specify which histograms__ end up on the website and how they will be ordered.

You can download example DQM files for [target](https://rembserj.web.cern.ch/rembserj/data/github/guitargeek/dqm-hist-webpage/zee_target.root) and [reference](https://rembserj.web.cern.ch/rembserj/data/github/guitargeek/dqm-hist-webpage/zee_reference.root) here in order to run the example yourself. Place the DQM files in the current directory and run the script with the following arguments:

```bash
python dqm-hist-webpage.py zee_target.root zee_reference.root specifications/electron_mc_signal_histos.txt 
```
The histogram specification file is [included in this repository](specifications).

You should now have a file `index.html` in your current directory, as well as a directory `plots/` where all the plots are stored. These are default names which can be changed by command line arguments.

The website can be opened with a browser directly, or copied on a webserver together with the directory containing the plots.

If you want to produce the website again but already have the plots, use the `--website-only` argument to save some time.

### Advice for LLR CMS group members

Use the `/scratch` area on the `llruicms01` machine to do this work. Producing all plots will be 10 times faster than on `lxplus` thanks to the sweet [SSD](https://en.wikipedia.org/wiki/Solid-state_drive).

## The Histogram Specification File

Let's look at a few lines from the aforementioned histogram specification file:

```
# Comparison with MC truth (residuals)

DQMData/Run 1/EgammaV/Run summary/ElectronMcSignalValidator/h_ele_ChargeMnChargeTrue

DQMData/Run 1/EgammaV/Run summary/ElectronMcSignalValidator/h_ele_PoPtrue
DQMData/Run 1/EgammaV/Run summary/ElectronMcSignalValidator/h_ele_PoPtrue_barrel
DQMData/Run 1/EgammaV/Run summary/ElectronMcSignalValidator/h_ele_PoPtrue_endcaps

DQMData/Run 1/EgammaV/Run summary/ElectronMcSignalValidator/h_ele_PoPtrue_golden_barrel
DQMData/Run 1/EgammaV/Run summary/ElectronMcSignalValidator/h_ele_PoPtrue_golden_endcaps
```

This snippet showcases what can be specified:

* section names starting with a "hashtag" (`#`) like in markdown
* the location of the histogram in the DQM ROOT files
* start a new row in the website tabular structure by inserting an empty line between histograms

## Developer Notes

This script was written in summer 2018, when uproot did not support TProfiles yet. Therefore, this script extends uproot with the file `uproot_exts.py` to implement the missing TProfile member functions. It could be possible that gets obsolete some day or that the code breaks, as uproot-methods might implement the TProfile functionality itself. As of April 2019, the custom implementations still work.
