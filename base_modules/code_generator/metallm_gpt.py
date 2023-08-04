import re
import traceback
import time

from langchain.chat_models import ChatOpenAI

from base_modules.prompter.default import prompt_settings
from base_modules.code_management import FileManager
from base_modules.code_management import overtime_kill, execute
from base_modules.interface import CodeBlob


class MetaLLM_GPT:
    def __init__(
        self,
        objective,
        file_path,
        minimum_trial,
        resume=False,
        input=None,
        output=None,
        exec_time_limit_s=60,
        privilege=False,
        environment=None,
        infinity_mode=False,
        key=None,
        model="3.5",
        api_call_period_s=5,
        verbose=False,
    ):
        self.objective = objective
        self.file_path = file_path
        self.minimum_trial = minimum_trial
        self.resume = resume
        self.input = input
        self.output = output
        self.exec_time_limit_s = exec_time_limit_s
        self.privilege = privilege
        self.environment = environment
        self.infinity_mode = infinity_mode
        self.key = key
        self.verbose = verbose

        self.trial_count = 0
        self.previous_start = time.time() - api_call_period_s
        self.api_call_period_s = api_call_period_s
        self.prev_code_str = ""

        if isinstance(model, str):
            if model == "3.5":
                model = "gpt-3.5-turbo"
            elif model == "4":
                model = "gpt-4"
            self.llm = ChatOpenAI(
                model=model,
                openai_api_key=self.key,
                max_retries=1,
                max_tokens=None,
            )
        else:
            self.llm = model

        self.code_io = FileManager(
            self.file_path, output=self.output, verbose=self.verbose
        )
        self.prompter = prompt_settings(
            self.input, self.output, self.objective, self.privilege, self.environment
        )

    def run(self):
        if self.verbose:
            print(
                "Monitoring attributes:",
                self.trial_count,
                self.minimum_trial,
                self.output,
                self.infinity_mode,
            )
        while True:
            try:
                self.trial_count += 1
                print(f"---------Iteration {self.trial_count} starts!---------")

                self.wait_if_needed()
                codeblob = None
                print("Thinking right now...")
                prompt = self.prompter.generate_prompt(codeblob).to_messages()
                response_txt = self.call_LLM(prompt)
                code_str = self.prompter.parse_code(response_txt)
                codeblob = None
                if(self.test_length(response_txt)):
                    self.code_io.write(code_str)
                    # code = self.code_io.read()
                    codeblob = self.run_and_test_code(code_str)
                else:
                    print(f"---------Iteration {self.trial_count} failed!---------")
                    print("Reason of failure: The modified code is too short, change aborted")
                    continue

                if self.verbose:
                    print(f"{codeblob=}")
                if self.check_termination(codeblob):
                    print("MetaLLM-GPT reaches the termination criteria!")
                    return codeblob
                print(f"---------Iteration {self.trial_count} succeeded!---------")
            except Exception as fail:
                time.sleep(1)
                print(f"---------Iteration {self.trial_count} failed!---------")
                print("Reason of failure:", str(traceback.format_exc()))

    def check_termination(self, codeblob: CodeBlob) -> bool:
        return (
            codeblob is not None
            and not codeblob.buggy
            and not codeblob.execution_killed
            and self.trial_count > self.minimum_trial
            and not self.infinity_mode
            and (
                len(codeblob.stdout) != 0
                or self.output is None
            )
        )

    def run_and_test_code(self, code_str: str) -> CodeBlob:
        output_required = self.output is not None
        codeblob = overtime_kill(
            execute,
            target_function_args=(
                code_str,
                output_required,
                True,
                2000,
                self.privilege,
            ),
            time_limit=self.exec_time_limit_s,
        )
        return codeblob

    def call_LLM(self, prompt):
        response = self.llm(prompt)
        response_txt = response.content
        # TODO: log token usage here
        print("modification during this iteration:\n", response_txt)

        if self.verbose:
            print("type of the raw response:", type(response))
            print("raw response:", repr(response))

        self.resume = True
        return response_txt

    def test_length(self, code_str):
        if not len(code_str) >= 0.5 * len(self.prev_code_str):
            return False
        else:
            self.prev_code_str = code_str
            return True

    def wait_if_needed(self):
        now = time.time()
        time_left = self.api_call_period_s - (now - self.previous_start)
        if time_left >= 0:
            print(f"Waiting for {time_left} seconds to avoid API overuse.")
            time.sleep(time_left + 0.1)

        self.previous_start = time.time()