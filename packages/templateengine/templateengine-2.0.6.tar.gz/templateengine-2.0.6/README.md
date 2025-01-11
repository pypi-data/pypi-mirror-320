# Template Engine V2

Hello there! Thank you for using the Template Engine. Please review our commercial license for legal use and contact us at [support@entinco.com](mailto:support@entinco.com) for inquiries and clarification.

---

## Overview
The Template Engine is a powerful tool designed to create software component skeletons from templates. This tool streamlines the process of creating complex software components by leveraging templates and advanced AI-based descriptions for increased precision.

## Features

### Template-based Skeleton Generation
- Copies a component template to a specified output directory and performs search & replace operations on targeted keywords.

### AI-Powered Planning and Strategy Selection
- Utilizes OpenAI's GPT model to analyze specifications and determine the most effective strategy for each task.
- Automatically identifies dependencies and optimizes execution paths.
- Supports generative assistance to create new templates and components based on custom needs and specifications.

### CLI with Flexible Options
- Offers intuitive command-line options for quiet, verbose, and replacement modes.
- Supports batch operations for repeatable processes, enabling automated workflows.
- Provides helpful error messages and usage hints for a smoother user experience.

### Specification Handling
- Reads JSON-formatted specification files to guide the component generation process.
- Adapts dynamically based on user-provided descriptions and templates.
- Integrates structured and unstructured input to provide a robust understanding of the component structure.
- Supports `.gitignore`-style lists to skip unnecessary files and directories during generation.

---

## Installation
Install this package from PyPI using the Python package installer (Pip):
```sh
pip install templateengine
```

---

## Command-line Usage
To run the Template Engine, use the following command in your terminal:
```sh
templateengine [options]
```

### General Arguments

- **`-h, --help`**: Displays available command-line arguments.
  - **Type**: Utility
  - **Required**: No

- **`--version`**: Displays the current version of the Template Engine.
  - **Type**: Utility
  - **Required**: No

### Primary Parameters

- **`-t, --template`**: Specifies the folder or directory path where the component template is located.
  - **Type**: Required
  - **Shorthand**: `-t`

- **`-o, --output`**: Specifies the folder or directory path where the resulting component will be saved.
  - **Type**: Required
  - **Shorthand**: `-o`

### Optional Parameters

- **`-g, --ignore`**: Specifies the file name or relative path in the template directory for a list of ignored keywords. By default, it looks for a `.gitignore` file.
  - **Type**: Optional
  - **Default**: `.gitignore`
  - **Shorthand**: `-g`

- **`-n, --name`**: Specifies a search and replacement keyword pair for renaming components. Can be repeated for multiple replacements.
  - **Type**: Optional but recommended
  - **Shorthand**: `-n`
  - **Usage**: `--name=<old_name>:<new_name>`
  - **Example**: `--name=entity:product`

- **`-v, --verbose`**: Enables verbose output for detailed information during execution.
  - **Type**: Optional
  - **Shorthand**: `-v`

- **`-q, --quiet`**: Mutes all output during execution. Overrides `--verbose` if both are present.
  - **Type**: Optional
  - **Shorthand**: `-q`

- **`-s, --spec`**: Specifies the file path to the component specifications file (in JSON format).
  - **Type**: Optional
  - **Shorthand**: `-s`
  - **Description**: This file guides the generation process and helps describe subcomponents in detail.

- **`-m, --model`**: Specifies the GPT model to use for AI-assisted generation.
  - **Type**: Optional
  - **Default**: `gpt-4o`
  - **Shorthand**: `-m`

### OpenAI API Key
The Template Engine requires an OpenAI API key to use AI-assisted planning and component generation. The API key can be provided in two ways:

1. **Environment Variable**: Set the `OPENAI_API_KEY` in your system environment.
   ```sh
   export OPENAI_API_KEY=your_openai_api_key_here
   ```
   - **Benefits**: Automatically read during execution for convenience.

2. **Manual Input**: If the environment variable is not set, the Template Engine will prompt you to input the API key manually.

### API Key Validation:
- The API key must be at least 20 characters long.
- If the key is invalid or missing, the program will terminate with an error code `4`.
  ```sh
  Code 4 - Invalid or missing API key.
  ```
- **Security Tip**: Do not share or hard-code your API key in scripts to avoid unauthorized access.

### Example Usage
Here's an example of running the Template Engine from the command line:
```sh
#!/usr/bin/env pwsh

templateengine \
--template=../../templates/backend/node/service-cruddata-pipservices \
--output=../../output/service-products-pipservices \
--name=cruddata:products \
--name=entity:product \
--name=entities:products \
--spec=specifications/description.json \
--verbose
```

---

## InputParams Structure
The `InputParams` class stores all the key parameters passed to the Template Engine. Here is a breakdown of its attributes:

- **`command`** *(str)*: Specifies the command to execute (e.g., `create`, `extend`, `fix`).
- **`template_dir`** *(str)*: Directory path to the template being used.
- **`input_dir`** *(str)*: Directory path to the input software component.
- **`output_dir`** *(str)*: Directory path where the output software component will be saved.
- **`ignore_list`** *(list)*: List of paths or filenames to ignore during template processing.
- **`replacements`** *(list of dicts)*: List of search and replacement keyword pairs for renaming components.
  - Example: `[{"search": "cruddata", "replace": "products"}]`
- **`specs`** *(dict)*: JSON-formatted specifications that guide the component generation process.
- **`quiet`** *(bool)*: Whether to suppress all output.
- **`verbose`** *(bool)*: Whether to display detailed execution logs.
- **`model`** *(str)*: Specifies the GPT model to use (default: `omni`).
- **`api_key`** *(str)*: OpenAI API key for accessing AI-powered features.

---

## Contact
Please contact us at [support@entinco.com](mailto:support@entinco.com) for inquiries and clarification.

---

Thank you for using the Template Engine!
