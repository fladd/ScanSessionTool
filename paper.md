---
title: 'Scan Session Tool: (f)MRI scan session documentation and archiving'
tags:
  - Python
  - neuroscience
  - MRI
  - research documentation
  - data archiving
authors:
  - name: Florian Krause
    orcid: 0000-0002-2754-3692
    affiliation: "1"
  - name: Nikos Kogias
    affiliation: 1
affiliations:
 - name: Donders Institute for Brain, Cognition and Behaviour, RadboudUMC, Nijmegen, The Netherlands
   index: 1
date: 31 January 2023
bibliography: paper.bib
---

# Summary

TODO: Short intro?

Scan Session Tool is a cross-platform (Windows, MacOS, Linux) graphical
application for standardized real-time documentation of (functional) Magnetic
Resonance Imaging (MRI) scan sessions and automatized archiving of the collected
(raw) data. The software allows session information (i.e. metadata, project- and
subject-specific notes/documents, as well as a detailed log of acquired MRI
measurements) to be entered in a fast and convenient way during a session and to
be saved into a human- and machine-readable protocol file (in YAML format).
The software then uses this scan session documentation to automatically organize
the raw data (i.e. DICOM images) of all acquired measurements, as well as any
related logfiles (e.g. stimulation protocols, response time recordings, etc.)
into a unified hierarchical folder structure for archiving purposes.
In addition, the software has (optional) sepcial support for BrainVoyager and
(Turbo-)BrainVoyager (which is commonly used for real-time functional MRI
measurements).


# Statement of need
TODO: Problem description

Scan Session Tool was written to be used by neuroscientists, to help them
increase transparency and reproducibilty of their MRI research by standardizing
scan session documentation and raw data archiving. The software has already
been succesfully used during data collection of recent MRI studies (e.g.
`@krause:2019`; `@krause:2021`),
and its standardized scan session documentation as well as arhiving structure
are already part of open datasets (e.g. REF). The archiving structure is
furthermore automatically recognized by BIDScoin (REF), which allows the raw
DICOM data archived with Scan Session Tool to be further converted to the
Brain Imaging Data Structure (BIDS, REF) if desired.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# References
