"""Utilities.

A set of utility functions used in Scan Session Tool.

"""


import os
import shutil
from tempfile import mkstemp

import pydicom


def replace(file_path, pattern, subst):
    """Replace text in a file.

    Parameters
    ----------
    file_path : str
        the file to replace text in
    pattern : str
        the text pattern to be replaced
    subst : str
        the text to replace the pattern with

    """

    # Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w', newline='')
    old_file = open(file_path, newline='')
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    # Close temp file
    new_file.close()
    os.close(fh)
    old_file.close()
    # Remove original file
    os.remove(file_path)
    # Move new file
    shutil.move(abs_path, file_path)

def readdicom(filename):
    """Read metadata from a DICOM file.

    Returns
    -------
    filename : str
        the DICOM file name
    series_number : int
        the DICOM series number
    acquisition_number : int
        the DICOM acquisition number
    instance_number : int
        the DICOM instance number
    protocol_name : str
        the DICOM protocol name
    echo_numbers : int
        the DICOM echo numbers

    """

    dicom = pydicom.filereader.read_file(filename, stop_before_pixels=True)
    return [filename, dicom.SeriesNumber, dicom.AcquisitionNumber,
            dicom.InstanceNumber, dicom.ProtocolName, dicom.EchoNumbers]
