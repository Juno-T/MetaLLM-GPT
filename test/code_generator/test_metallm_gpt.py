from base_modules.code_generator import MetaLLM_GPT
from base_modules.interface import CodeBlob

class DummyLLMResponse:
    def __init__(self, content):
        self.content = content

def get_dummy_llm(static_response):
    def dummy_llm(prompt):
        return DummyLLMResponse(content=static_response)
    return dummy_llm

def wrap_codeblock(code: str):
    return f"``` python\n{code}\n```\n"

def test_dummy_llm():
    stdout = "hello world"
    assert stdout == "hello world"
    dummy_code = f"print(\"{stdout}\")"
    dummy_llm = get_dummy_llm(wrap_codeblock(dummy_code)+"\nSome explanation.\n")

    assert isinstance(dummy_llm("whatever").content, str)

    code_generator = MetaLLM_GPT(
        objective = "what ever",
        file_path = "exp/test/dummy_llm.py",
        minimum_trial = 5,
        resume = False,
        input=None,
        output="whatever",
        key=None,
        model=dummy_llm,
        exec_time_limit_s=1,
        api_call_period_s=0.05,
        verbose=False)
    print("init done")

    codeblob = code_generator.run()
    assert isinstance(codeblob, CodeBlob)
    assert codeblob.code.strip("\n") == dummy_code.strip("\n")
    assert codeblob.stdout.strip("\n") == stdout.strip("\n")
    assert codeblob.buggy == False
    assert codeblob.execution_killed == False