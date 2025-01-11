import os
import sys
import json
import argparse
from ..data.InputParams import InputParams
from ..data.CommandType import CommandType

# Error codes:
# 0 - Successful completion
# 1 - Unknown error
# 2 - Invalid template
# 3 - Invalid specification
# 4 - Error in AI model
class CommandLineInput: #TODO Approve input params and checking input parameters and showing errors
    def __init__(self):
        pass

    @staticmethod
    def parse(args: list[str]) -> InputParams:
        parser = argparse.ArgumentParser(
            description="Template Engine V2 - Create software component skeletons from templates with AI support."
        )
        parser.add_argument("-c", "--command", help="Command to execute (create, extend, fix, etc.)")
        parser.add_argument("-t", "--template", help="Dir path to component template | Usage: -t <path>, --template=<path>")
        parser.add_argument("-i", "--input", help="Dir path to input software component | Usage: -i <path>, --input=<path>")
        parser.add_argument("-o", "--output", help="Dir path to output software component | Usage: -o <path>, --output=<path>")
        parser.add_argument("-g", "--ignore", default=".gitignore", help="File name or relative path in input/template dir to list of ignored paths | Default: .gitignore")
        parser.add_argument("-n", "--name", action="append", help="Replacements to perform | Usage: -n <old_name>:<new_name>")
        parser.add_argument("-s", "--spec", help="File path to component specifications (formal or informal) | Usage: -s <path>, --spec=<path>")
        parser.add_argument("-q", "--quiet", action="store_true", help="Mute line output | Usage: -q, --quiet")
        parser.add_argument("-v", "--verbose", action="store_true", help="Include verbose line output | Usage: -v, --verbose")
        parser.add_argument("-m", "--model", default="gpt-4o", help="GPT model to use for AI assistance | Default: gpt-4o")

        parsed_args = parser.parse_args(args)

        # Check for API key in environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            api_key = input("OPENAI_API_KEY environment variable not found. Please enter your API key manually: ").strip()

        if not api_key or len(api_key) < 20:
            print("Code 4 - Invalid or missing API key.")
            sys.exit(4)

        # Load command
        command = parsed_args.command

        # Check output directory
        output_dir = parsed_args.output
        if not output_dir:
            print(f"Code 2 - Output param does not exist.")
            sys.exit(2)

        # Load template directory, validate if required for specific commands
        template_dir = parsed_args.template
        if not template_dir and command == 'create-skeleton':
            print(f"Code 2 - Template does not exist.")
            sys.exit(2)

        # Load input directory
        input_dir = parsed_args.input if parsed_args.input else (template_dir if template_dir else output_dir)

        # Handle quiet and verbose flags
        quiet = parsed_args.quiet
        verbose = not quiet and parsed_args.verbose

        # Handle spec file
        spec_file = parsed_args.spec
        specs = {}
        if spec_file is not None:
            if not os.path.isfile(spec_file):
                print(f"Code 3 - Specification file {spec_file} does not exist.")
                sys.exit(3)
            try:
                with open(spec_file, 'r') as file:
                    specs = json.load(file)
            except Exception as e:
                print(f"Code 3 - unable to load JSON from specs file at {spec_file}: {e}")
                sys.exit(3)

        # Handle replacements
        replacements = []
        if parsed_args.name:
            for name in parsed_args.name:
                old_name, new_name = name.split(':')
                replacements.append({"search": old_name, "replace": new_name})

        # Load ignore list
        ignore_list = []
        ignore_file_path = os.path.join(input_dir, parsed_args.ignore) or None
        if ignore_file_path is not None and os.path.isfile(ignore_file_path):
            with open(ignore_file_path, 'r', encoding='utf-8') as file:
                ignore_list = [line.strip() for line in file if line.strip() and not line.startswith("#")]

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Populate InputParams
        return InputParams(
            command=command,
            template_dir=template_dir,
            input_dir=input_dir,
            output_dir=output_dir,
            specs=specs,
            ignore_list=ignore_list,
            replacements=replacements,
            quiet=quiet,
            verbose=verbose,
            model=parsed_args.model,
            api_key=api_key
        )
