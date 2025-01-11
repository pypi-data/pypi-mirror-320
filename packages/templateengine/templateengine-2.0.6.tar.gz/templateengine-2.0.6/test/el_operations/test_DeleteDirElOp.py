import os
import shutil
import pytest
from templateengine.exec.el_operations import DeleteDirElOp

def setup_module(module):
    os.makedirs("test_dir_to_delete", exist_ok=True)

def test_delete_dir():
    operation = DeleteDirElOp()
    operation.run({'path': 'test_dir_to_delete'})
    assert not os.path.exists("test_dir_to_delete")