import os
import pytest
from templateengine.exec.el_operations import EditContentElOp

def setup_module(module):
    with open("test_edit_file.txt", "w") as f:
        f.write("Old Content")

def teardown_module(module):
    os.remove("test_edit_file.txt")

def test_edit_content():
    operation = EditContentElOp()
    operation.run({
        'path': 'test_edit_file.txt',
        'content': 'New Content'
    })
    with open("test_edit_file.txt", "r") as f:
        content = f.read()
    assert content == "New Content"