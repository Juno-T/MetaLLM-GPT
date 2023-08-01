from typing import Optional
import warnings
from base_modules.interface import CodeBlob
from langchain.prompts import PromptTemplate
from langchain.schema import PromptValue

def format_prompt_template(prompt_template: PromptTemplate, codeblob: Optional[CodeBlob], **kwargs) -> PromptValue:
    if codeblob is None:
        codeblob = CodeBlob()
    # remove duplicated keys from kwargs
    for key in codeblob._fields:
        if key in kwargs:
            warnings.warn(f"Key '{key}' is duplicated in codeblob and kwargs. Removing from kwargs.")
            del kwargs[key]
    return prompt_template.format_prompt(
        code=codeblob.code,
        stdout=codeblob.stdout,
        error=codeblob.error,
        tb=codeblob.tb,
        buggy=codeblob.buggy,
        execution_killed=codeblob.execution_killed,
        execution_time=codeblob.execution_time,
        environment=codeblob.environment,
        **kwargs
    )