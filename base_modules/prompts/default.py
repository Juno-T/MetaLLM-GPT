from typing import Optional
from copy import deepcopy
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from base_modules.interface import CodeBlob
from base_modules.prompts.common import format_prompt_template

base_prompt = ChatPromptTemplate.from_messages([SystemMessagePromptTemplate.from_template("""
You are a programming expert.
The code should always include at least one function call inside it to demonstrate an execution
For your response, you should strictly follow the format
``` python
<python code that includes at least one function call to demonstrate an execution>
```
<Explanation about the generated code>
You should always write all of the codes you generated in a single block. Any python codes in your response should always start with "``` python" and end with "```".
You should always include the full code in your response, instead of simply the modified part of the code or the function call.
You are forbidden to only include the modified part of the code in your response.
You are forbidden to only include the function call of the code in your response.
If your code is a python script, then your code should not require any user input.
The user is not using any notebook environment. You are forbidden to include any exclamation mark in the code.
Do not include any 'argparse' in the code.
Do not include any 'try or except' in the code.
Do not include any '__name__' in the code.
If a module is repeatedly missing after multiple attempts, you should switching to other modules.
The objective of the code is to {objective}.
""")
])

input_prompt = ChatPromptTemplate.from_messages([
SystemMessagePromptTemplate.from_template("""
The input arguments given to the function call is: {input}
""")
])
output_prompt = ChatPromptTemplate.from_messages([
SystemMessagePromptTemplate.from_template("""
The standard output the python code should generate should be {output}
""")
])
privilege_prompt = ChatPromptTemplate.from_messages([
SystemMessagePromptTemplate.from_template("""
You can use any python packages. When installing additional packages, use os.system('pip install package_name') and you cannot use !pip install.
For example, os.system('pip install numpy'). Your message should include os.system('pip install package_name') and the rest of the codes in the same markdown block.
""")
])
not_privilege_prompt = ChatPromptTemplate.from_messages([
SystemMessagePromptTemplate.from_template("""
Do not include any 'pip install' in the code
""")
])
environment_prompt = ChatPromptTemplate.from_messages([
SystemMessagePromptTemplate.from_template("""
The available python modules for the code only built-in python modules and the base_modules in the list: {environment}
""")
])
not_environment_prompt = ChatPromptTemplate.from_messages([
SystemMessagePromptTemplate.from_template("""
The available python modules for the code only include the built-in python modules.
The code in your generated response should not include any extra python packages.
""")
])

improve_prompt_with_output = ChatPromptTemplate.from_messages([
SystemMessagePromptTemplate.from_template("""
The standard output of the current code is:
{stdout}
"""), 
HumanMessagePromptTemplate.from_template("""
Improve the code: {code}
The objective of the code is to {objective}.
Check whether the standard output of the current code fits the objective of the code.
The code should always include at least one function call inside it to demonstrate an execution.
If my code does not contain at least one function call inside the code, you should always add at least one function call inside the code.
"""),
SystemMessagePromptTemplate.from_template("""
If my code does not contain at least one function call inside the code, you should 
always add at least one function call inside the original code.
""")
])
improve_prompt_without_output = ChatPromptTemplate.from_messages([
SystemMessagePromptTemplate.from_template("""
The standard output of the current code is:
{stdout}
"""), 
HumanMessagePromptTemplate.from_template("""
Improve the code: {code}
The objective of the code is to {objective}.
The code should always include at least one function call inside it to demonstrate an execution.
If my code does not contain at least one function call inside the code, you should always add at least one function call inside the code"
"""),
SystemMessagePromptTemplate.from_template("""
If my code does not contain at least one function call inside the code, you should 
always add at least one function call inside the original code.
""")
])

debug_prompt = ChatPromptTemplate.from_messages([
SystemMessagePromptTemplate.from_template("""
The error message of the current code is: {error}
The traceback of the exception is: {tb}
"""),
HumanMessagePromptTemplate.from_template("""
Debug the code:
{code}
The code should always include at least one function call inside it to demonstrate an execution.
You should consider the error message:
{error}
""")
])

create_prompt = ChatPromptTemplate.from_messages([
HumanMessagePromptTemplate.from_template("""
Create the code for me. The objective of the code is to {objective}.
The code should always include at least one function call inside it to demonstrate an execution
""")
])

kill_prompt = ChatPromptTemplate.from_messages([
HumanMessagePromptTemplate.from_template("""
The code {code} takes too long to run, modify the code so that it takes shorter time to finish. The objective of the code is to {objective}.
""")
])

class prompt_settings:
    def __init__(self, Input, Output, Objective, Privilege, Environment):
        self.Input = Input
        self.Output = Output
        self.Objective = Objective
        self.Privilege = Privilege
        self.Environment = Environment

    def generate_prompt(self, prev_codeblob: Optional[CodeBlob]=None):
        prompt = self.construct_base_prompt()
        if prev_codeblob is not None:
            if prev_codeblob.execution_killed:
                Mode = "Killed"
            else:
                if prev_codeblob.buggy:
                    Mode = "Debug"
                else:
                    Mode = "Improve"
        else:
            Mode = "Create"
        if Mode == "Debug":
            prompt += debug_prompt

        if Mode == "Improve":
            if self.Output is not None:
                prompt += improve_prompt_with_output
            else:
                prompt += improve_prompt_without_output
    
        if Mode == "Create":
            prompt += create_prompt

        if Mode == "Killed":
            prompt += kill_prompt
        
        return format_prompt_template(
            prompt, 
            prev_codeblob, 
            objective=self.Objective,
            input=self.Input,
            output=self.Output,
            environment=self.Environment,)

    def construct_base_prompt(self):
        prompt = deepcopy(base_prompt)
        if self.Input is not None:
            prompt += input_prompt

        if self.Output is not None:
            prompt += input_prompt

        if self.Privilege:
            prompt += privilege_prompt
        else:
            prompt += not_privilege_prompt
            if self.Environment is None:
                prompt += not_environment_prompt
            else:
                prompt += environment_prompt
        return prompt