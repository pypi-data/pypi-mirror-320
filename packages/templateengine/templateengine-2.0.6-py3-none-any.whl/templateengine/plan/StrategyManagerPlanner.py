import json

from ..plan.CommonPlanner import CommonPlanner
from ..exec.Action import Action
from ..ai.OpenAISession import OpenAISession
from ..strategy.StrategyAction import StrategyAction

class StrategyManagerPlanner(CommonPlanner):
    actions_session: OpenAISession = None
    template_project_structure = None
    project_structure = None
    template_metadata = None

    def __init__(self):
        super().__init__()

    def run(self) -> list[Action] | list[StrategyAction]:
        self.__init_actions_session()
        self.spinner.reset_spinner()
        try:
            self.spinner.start()
            # Step 1: Generate and send prompt
            if self.verbose:
                self.logger.info(None, "Generating and Sending prompt to generate strategy actions...")
            response = self.__generate_and_send_actions_prompt()

            # Step 2: Process actions
            if self.verbose:
                self.logger.info(None, "Generate strategy actions...")
            actions = json.loads(response)

            self.spinner.set_success_spinner("Generating strategy actions completed successfully!")
        except Exception as e:
            self.spinner.set_failure_spinner("Error in StrategyManagerPlanner.run() is occurred.", e)
            raise e
        finally:
            self.spinner.stop()
        return actions

    def __init_actions_session(self) -> None:
        self.ai_model.delete_sessions()
        self.actions_session = self.ai_model.create_session(None)
        self.actions_session.add_role("system",
                                      "You are a strategic planner and analyst. Your task is to evaluate metadata, input parameters, and user prompts to generate a structured actions plan. Your focus is on aligning actions with strategic goals and ensuring clarity in the steps required.")

    def __send_actions_prompt(self, prompt: str) -> str:
        self.actions_session.add_role("user", prompt)
        return self.actions_session.send_prompt()

    def __generate_and_send_actions_prompt(self) -> str:
        tasks = [(f"Tasks: \n"
            f"Analyze the strategies and their goals, description and tasks set in it and input parameters.\n"
            "Break the description into logical blocks and select from the list of strategies those that are suitable for completing the tasks in these blocks.\n"
            "metadata in StrategyAction should contain input_params -> copy input params from prompt and desc_block -> logical block which was obtained from splitting the description, task and session_id.\n"
            "task -> a detailed description of the logical part that the strategy must fulfill"
            "(describe in detail what needs to be done, what to create, what to change or remove, correct names of classes, functions, files, packages, components, subcomponents. Also indicate the programming language and technologies, frameworks and dependencies)\n"            
            "You can supplement the existing description, but you cannot remove important parts and tasks from it(which component or components to create, modify, extend, or delete. ).\n"
            "This task will be used in the planner like prompt in the corresponding strategy to form actions that will allow you to fulfill all the goals in the strategy.\n"
            "session_id -> Session ID for working with AI for storing messages history. \n"
            "Based on the set of actions and selected strategies, tasks and descriptions and broken logical blocks, this field will either be generated using 128-bit random unique ID generation or if the selected strategies and tasks that they will perform can use the same context and can be dependent on each other, then use the same session ID also generated using 128-bit random unique ID generation.\n"
            "Generate a json object based on the expected result described above.\n"
            """An example of the result: [{"strategy_name": ..., "metadata": {}}, ...]"""
            "\nComments on the formation of the result:\n"
            "If you decide to use a 'create-skeleton' strategy then it should have the highest priority and go first.")]
        expected = StrategyAction.get_prompt()
        prompts = [f"Strategies and goals for planning block:\n{json.dumps(self.tools)} \n\n",
                   f"Description:\n {self.params.specs["description"] or ""} \n\n",
                   f"Input params: \n {self.params.toJSON()} \n\n",
                   f"{expected}\n\n"]
        prompts.extend(tasks)

        return_yes = "Print Yes if understand."
        for prompt in prompts:
            r = self.__send_actions_prompt(prompt + return_yes)
            if "Yes" in r:
                continue
            else:
                break

        return self.__send_actions_prompt(f"Check the result.\n"
                                              "Generate and Provide only resulting json without your clarification on what you did.")