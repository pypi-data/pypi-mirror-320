# %%
from functools import wraps

import joblib
import joblib.func_inspect


def function():
    return 1


@wraps(function)
def function_wrapper():
    return function()


joblib.func_inspect.get_func_code(function_wrapper)
