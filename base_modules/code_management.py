import io
import time
from contextlib import redirect_stdout
import traceback
import multiprocessing
from pathlib import Path

from base_modules.interface import CodeBlob


class FileManager():
    def __init__(self, file_path, output=None, verbose=False):
        self.file_path = file_path
        self.verbose = verbose
        self.output = output

    def read(self):
        file = open(self.file_path, "r")
        line_list = file.readlines()
        if self.verbose:
            print("raw string line by line:")
            for line in line_list:
                print(repr(line))
        combined_raw_code = "".join(str(item) for item in line_list)
        if self.verbose:
            print("raw string combined:")
            print("combined raw code", repr(combined_raw_code))
        return combined_raw_code

    def write(self, the_code):
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
        f = open(self.file_path, "w")
        f.write(the_code)
        f.close()

def execute(
    ret_dict,
    code: str,
    output_required=False,
    capture_error=False,
    output_length_limit=None,
    ignore_warning=False
):
    try:
        ret_dict["code"] = code
        compiled_code = compile(code, 'code_to_be_compiled', 'exec')
        f = io.StringIO()
        with redirect_stdout(f):
            s = time.time()
            exec(compiled_code, {})
            e = time.time()
        ret_dict["execution_time"] = e - s
        stdout = f.getvalue()
        ret_dict["stdout"] = str(stdout)
        print("The code runs smoothly")

        if output_length_limit is not None:
            if len(stdout) > output_length_limit:
                print(f"Warning: The length of the standard output is too long, \
                                    MetaLLM-GPT only considers the last {output_length_limit} strings of the "
                        f"standard output.")
                stdout = stdout[-output_length_limit:]

        if output_required and ("save" or "show") not in code:
            if len(stdout) == 0:
                print("However, the code lacks a function call or valid output")
            else:
                print("Output of the code:\n" + stdout)

    except Exception as e:
        if capture_error:
            ret_dict["error"] = str(e)
            # self.past_error_history.append(self.error)
            ret_dict["tb"] = str(traceback.format_exc())

        if e.__class__.__name__ == 'ModuleNotFoundError':
            if not ignore_warning:
                print("The generated code cannot be tested due to missing packages. It is advised to either change "
                        "the objective, describe your current environment, or install the missing packages before "
                        "proceeding with MetaLLM-GPT")
            if capture_error:
                print("The error message is:", ret_dict["error"])
        else:
            print("The code is buggy")
            if capture_error:
                print(ret_dict["tb"])
        ret_dict["buggy"] = True
    

def overtime_kill(target_function, target_function_args=None, time_limit=60, ret=True, overhead_s = 2):
    # converting this function into a decorator might make it less convenient

    ret_dict = multiprocessing.Manager().dict()

    if target_function_args is not None:
        p = multiprocessing.Process(target=target_function, args=(ret_dict,) + target_function_args)
    elif ret:
        p = multiprocessing.Process(target=target_function, args=(ret_dict,))
    else:
        p = multiprocessing.Process(target=target_function)

    p.start()
    p.join(overhead_s + time_limit)
    if p.is_alive():
        print(f"The execution of the code takes longer than {overhead_s + time_limit} seconds, terminating the execution...")
        p.terminate()
        p.join()
        killed = True
    else:
        killed = False
        print("The execution of the code finishes in time")
    
    ret_dict = dict(ret_dict)
    kwargs = {k: v for k,v in ret_dict.items() if k in CodeBlob._fields}
    kwargs["execution_killed"] = killed
    if not "execution_time" in kwargs:
        kwargs["execution_time"] = time_limit
    return CodeBlob(**kwargs)
