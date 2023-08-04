import os
from base_modules.code_generator import MetaLLM_GPT

def main(
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
    verbose=False
):
    code_generator = MetaLLM_GPT(
        objective = objective,
        file_path = file_path,
        minimum_trial = minimum_trial,
        resume = resume,
        input=input,
        output=output,
        exec_time_limit_s=exec_time_limit_s,
        privilege=privilege,
        environment=environment,
        infinity_mode=infinity_mode,
        key=key,
        model=model,
        api_call_period_s=api_call_period_s,
        verbose=verbose)

    return code_generator.run()

if __name__ == "__main__":
    main(
        objective="a program that output some funny joke",
        file_path="exp/joke.py",
        minimum_trial=2,
        output="1 random funny joke from 10 jokes as stdout",
        key=os.environ.get("OPENAI_API_KEY"),
    )