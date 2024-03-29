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

Scan Session Tool is a cross-platform (Windows, MacOS, Linux) graphical
application for standardized real-time documentation of (functional) Magnetic
Resonance Imaging (MRI) scan sessions and automatized archiving of the
collected (raw) data. The software allows session information (i.e. metadata,
project- and subject-specific notes/documents, as well as a detailed log of
acquired MRI measurements) to be entered in a fast and convenient way during a
session (see also \autoref{fig:Figure1}) and to be saved into a human- and
machine-readable protocol file (in YAML format) that facilitates both sharing
with other researchers and integration into automatized procedures.
Scan Session Tool can furthermore use this scan session documentation itself to
automatically organize the raw data (i.e. DICOM images) of all acquired
measurements, as well as any related logfiles (e.g. stimulation protocols,
response time recordings, etc.) into a unified hierarchical folder structure for
archiving purposes (see also \autoref{fig:Figure2}).
In addition, the software has (optional) special support for BrainVoyager and
(Turbo-)BrainVoyager (which is commonly used for real-time functional MRI
measurements).


# Statement of need

There is an urgent need to improve the reproducibility of (functional) MRI
research through transparent reporting [@noauthor_fostering_2017]. Despite
large agreement among researchers on the importance of openly sharing not only
collected raw data (i.e. MR images and related behavioural/physiological
recordings) and their analysis [@nichols_best_2017], but also the detailed
documentation of the data collection process [i.e. notes and data about the
scan sessions themselves, @borghi_data_2018; @glover_function_2012],
standardization in this domain is currently lacking. Shared MR images are often
only made available after transformation into a derivative data format, such as
the Brain Imaging Data Structure [BIDS, @gorgolewski_brain_2016], and scan
session documentation is commonly either manually implemented [e.g. with hand
written notes, @meissner_head_2020] or neglected entirely.

Scan Session Tool was written to fill this gap, and to be used by
neuroscientists, to help them increase transparency and reproducibilty of their
MRI research by standardizing scan session documentation and raw data archiving.
The software has already been succesfully used during data collection of several
fMRI studies [e.g. @krause_real-time_2017; @luhrs_potential_2019;
@krause_active_2019; @krause_selfregulation_2021], and its standardized scan
session documentation as well as archiving structure have been made part of
openly published data [e.g. @krause_selfregulation_2021_data]. The archiving
structure is furthermore automatically already recognized by the third-party
software BIDScoin [since version 3.7.3, @zwiers_bidscoin_2021], which allows the
raw DICOM data archived with Scan Session Tool to be converted to the popular
BIDS format if desired (e.g. for standardized preporocessing and analysis). We
hope to see further adaptation and increasing integration with other tools and
standardized workflows (e.g. quality control pipelines, online data
repositories) in the future. 


# Figures

![Example of documenting a scan session with Scan Session Tool.\label{fig:Figure1}](ScanSessionToolExample.png)

![Example of resulting folder structure after archiving data with Scan Session Tool.\label{fig:Figure2}](ArchivingStructureExample.png)


# References

