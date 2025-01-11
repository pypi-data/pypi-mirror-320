import os
import shutil
import pytest
from templateengine.exec.el_operations import CopyAllElOp

def setup_module(module):
    os.makedirs("test_source", exist_ok=True)
    os.makedirs("test_destination", exist_ok=True)
    with open("test_source/test_file.txt", "w") as f:
        f.write("Hello, World!")

def teardown_module(module):
    shutil.rmtree("test_source", ignore_errors=True)
    shutil.rmtree("test_destination", ignore_errors=True)

def test_copy_all():
    operation = CopyAllElOp()
    operation.run({
        'source': 'test_source',
        'destination': 'test_destination',
        'ignore_list': []
    })
    assert os.path.exists("test_destination/test_file.txt")