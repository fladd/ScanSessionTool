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
### Using pipx (recommended)
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

### Using pip
1. Make sure [Python 3](https://python.org) (>=3.6; with Tkinter) is installed.

2. Install Scan Session Tool:

   ```
   python3 -m pip install ScanSessionTool
   ```
(On Windows you might need to replace `python3` with `py -3`).

Usage
-----

Scan Session Tool can be started with the command `scansessiontool`.

Documentation
-------------
The full documentation can be found from within the programme, by clicking on
the "?" button, or by selecting "Scan Session Tool Help" from the Help menu,
as well as at https://fladd.github.io/ScanSessionTool/.

Automated tests
---------------
Core functionality of Scan Session Tool can be tested automatically.
To do so, first install all dependencies:
```
python -m pip install -r requirements.txt`
```

Then, run tests from this directory:
```
python -m unittest -v
```

Contributing
------------
We very much welcome contributions to Scan Session Tool, and there are multiple ways to contribute. Contributions are always handled transparently through the public GitHub interface.

### Bug reports
If you encounter bugs or incorrect/unexpected behaviour of Scan Session Tool, please consider creating an [issue](https://github.com/fladd/ScanSessionTool/issues) here on GitHub for it. You can read more about how to do this [here](https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-an-issue). When reporting issues, make sure to report (1) what you were trying to do, (2) what the expected outcome should have been, (3) what the observed outcome is, and (4) how to replicate this behaviour.

### Code contributions
We work with the standard [GitHub forking workflow](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) and appreciate code contributions in that way. Individuals that have contributed code will be named with their contributions on this page.

#### Bug fixes
To implement bug fixes, please
1. [fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) the [main branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches) of this repository
2. [commit](https://docs.github.com/en/pull-requests/committing-changes-to-your-project) your changes (potentially in a [new branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches))
3. [test](https://github.com/fladd/ScanSessionTool/tree/master/tests) you changes
4. [create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) and reference the corresponding GitHub [issue](https://github.com/fladd/ScanSessionTool/issues), if applicable
   
#### New features
Before implementing a new feature, we would encourage you to first discuss the planned feature with us, either in the [issue tracker](https://github.com/fladd/ScanSessionTool/issues), or [GitHub discussions](https://github.com/fladd/ScanSessionTool/discussions). Once discussed, new features can then be implemented the same way as bug fixes.

Contributors
------------
- Florian Krause (main developer)
- Nikos Kogias (co-developer)
