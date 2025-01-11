import pytest
import sys
import os
import json
from unittest.mock import MagicMock
from templateengine.cmd.CommandLineInput import CommandLineInput
from templateengine.data.InputParams import InputParams

@pytest.fixture
def mock_file_operations(mocker):
    # Mock os.path.isfile and os.makedirs
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("os.makedirs", return_value=None)

@pytest.fixture
def mock_open(mocker):
    # Mock the open function to simulate reading JSON specs and ignore files
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps({"key": "value"})))
    return mock_open

def test_parse_create_skeleton(mock_file_operations, mock_open):
    # Arrange: Set up the args and expected values
    args = [
        "-c", "create_skeleton",
        "-t", "/path/to/template",
        "-o", "/path/to/output",
        "-i", "/path/to/input",
        "-n", "old_name:new_name",
        "-s", "/path/to/spec.json",
        "-g", ".custom_ignore",
        "-v"
    ]
    
    # Mock the ignore file reading
    mock_open.return_value.readlines.return_value = [{"key": "value"}]

    # Act: Parse the arguments
    input_params = CommandLineInput.parse(args)

    # Assert: Verify the parsed InputParams fields
    assert input_params.command == "create_skeleton"
    assert input_params.template_dir == "/path/to/template"
    assert input_params.input_dir == "/path/to/input"
    assert input_params.output_dir == "/path/to/output"
    assert input_params.replacements == [{"search": "old_name", "replace": "new_name"}]
    assert input_params.specs == {}
    assert input_params.ignore_list == ['{"key": "value"}']
    assert input_params.verbose is True
    assert input_params.quiet is False

def test_parse_missing_output_raises_error(mock_file_operations, capsys):
    # Arrange: Missing output argument
    args = ["-c", "create_skeleton", "-t", "/path/to/template"]
    
    # Act: Run the parser and capture output
    with pytest.raises(SystemExit) as e:
        CommandLineInput.parse(args)

    # Assert: Ensure it exits with code 2 and has the expected message
    assert e.value.code == 2
    captured = capsys.readouterr()
    assert "Code 2 - Output param does not exist." in captured.out

def test_parse_invalid_spec_file_raises_error(mock_file_operations, mocker, capsys):
    # Arrange: Mock os.path.isfile to return False for spec file
    mocker.patch("os.path.isfile", side_effect=lambda path: path != "/path/to/spec.json")
    args = ["-c", "extend", "-t", "/path/to/template", "-o", "/path/to/output", "-s", "/path/to/spec.json"]
    
    # Act: Run the parser and capture output
    with pytest.raises(SystemExit) as e:
        CommandLineInput.parse(args)
    
    # Assert: Ensure it exits with code 3 and has the expected message
    assert e.value.code == 3
    captured = capsys.readouterr()
    assert "Code 3 - Specification file /path/to/spec.json does not exist." in captured.out
