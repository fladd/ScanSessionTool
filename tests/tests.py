import os
import glob
import platform
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
    z = zipfile.ZipFile(os.path.join(os.path.join(os.path.split(__file__)[0]),
                                      "TestData.zip"), 'r')
    global DATA_DIR
    DATA_DIR = tempfile.TemporaryDirectory()
    print("Extracting test data...\n")
    z.extractall(DATA_DIR.name)

def cleanup():
    global DATA_DIR
    DATA_DIR.cleanup()

unittest.addModuleCleanup(cleanup)

def change_eol_win2unix(path):
    txt_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))

    for file in txt_files:
        with open(file, 'rb') as f:
            content = f.read()
        content = content.replace(b"\r\n", b"\n")
        with open(file, 'wb') as f:
            f.write(content)


class TestScanSessionDocumentation(unittest.TestCase):
    def setUp(self):
        global DATA_DIR
        self.test_protocol = os.path.join(
            DATA_DIR.name,
            "ScanProtocol_TestData_sub-001_ses-007-Transfer_20211203.txt")
        self.root = Tk()

    def tearDown(self):
        self.root.destroy()

    def test_open_save_scan_protocol(self):
        global DATA_DIR
        new_protocol = os.path.join(DATA_DIR.name, "newprotocol.txt")
        app = ScanSessionTool(self.root,
                              run_actions={"open": [self.test_protocol],
                                           "save": [new_protocol]})
        with open(self.test_protocol, 'r') as f1:
            with open(new_protocol, 'r') as f2:
                self.assertEqual(
                    f1.read(), f2.read(),
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

    def tearDown(self):
        self.root.destroy()

    def test_archive_data_single_folder(self):
        global DATA_DIR
        with tempfile.TemporaryDirectory(dir=DATA_DIR.name) as output:
            test_data = os.path.join(DATA_DIR.name, "TestData_1")
            app = ScanSessionTool(self.root,
                                  run_actions={"open": [self.test_protocol],
                                               "archive": [True, test_data,
                                                           output, 1, 1,
                                                           "TBVFiles",
                                                           "TBV_"]})
            if platform.system() == "Windows":
                change_eol_win2unix(os.path.join(output, "TestData"))
            dif = DataIntegrityFingerprint(os.path.join(output, "TestData"))
            self.assertEqual(
                dif.dif, self.checksums_dif.dif,
                "Archived data fingerprint differs from checksums file.")

    def test_archive_data_subfolders(self):
        global DATA_DIR
        with tempfile.TemporaryDirectory(dir=DATA_DIR.name) as output:
            test_data = os.path.join(DATA_DIR.name, "TestData_2")
            app = ScanSessionTool(self.root,
                                  run_actions={"open": [self.test_protocol],
                                               "archive": [True, test_data,
                                                           output, 1, 1,
                                                           "TBVFiles",
                                                           "TBV_"]})
            if platform.system() == "Windows":
                change_eol_win2unix(os.path.join(output, "TestData"))
            dif = DataIntegrityFingerprint(os.path.join(output, "TestData"))
            self.assertEqual(
                dif.dif, self.checksums_dif.dif,
                "Archived data fingerprint differs from checksums file.")


if __name__ == "__main__":
    unittest.main()
