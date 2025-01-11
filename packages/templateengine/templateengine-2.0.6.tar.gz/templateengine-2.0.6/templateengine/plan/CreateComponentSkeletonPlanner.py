import json
import os
from yaspin import yaspin
from yaspin.spinners import Spinners
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm
from ..plan.CommonPlanner import CommonPlanner
from ..exec.Action import Action
from ..exec.tools.ToolTypes import ToolTypes
from ..ai.OpenAISession import OpenAISession
from ..strategy.StrategyAction import StrategyAction

class CreateComponentSkeletonPlanner(CommonPlanner):
    actions_session: OpenAISession = None
    template_project_structure = None
    template_metadata = None
    is_new_actions_session = False

    def __init__(self):
        super().__init__()

    def run(self) -> list[Action] | list[StrategyAction]:
        self.__init_actions_session()
        self.spinner.reset_spinner()
        try:
            self.spinner.start()
            # Step 1: Get project structure
            if self.params.template_dir:
                if self.verbose:
                    self.logger.info(None, "Retrieving template project structure and metadata...")
                self.template_project_structure = self.__get_project_structure(self.params.template_dir)
                if (os.path.exists(self.params.template_dir) and
                        os.path.exists(self.params.template_dir + "/metadata.json") and
                        os.path.isfile(self.params.template_dir + "/metadata.json")):
                    with open(self.params.template_dir + "/metadata.json", "r", encoding="utf-8") as file:
                        self.template_metadata = file.read()

            # Step 2: Generate and send prompt
            if self.verbose:
                self.logger.info(None, "Generating and Sending prompt to generate actions...")
            response = self.__generate_and_send_actions_prompt()

            # Step 3: Process actions
            if self.verbose:
                self.logger.info(None, "Generate actions...")
            actions = self.__get_actions(response)

            self.spinner.set_success_spinner("Generating actions completed successfully!")
        except Exception as e:
            self.spinner.set_failure_spinner("Error in CreateComponentSkeletonPlanner.run() is occurred.", e)
            raise e
        finally:
            self.spinner.stop()
        return actions

    def __init_actions_session(self) -> None:
        def __init():
            self.actions_session = self.ai_model.create_session(session_id=self.metadata.get("session_id", None) or None)
            self.actions_session.add_role("system",
                                        "You are a strategic planner and analyst. Your task is to evaluate metadata, input parameters, and user prompts to generate a structured actions plan. Your focus is on aligning actions with strategic goals and ensuring clarity in the steps required.")
            self.is_new_actions_session = True
        if self.actions_session is None:
            self.ai_model.delete_sessions()
            __init()
        else:
            if self.metadata.get("session_id") is not None:
                self.actions_session = self.ai_model.get_session(session_id=self.metadata.get("session_id", None) or None)
                if self.actions_session is None:
                    __init()
                else:
                    self.is_new_actions_session = False
            else:
                __init()

    def __send_actions_prompt(self, prompt: str) -> str:
        self.actions_session.add_role("user", prompt)
        return self.actions_session.send_prompt()

    def __get_project_structure(self, path: str):
        structure = {}
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                structure[entry] = self.__get_project_structure(full_path)  # Recursively process subdirectories
            else:
                structure[entry] = None  # Files are represented as `None`
        return structure

    def __calculate_files_count(self, structure: dict) -> int:
        count = 0
        if structure is not None:
            for key, value in structure.items():
                if value is None:
                    count += 1
                elif isinstance(value, dict):
                    count += self.__calculate_files_count(value)
        return count

    def __generate_and_send_actions_prompt(self) -> str:
        goals = "".join([goal.get_goal() for goal in self.goals])        
        project_structure = json.dumps(self.template_project_structure, indent=4)
        tasks = [("\nTasks: \n"
            f"Analyze the goals, template project path(if exists), template project structure(if exists), template metadata(if exists)"
            "output project path, output project structure, list of tools, ignore list, list of replacements, description.\n"
            "Generate a set of actions to achieve the goals using the parameters above.\n"),
            ("Main steps: \n"
            "1. IMPORTANT! First, create a skeleton of the resulting project based on the tasks from the description template dir(if exists) and output dir:"
            "copy, rename, delete folders and files.\n"
            "IMPORTANT! Generate a complete list of operations for copy, rename, delete folders and files based on the description and tasks in it."
            "2. After that, generate a list of edit_content actions with content which will be updated by search&replace logic using replacements array.\n\n"),
            ("User Guide for Tools: \n"
            "Use copy and rename tools to update output project structure based on replacements.\n"            
            "Copy and rename tools should return source and destination(rename destination should be updated from replacements list).\n"
            f"{ToolTypes.EDIT_CONTENT} tools should work with all files inside new component.\n"
            "If it is necessary to make replacements in folder names or file names, then the old folders or files (which were replaced) should not be in the new project, only renamed. The remaining folders or files that were not searched and replaced should simply be copied and the edit_content operation performed.\n"
            "Generate them in the end of the Actions list.\n"
            f"In {ToolTypes.EDIT_CONTENT} and {ToolTypes.CREATE_FILE} tools provide path and old_path(path from template_dir).\n"
            "if replacements occur, the path must be updated based on the search and the replace(this is an important part), in the tool_params, also you need to enter the old_path(path before replacements from template dir) before the replacement for the further possibility of updating the content in the file\n")]
        expected = Action.get_prompt()        
        prompts = [f"Strategy goals for planning block:\n{goals} \n\n",
                  f"Template project path:\n {self.params.template_dir} \n\n",
                  f"Template project structure:\n {project_structure} \n\n",
                  f"Output project path:\n {self.params.output_dir} \n\n",
                  f"Project Metadata: \n {self.template_metadata or ""} \n\n",
                  f"List of tool to achieve goals:\n {json.dumps(self.tools)}\n\n",
                  f"Ignore list:\n {self.params.ignore_list}\n\n",
                  f"List of replacements from parameters:\n {self.params.replacements}\n\n",
                  f"{expected}\n\n",
                  """An example of the result: [{"tool_name": ..., "tool_params": {}}, ...]"""]        
        prompts.extend(tasks)
        return_yes = "Print Yes if understand."
        for prompt in prompts:
            r = self.__send_actions_prompt(prompt + return_yes)
            if "Yes" in r:
                continue
            else:
                break

        return self.__send_actions_prompt(f"Check the result, check a full coverage of all tasks by a set of tools, pay attention with {ToolTypes.EDIT_CONTENT} and renaming tools\n"
                                              "Provide only resulting json without your clarification on what you did.")

    def __get_actions(self, response: str) -> list[Action]:
        files_count = self.__calculate_files_count(self.template_project_structure)
        all_actions = json.loads(response)
        not_edit_content_actions = list(filter(lambda x: x["tool_name"] != ToolTypes.EDIT_CONTENT, all_actions))
        edit_content_actions = list(filter(lambda x: x["tool_name"] == ToolTypes.EDIT_CONTENT, all_actions))
        if len(edit_content_actions) > 0:
            while True:
                _actions: list[Action] = json.loads(response)
                edit_content_actions = list(filter(lambda x: x["tool_name"] == ToolTypes.EDIT_CONTENT, _actions))
                if len(edit_content_actions) < files_count and len(self.params.replacements) > 0:
                    prompt = (
                        f"The task was not completed correctly. The number of files in the "
                        f"structure ({files_count}) does not match the number of edit_content actions "
                        f"({len(edit_content_actions)}). Generate all actions for processing from the template structure, as well as additional actions that will fulfill the requirements from the description if necessary. Please review and adjust.\n"
                        f"Analyze prompt before, analyze response and new clarifications.\n"
                        f"Return the result as json only with an array of all {ToolTypes.EDIT_CONTENT} actions inside.\n"
                        f"Also remember the actions that need to be generated to update existing files (their content) depending on the description and tasks set above.\n"
                        f"In tool_params should be: \n"
                        "path -> new path of the file with new file name using output project path and dir or file name after replacement if exists(see above in prompt and params replacements array))\n"
                        "path property is important path so be careful to generate it and if you do a search and replace don't forget to correct the path it is an important part\n"
                        "old_path -> path before replacement with old file name using template project path(see above in prompt and params)).\n"                        
                        """An example of the result: {[{"tool_name": ..., "tool_params": {}}, ...]}"""
                        f"\nProvide only resulting json without your clarification on what you did."
                    )
                    self.actions_session.add_role("user", prompt)
                    response = self.actions_session.send_prompt()
                else:
                    break
            edit_content_actions = self.__edit_content(edit_content_actions)
        return not_edit_content_actions + edit_content_actions

    def __edit_content(self, actions: list[Action]) -> list[Action]:
        def process_and_update_action(idx, action):
            try:
                # Process file and get new content
                file_path = action["tool_params"].get("old_path")
                if not file_path:
                    raise ValueError("File path is missing in action")
                new_content = self.__process_file(file_path)
                # Update action with the new content
                action["tool_params"]["content"] = new_content
            except Exception as e:
                if self.verbose:
                    self.logger.fatal(None, e, f"Error processing action at index {idx}: {e}")

        MAX_WORKERS = 20
        self.spinner.stop()
        with ThreadPoolExecutor() as executor: # max_workers=MAX_WORKERS
            # Submit tasks for processing actions
            with tqdm(total=len(actions), desc="Generate files content", unit="file") as progress_bar:
                futures = [
                    executor.submit(process_and_update_action, idx, action)
                    for idx, action in enumerate(actions)
                ]

                # Ensure all tasks are completed
                for future in futures:
                    try:
                        future.result()  # Raises any exception from the thread
                    except Exception as e:
                        if self.verbose:
                            self.logger.fatal(None, e, f"Unhandled exception during processing: {e}")
                    finally:
                        progress_bar.update(1)
        self.spinner.start()
        return actions

    def __process_file(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            new_content = self.__replace_in_content(content)

            return new_content
        except Exception as e:
            if self.verbose:
                self.logger.fatal(None, e, f"Code 1 - error processing file at {file_path}: {e}")

    def __replace_in_content(self, content: str):
        prompt = f"Here is a text from a file:\n{content}\n\n"
        for replacement in self.params.replacements:
            prompt += f"Replace all occurrences of '{replacement['search']}' with '{replacement['replace']}'.\n"
        prompt += "Provide only updated text without your clarification what you did"
        return self.__send_prompt(prompt)

    def __send_prompt(self, prompt: str) -> str:        
        session = self.ai_model.create_session(session_id=self.metadata.get("session_id", None) or None)
        session.add_role("system", "You are a versatile content editor and generator specializing in code. Your task is to review and edit existing files or create new content based on user requirements. You handle backend, frontend, tests, DevOps scripts, and other coding needs across various languages, platforms, and frameworks. Ensure the code is optimized, clean, and follows best practices. For edits, highlight changes and explain your reasoning in the comments. For new content, ensure it is well-documented, efficient, and aligned with the specified requirements.").add_role("user", prompt)
        return session.send_prompt()
