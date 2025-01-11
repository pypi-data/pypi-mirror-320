import os
import pytest
from templateengine.exec.el_operations import CopyFileElOp

def setup_module(module):
    with open("test_file.txt", "w") as f:
        f.write("File Test")

def teardown_module(module):
    os.remove("test_file.txt")
    os.remove("test_file_copy.txt")

def test_copy_file():
    operation = CopyFileElOp()
    operation.run({
        'source': 'test_file.txt',
        'destination': 'test_file_copy.txt'
    })
    assert os.path.exists("test_file_copy.txt")