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

class ParseDescriptionPlanner(CommonPlanner):
    actions_session: OpenAISession = None
    project_structure = None
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
            if self.verbose:
                self.logger.info(None, "Retrieving output project structure...")
            self.project_structure = self.__get_project_structure(self.params.output_dir)
            if (os.path.exists(self.params.output_dir) and
                        os.path.exists(self.params.output_dir + "/metadata.json") and
                        os.path.isfile(self.params.output_dir + "/metadata.json")):
                    with open(self.params.output_dir + "/metadata.json", "r", encoding="utf-8") as file:
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
            self.spinner.set_failure_spinner("Error in ParseDescriptionPlanner.run() is occurred.", e)
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
        if os.path.exists(path):
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    structure[entry] = self.__get_project_structure(full_path)  # Recursively process subdirectories
                else:
                    structure[entry] = None  # Files are represented as `None`
        return structure

    def __generate_and_send_actions_prompt(self) -> str:
        if self.is_new_actions_session:
            goals = "".join([goal.get_goal() for goal in self.goals])
            project_structure = json.dumps(self.project_structure, indent=4)
            tasks = [(f"\nTasks: \n"
                f"Analyze the goals, metadata(if exists) "
                "output project path, output project structure, list of tools, ignore list, list of replacements, description.\n"
                "Generate a set of actions to achieve the goals using the parameters above.\n"
                "Main steps: \n"
                "1. if necessary, create new components (folders or files)(IMPORTANT! Carefully analyze the description and select a complete set of actions to perform the tasks described there).\n"
                "IMPORTANT! Generate a complete list of operations for creating folders or files based on the description and tasks in it.\n"
                "2. if necessary, update or expand existing components based on the tasks from description\n"
                "3. After that, generate a list of edit_content actions.\n\n"
                "Some comments to steps: \n"
                "Based on the description, you need to perform tasks to update(expand) the project, components or files or add a new component to the structure or delete component.\n"
                f"Pay attention to the {ToolTypes.CREATE_FILE} and  {ToolTypes.CREATE_DIR} tool. Also an important point. If the description contains a task to create some component, file and it needs to be filled with content, then this tool must be in the list of actions.\n"),
                ("User Guide for Tools: \n"
                "Use copy and rename tools to update output project structure based on replacements.\n"            
                "Copy and rename tools should return source and destination(rename destination should be updated from replacements list).\n"
                f"In {ToolTypes.EDIT_CONTENT} and {ToolTypes.CREATE_FILE} tools provide path and prompt(a short description of what should be in this file (class name, description of methods, logic, frameworks, libraries, dependencies, programming language, etc).\n"
                "This parameter will be used as a prompt to generate the content of this file) in the tool_params.\n"
                "Fill in this parameter only in cases when a new file and content is created or an existing file needs to be updated by adding new content or logic based on the description.\n"
                "If replacements occur, the path must be updated based on the search and the replace(this is an important part) also in this case, in the tool_params, you need to enter the old_path before the replacement for the further possibility of updating the content in the file\n"
                "If you need to update some existing file to perform the tool, specify upd_content=true in the tool_params. Also should updated imports if necessary\n"
                "Also specify in these prompts the libraries and the language with which you need to implement from description above.\n")]
            expected = Action.get_prompt()
            prompts = [f"Strategy goals for planning block:\n{goals} \n\n",
                    f"Description:\n {self.metadata.get("task", "") or ""} \n\n",
                    f"Project Metadata: \n {self.template_metadata or ""} \n\n",
                    f"Output Project path:\n {self.params.output_dir} \n\n",
                    f"Output Project structure:\n {project_structure} \n\n",
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

            return self.__send_actions_prompt(f"Check the result, check a full coverage of all tasks by a set of tools, pay attention with {ToolTypes.EDIT_CONTENT} and creating and renaming tools\n"
                                                "Provide only resulting json without your clarification on what you did.")
        else:
            task = ("Analyze the message history, incoming data and params, goals, tasks, expected result and using the whole context perform the next task.\n"
                    f"Task:\n {self.metadata.get("task", "") or ""} \n\n"
                    "Provide only resulting json without your clarification on what you did.")
            return self.__send_actions_prompt(task)

    def __get_actions(self, response: str) -> list[Action]:
        all_actions = json.loads(response)
        actions = list(filter(lambda x: x["tool_name"] != ToolTypes.EDIT_CONTENT and x["tool_name"] != ToolTypes.CREATE_FILE, all_actions))
        edit_content_actions = list(filter(lambda x: x["tool_name"] == ToolTypes.EDIT_CONTENT, all_actions))
        create_file_actions = list(filter(lambda x: x["tool_name"] == ToolTypes.CREATE_FILE, all_actions))
        if len(edit_content_actions) > 0:            
            edit_content_actions = self.__edit_content(edit_content_actions)
        if len(create_file_actions) > 0:
            create_file_actions = self.__edit_content(create_file_actions)
        return actions + create_file_actions + edit_content_actions

    def __edit_content(self, actions: list[Action]) -> list[Action]:
        def process_and_update_action(idx, action):
            try:
                # Process file and get new content
                old_file_path = action["tool_params"].get("old_path")
                file_path = action["tool_params"].get("path")
                upd_content = action["tool_params"].get("upd_content") or False
                prompt = action["tool_params"].get("prompt") or action["tool_params"].get("content") or ""
                if not file_path:
                    raise ValueError("File path is missing in action")
                new_content = self.__process_file(old_file_path, file_path, prompt, upd_content)
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

    def __process_file(self, old_file_path: str, file_path: str, prompt: str, upd_content = False) -> str:
        new_content = ""
        if len(self.params.replacements) > 0 and old_file_path is not None and os.path.exists(old_file_path) and upd_content:
            try:
                with open(old_file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    new_content = self.__upd_content(content, prompt, True)
            except Exception as e:
                if self.verbose:
                    self.logger.fatal(None, e, f"Code 1 - error processing file at {file_path}: {e}")
        else:
            try:
                if upd_content:
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        new_content = self.__upd_content(content, prompt)
                else:
                    new_content = self.__upd_content("", prompt)
            except Exception as e:
                if self.verbose:
                    self.logger.fatal(None, e, f"Code 1 - error processing file at {file_path}: {e}")
        return new_content

    def __upd_content(self, content: str, task: str, replacements_prompt = False):
        prompt = ""
        if len(content) > 0:
            if replacements_prompt:
                prompt += self.__get_replacements_prompt(content, task)
            else:
                prompt += (f"Task: \n{task}\n"
                           f"File content: \n{content}\n")
        else:
            prompt += (f"Task: \n{task}\n")
        prompt += "Provide only updated text without your clarification what you did"
        return self.__send_prompt(prompt)

    def __get_replacements_prompt(self, content: str, task = ""):
        prompt = f"Here is a text from a file:\n{content}\n\n"
        for replacement in self.params.replacements:
            prompt += f"Replace all occurrences of '{replacement['search']}' with '{replacement['replace']}'.\n"
        prompt += task
        return prompt

    def __send_prompt(self, prompt: str) -> str:
        session = self.ai_model.create_session(session_id=self.metadata.get("session_id", None) or None)
        session.add_role("system", "You are a versatile content editor and generator specializing in code. Your task is to review and edit existing files or create new content based on user requirements. You handle backend, frontend, tests, DevOps scripts, and other coding needs across various languages, platforms, and frameworks. Ensure the code is optimized, clean, and follows best practices. For edits, highlight changes and explain your reasoning in the comments. For new content, ensure it is well-documented, efficient, and aligned with the specified requirements.").add_role("user", prompt)
        return session.send_prompt()
