Scan Session Tool
=================

About
-----
The Scan Session Tool is a graphical application for documenting (f)MRI scan
sessions and automatized data archiving. Information about the scan session
itself, used forms and documents, as well as the single measurements can be
entered and saved into a protocol file. This information can furthermore be
used to copy acquired data (DICOM images as well as optional stimulation
protocols and logfiles into a specific hierarchical folder structure for
unified archiving purposes, with optional sepcial support for
(Turbo-)BrainVoyager.


Installation
------------
The Scan Session Tool is a Python script and hence runs wherever Python (with
TKinter), PyYAML and pydicom are installed.

Install required packages with:
```
python3 -m pip install pyYAML pydicom
```

Then simply run `python3 scan_session_tool.py`.


Documentation
-------------
The full documentation can be found from within the programme, by clicking on
the "?" button, or by selecting "Scan Session Tool Help" from the Help menu.
