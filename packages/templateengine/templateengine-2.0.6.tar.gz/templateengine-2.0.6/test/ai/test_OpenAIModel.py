import pytest
from unittest.mock import MagicMock

from templateengine.ai import OpenAIModel


@pytest.fixture
def mock_openai_client(mocker):
    # Patch the OpenAI client and set up the mocked response
    mock_client = mocker.patch('templateengine.ai.OpenAIModel.OpenAI').return_value
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Mocked response content"))]
    )
    return mock_client


@pytest.fixture
def openai_model():
    # Initialize OpenAIModel with a mock API key
    return OpenAIModel()


# def test_generate_replacement(openai_model, mock_openai_client):
#     # Define a test prompt
#     prompt = "Generate mocked response content"

#     # Call generate_replacement and capture the result
#     result = openai_model.generate_replacement(prompt)

#     # Assert that the result is as expected from the mock
#     assert result == "Mocked response content"

#     # Verify that the OpenAI API was called with the expected arguments
#     mock_openai_client.chat.completions.create.assert_called_once_with(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": prompt},
#         ],
#     )


# def test_parse_informal_description(openai_model, mock_openai_client):
#     # Define a test description
#     description = "Generate a file called example.py in /src with a function that prints 'Hello, world!'"

#     # Call parse_informal_description and capture the result
#     result = openai_model.parse_informal_description(description)

#     # Assert that the result is as expected from the mock
#     assert result == "Mocked response content"

#     # Verify that the OpenAI API was called with the expected arguments
#     mock_openai_client.chat.completions.create.assert_called_once_with(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": (
#                 f"Here is a text description from a file:\n{description}\n\n"
#                 "Parse this informal description and extract file name, file path.\n"
#                 "Generate code component based on description content.\n"
#                 "Return the result in the json object with three fields:\n"
#                 "file_name:<file_name>\n file_path:<path>\n content:<content>\n"
#                 "-> generated content based on description content.\n"
#                 "Provide only resulting json without your clarification on what you did."
#             )}
#         ],
#     )
