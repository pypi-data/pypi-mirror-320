"""A pytest plugin for running and analyzing LLM evaluation tests."""

from .plugin import *  # noqa
from .models import EvalResult as EvalResult
from .ipython_extension import load_ipython_extension

__all__ = ["EvalResult", "load_ipython_extension"]
