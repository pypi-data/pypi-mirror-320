import os
import pytest
from templateengine.exec.el_operations import RenameDirElOp

def setup_module(module):
    os.makedirs("test_dir_to_rename", exist_ok=True)

def teardown_module(module):
    os.rmdir("renamed_dir")

def test_rename_dir():
    operation = RenameDirElOp()
    operation.run({
        'source': 'test_dir_to_rename',
        'destination': 'renamed_dir'
    })
    assert os.path.exists("renamed_dir")