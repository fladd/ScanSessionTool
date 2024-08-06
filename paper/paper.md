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
    orcid: 0000-0002-9692-1503
    affiliation: 1
affiliations:
 - name: Donders Institute for Brain, Cognition and Behaviour, RadboudUMC, Nijmegen, The Netherlands
   index: 1
date: 31 January 2023
bibliography: paper.bib
---

# Summary

Scan Session Tool is a cross-platform (Windows, MacOS, Linux) graphical
application for standardised real-time documentation of (functional) Magnetic
Resonance Imaging (MRI) scan sessions and automatised archiving of the
collected (raw) data. The software allows session information (i.e. metadata,
project- and subject-specific notes/documents, as well as a detailed log of
acquired MRI measurements) to be entered in a fast and convenient way during a
session (see also \autoref{fig:Figure1}) and to be saved into a human- and
machine-readable protocol file (in YAML format) that facilitates both sharing
with other researchers and integration into automatised procedures.
Scan Session Tool can furthermore use this scan session documentation itself to
automatically organise the raw data (i.e. DICOM images) of all acquired
measurements, as well as any related logfiles (e.g. stimulation protocols,
response time recordings, etc.) into a unified hierarchical folder structure for
archiving purposes (see also \autoref{fig:Figure2}).
In addition, the software has (optional) special support for BrainVoyager and
(Turbo-)BrainVoyager (which is commonly used for real-time functional MRI
measurements). This entails the creation of links to DICOM images using 
dedicated filename conventions (BrainVoyager and Turbo-BrainVoyager) as well as 
adapting references to files and data to reflect the archived folder structure 
(Turbo-BrainVoyager).


# Statement of need

There is an urgent need to improve the reproducibility of (functional) MRI
research through transparent reporting [@noauthor_fostering_2017]. Despite
large agreement among researchers on the importance of openly sharing not only
collected raw data (i.e. MR images and related behavioural/physiological
recordings) and their analysis [@nichols_best_2017], but also the detailed
documentation of the data collection process [i.e. notes and data about the
scan sessions themselves, @borghi_data_2018; @glover_function_2012],
standardisation in this domain is currently lacking. Most current approaches 
focus on automatised reproducible analysis (e.g. https://github.com/ReproNim), 
and shared MR images often only made available after transformation into a 
derivative data format, such as the Brain Imaging Data Structure 
[BIDS, @gorgolewski_brain_2016], with a rich ecosystem of tools being available 
to accomplish this [e.g. @halchenko_2024_11201247; @zwiers_bidscoin_2021]. 
Furthermore, to our knowledge, none of the available solutions cover scan session 
documentation, which currently is often either manually implemented 
with hand written notes [@meissner_head_2020], with Electronic Data Capture 
systems (e.g. https://www.castoredc.com/) or neglected entirely. 

Scan Session Tool was written to fill this gap, and to be used by
neuroscientists, to help them increase transparency and reproducibility of their
MRI research by standardising scan session documentation and raw data archiving.
The software has already been successfully used during data collection of several
fMRI studies [e.g. @krause_real-time_2017; @luhrs_potential_2019;
@krause_active_2019; @krause_selfregulation_2021], and its standardised scan
session documentation as well as archiving structure have been made part of
openly published data [e.g. @krause_selfregulation_2021_data]. The archiving
structure is furthermore automatically already recognised by the third-party
software BIDScoin [since version 3.7.3, @zwiers_bidscoin_2021], which allows the
raw DICOM data archived with Scan Session Tool to be converted to the popular
BIDS format if desired (e.g. for standardised preprocessing and analysis). We
hope to see further adaptation and increasing integration with other tools and
standardised workflows (e.g. quality control pipelines, online data
repositories) in the future. 


# Figures

![Example of documenting a scan session with Scan Session Tool.\label{fig:Figure1}](ScanSessionToolExample.png)

![Example of resulting folder structure after archiving data with Scan Session Tool.\label{fig:Figure2}](ArchivingStructureExample.png)


# References

