import os
import unittest
import tempfile
import filecmp
import zipfile

from tkinter import *
from tkinter import _tkinter
from tkinter.ttk import *

from dataintegrityfingerprint import DataIntegrityFingerprint

from scansessiontool.scansessiontool import ScanSessionTool


DATA_DIR = None

def setUpModule():
    with zipfile.ZipFile(os.path.join(os.path.join(os.path.split(__file__)[0]),
                                      "TestData.zip"), 'r') as z:
        global DATA_DIR
        DATA_DIR = tempfile.TemporaryDirectory()
        print("Extracting test data...\n")
        z.extractall(DATA_DIR.name)

def cleanup():
    global DATA_DIR
    DATA_DIR.cleanup()

unittest.addModuleCleanup(cleanup)


class TestScanSessionDocumentation(unittest.TestCase):
    def setUp(self):
        global DATA_DIR
        self.test_protocol = os.path.join(
            DATA_DIR.name,
            "ScanProtocol_TestData_sub-001_ses-007-Transfer_20211203.txt")
        self.root = Tk()

    def test_open_save_scan_protocol(self):
        with tempfile.NamedTemporaryFile(mode='w') as output:
            app = ScanSessionTool(self.root,
                                  run_actions={"open": [self.test_protocol],
                                               "save": [output.name]})
            self.assertTrue(
                filecmp.cmp(self.test_protocol, output.name, shallow=False),
                "(Re)saved scan protocol file differs from original.")


class TestDataArchiving(unittest.TestCase):
    def setUp(self):
        global DATA_DIR
        self.test_protocol = os.path.join(
            DATA_DIR.name,
            "ScanProtocol_TestData_sub-001_ses-007-Transfer_20211203.txt")
        self.checksums_dif = DataIntegrityFingerprint(
            os.path.join(DATA_DIR.name, "TestData.sha256"),
            from_checksums_file=True)
        self.root = Tk()

    def test_archive_data_single_folder(self):
        global DATA_DIR
        with tempfile.TemporaryDirectory() as output:
            test_data = os.path.join(DATA_DIR.name, "TestData_1")
            app = ScanSessionTool(self.root,
                                  run_actions={"open": [self.test_protocol],
                                               "archive": [True, test_data,
                                                           output, 1, 1,
                                                           "TBVFiles",
                                                           "TBV_"]})
            dif = DataIntegrityFingerprint(os.path.join(output, "TestData"))
            self.assertEqual(
                dif.dif, self.checksums_dif.dif,
                "Archived data fingerprint differs from checksums file.")

    def test_archive_data_subfolders(self):
        global DATA_DIR
        with tempfile.TemporaryDirectory() as output:
            test_data = os.path.join(DATA_DIR.name, "TestData_2")
            app = ScanSessionTool(self.root,
                                  run_actions={"open": [self.test_protocol],
                                               "archive": [True, test_data,
                                                           output, 1, 1,
                                                           "TBVFiles",
                                                           "TBV_"]})
            dif = DataIntegrityFingerprint(os.path.join(output, "TestData"))
            self.assertEqual(
                dif.dif, self.checksums_dif.dif,
                "Archived data fingerprint differs from checksums file.")


if __name__ == "__main__":
    unittest.main()
