Scan Session Tool
=================

About
-----
There is an urgent need to improve the reproducibility of (functional) MRI
research through transparent reporting, but standardization in this domain is
currently lacking. Shared MR images are often only made available after
transformation into a derivative data format (e.g.
[BIDS](https://bids.neuroimaging.io/)), and scan session documentation is
commonly either manually implemented (e.g. with hand written notes) or
neglected entirely.

Scan Session Tool was written to fill this gap, and to be used by
neuroscientists, to help them increase transparency and reproducibilty of their
MRI research by standardizing scan session documentation and raw data
archiving.

Scan Session Tool is a graphical application for documenting (f)MRI scan
sessions and automatized data archiving. Information about the scan session
itself, used forms and documents, as well as the single measurements can be
entered and saved into a protocol file. This information can furthermore be
used to copy acquired data (DICOM images as well as optional stimulation
protocols and logfiles into a specific hierarchical folder structure for
unified archiving purposes, with optional sepcial support for
[(Turbo-)BrainVoyager](https://brainvoyager.com).


Installation
------------
1. Make sure [Python 3](https://python.org) (>=3.6; with Tkinter) is installed.

2. Install pipx:

    ```
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    ```
(On Windows you might need to replace `python3` with `py -3`).

3. Install Scan Session Tool:

    ```
    pipx install ScanSessionTool
    ```

Usage
-----

Scan Session Tool can be started with the command `scansessiontool`.

Documentation
-------------
The full documentation can be found from within the programme, by clicking on
the "?" button, or by selecting "Scan Session Tool Help" from the Help menu,
as well as at https://fladd.github.io/ScanSessionTool/.
