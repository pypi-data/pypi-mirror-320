import os
import pytest
from templateengine.exec.el_operations import DeleteFileElOp

def setup_module(module):
    with open("test_file_to_delete.txt", "w") as f:
        f.write("Delete Test")

def test_delete_file():
    operation = DeleteFileElOp()
    operation.run({'path': 'test_file_to_delete.txt'})
    assert not os.path.exists("test_file_to_delete.txt")