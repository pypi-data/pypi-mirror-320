import os
import shutil
import pytest
from templateengine.exec.el_operations import CopyDirElOp

def setup_module(module):
    os.makedirs("test_source_dir", exist_ok=True)
    os.makedirs("test_destination_dir", exist_ok=True)
    with open("test_source_dir/file.txt", "w") as f:
        f.write("Directory Test")

def teardown_module(module):
    shutil.rmtree("test_source_dir", ignore_errors=True)
    shutil.rmtree("test_destination_dir", ignore_errors=True)

def test_copy_dir():
    operation = CopyDirElOp()
    operation.run({
        'source': 'test_source_dir',
        'destination': 'test_destination_dir',
        'ignore_list': []
    })
    assert os.path.exists("test_destination_dir/file.txt")