import json

class InputParams: #TODO Approve input params
    def __init__(
        self,
        command,
        template_dir,
        input_dir,
        output_dir,
        specs,
        ignore_list,
        replacements,
        quiet,
        verbose,
        model,
        api_key
    ):
        self.command = command
        self.template_dir = template_dir
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.specs = specs
        self.ignore_list = ignore_list
        self.replacements = replacements
        self.quiet = quiet
        self.verbose = verbose
        self.model = model
        self.api_key = api_key

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)    
