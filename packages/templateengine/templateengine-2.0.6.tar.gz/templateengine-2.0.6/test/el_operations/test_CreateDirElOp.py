import os
import pytest
from templateengine.exec.el_operations import CreateDirElOp

def teardown_module(module):
    os.rmdir("test_created_dir")

def test_create_dir():
    operation = CreateDirElOp()
    operation.run({'path': 'test_created_dir'})
    assert os.path.exists("test_created_dir")