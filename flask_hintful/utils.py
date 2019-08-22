from inspect import getdoc, signature
from typing import Callable


def get_func_sig(func: Callable) -> dict:
    sig = signature(func, follow_wrapped=True)
    return {
        "return": sig.return_annotation,
        "params": sig.parameters,
        "doc": getdoc(func),
        "empty": sig.empty
    }
