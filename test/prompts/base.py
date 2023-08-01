from base_modules.interface import CodeBlob
from base_modules.prompts.default import prompt_settings
from langchain.schema import PromptValue

def type_check(prompter: prompt_settings):
    codeblob = CodeBlob(
        code="my_code",
        stdout="my_stdout",
        error="my_error",
        tb="my_tb",
        buggy=True,
        execution_killed=False,
        execution_time=0.0,
        environment=None
    )
    prompt = prompter.generate_prompt(codeblob)
    assert isinstance(prompt, PromptValue)

def handling_codeblobs(prompter: prompt_settings):
    codeblob_cases = [
        # Bug-free
        CodeBlob(
            code="my_code",
            stdout="my_stdout",
            execution_killed=False,
            execution_time=1
        ),
        # Buggy
        CodeBlob(
            code="my_code",
            stdout="my_stdout",
            error="my_error",
            tb="my_tb",
            buggy=True,
            execution_killed=False,
            execution_time=0.0,
            environment=None
        ),
        # killed
        CodeBlob(
            code="my_code",
            buggy=False,
            execution_killed=True,
            execution_time=10.0
        ),
    ]
    for cb in codeblob_cases:
        prompt = prompter.generate_prompt(cb)
        print(type(prompt))
        assert isinstance(prompt, PromptValue)