import os
import pytest
from templateengine.exec.el_operations import RenameFileElOp

def setup_module(module):
    with open("test_file_to_rename.txt", "w") as f:
        f.write("Rename Test")

def teardown_module(module):
    os.remove("renamed_file.txt")

def test_rename_file():
    operation = RenameFileElOp()
    operation.run({
        'source': 'test_file_to_rename.txt',
        'destination': 'renamed_file.txt'
    })
    assert os.path.exists("renamed_file.txt")