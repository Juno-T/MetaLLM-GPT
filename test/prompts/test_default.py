from base_modules.interface import CodeBlob
from base_modules.prompts.default import prompt_settings
from langchain.schema import PromptValue

from .base import type_check, handling_codeblobs

def test_simple():
    prompter = prompt_settings(None, None, "my_objective", False, None)
    type_check(prompter)

def test_codeblobs():
    prompter = prompt_settings(None, None, "my_objective", False, None)
    handling_codeblobs(prompter)
