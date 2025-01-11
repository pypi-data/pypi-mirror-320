import os
import pytest
from templateengine.exec.el_operations import CreateFileElOp

def teardown_module(module):
    os.remove("test_created_file.txt")

def test_create_file():
    operation = CreateFileElOp()
    operation.run({'path': 'test_created_file.txt'})
    assert os.path.exists("test_created_file.txt")