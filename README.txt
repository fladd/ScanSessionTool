+ - - - - - - - - - - - - - - Scan Session Tool - - - - - - - - - - - - - - +
|                                                                           |
|        A tool for MR scan session documentation and data archiving        |
|                                                                           |
|             Author: Florian Krause <Florian.Krause@fladd.de>              |
|                                                                           |
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +



=================================== About ===================================

The Scan Session Tool is a graphical application for documenting (f)MRI scan
sessions and automatized data archiving. Information about the scan session
itself, used forms and documents, as well as the single measurements can be
entered and saved into a protocol file. This information can furthermore be
used to copy acquired data (DICOM images, stimulation protocols, logfiles,
Turbo Brain Voyager files) into a specific hierarchical folder structure for
unified archiving purposes.



=================================== Usage ===================================

The user interface is organized into three different content areas, each hol-
ding different information about the scan session, as well as an additional
control area for saving and loading session information and for automatically
archiving acquired data, based on the session information.


----------------------- The "General Information" area ----------------------

This area provides input fields for basic information about the scan session.
Some of the fields allow for a selection of pre-specified values taken from a
config file (see below), while others take freely typed characters.
Fields that are marked with a red background, are mandatory and need to be
filled in. Fields that are marked with an orange background are automatically
filled in, but need to be checked.
The following fields are available:
    "Project"        - The project identifier
                       (free-type and selection)
    "Group"          - The group identifier
                       (free-type and selection)
    "Subject No."    - The subject number
                       (1-99)
    "Session"        - The session identifier
                       (free-type and selection)
    "Date"           - The date of the scan session
                       (free-type, auto-filled)
    "Booked Time"    - The time period the scanner was booked
                       (free-type)
    "Actual Time"    - The time period the scanner was actually used
                       (free-type)
    "Certified User" - The responsible user
                       (free-type and selection)
    "Backup Person"  - An additional person
                       (free-type and selection)
    "Notes"          - Any additional notes about the session
                       (free-type)


--------------------------- The "Documents" area ----------------------------

This area provides checkboxes to specify which forms and documents have been
collected from the participant. Additional documents can be specified in a
configuration file (see "Config File" section).
The following checkboxes are available:
    "MR Safety Screening Form"            - The (f)MRI screening from provi-
                                            ded by the scanning institution
    "Participation Informed Consent Form" - The official (f)MRI written con-
                                            sent form


------------------------- The "Measurements" area ---------------------------

This area provides several input fields for each measurement of the session.
When starting the application, only one (empty) measurement is shown. Click-
ing on "Add Measurement" will create additional measurements. Fields that are
marked with a red background, are mandatory and need to be filled in. Fields
that are marked with an orange background are automatically filled in, but
need to be checked.
The following input fields are available per measurement:
    "No"                   - The number of the measurement
                             (1-99)
    "Type"                 - "anatomical", "functional" or "misc"
                             (selection)
    "Vols"                 - The number of volumes of the measurement
                             (free-type)
    "Name"                 - The name of the measurement
                             (free-type, selection)
    "Logfiles"             - A newline separated list of all connected logfiles
                             (free-type)
                             (Please note that a stimulation protocol mask
                             will be included automatically, based on the
                             session information, and will be replaced by
                             the found files matching this mask)
    "Comments"             - Any additional comments about the measurement
                             (free-type)


----------------------------- The control area ------------------------------

The control area consists of the following three buttons:
"Save"    - Saves the entered session information into a text file
"Load"    - Loads previously saved information from a text file
"Archive" - Copies acquired data from specified location into a timestamped
            sub-folder <~Archiveyyymmdd>. Please note that all data is
            expected to be within the specified folder. That is, all DICOM
            files (*.dcm OR *.IMA; no sub-folders!), all stimulation protocols,
            all logfiles as well as all Turbo Brain Voyager files (all *.tbv
            files in a folder called 'TBVFiles').
            The data will be copied into the following folder hierarchy (with
            the <Type> directories shortened to "anat", "func", and "misc"):
            DICOMs -->
              <Project>/<Subject[Group]>/<Session>/<Type>/<Name>/<DICOM>/
            Logfiles -->
              <Project>/<Subject[Group]>/<Session>/<Type>/<Name>/
            Turbo Brain Voyager files -->
             <Project>/<Subject[Group]>/<Session>/<Type>/<Name>/TBV/
            Scan Session Protocol -->
              <Project>/<Project>_<Subject[Group]>_Session_ScanProtocol.txt



================================ Config File ================================

A configuration file can be created to pre-define the values to be used as
selection options for the "Group", "Session", "Certified User", "Backup
Person", the measurement "Name" on a per project basis, as well as additional
items in the "Documents" section. The Scan Session Tool will look for a
configuration file with the name "sst.cfg" located in the same directory as
the application itself.
The following syntax is used:

Project: Project1
Groups: Group1, Group2
Sessions: Sess1, Sess2
Measurements Anatomical: Localizer, Anatomy
Measurements Functional: Run1, Run2, Run3
Users: User1, User2, User3
Backups: User1, User2, User3
Documents: Pre-Scan Questionnaire, Post-Scan Questionnaire

Project: Project2
Groups: GroupA, GroupB
Sessions: SessA, SessB
Measurements Anatomical: Localizer, MPRAGE
Measurements Functional: RunA, RunB, RunC
Users: UserA, UserB, UserC
Backups: UserA, UserB, UserC
Documents: Participation Reimbursement Form