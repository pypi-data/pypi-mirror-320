# pyright: reportPossiblyUnboundVariable=false
import logging
from functools import wraps
from time import perf_counter
from typing import Callable, Optional, TypeVar, Union, overload

try:
    import torch

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

logger = logging.getLogger("fastdev")
T = TypeVar("T", bound=Callable)


class timeit:
    """
    Measure the time of a block of code.

    Args:
        print_tmpl (str, optional): The template to print the time. Defaults to None. Can be a
             string with a placeholder for the time, e.g., "func foo costs {:.5f} s" or a
             string without a placeholder, e.g., "func foo".

    Examples:
        >>> # doctest: +SKIP
        >>> with timeit():
        ...     time.sleep(1)
        it costs 1.00000 s
        >>> @timeit
        ... def foo():
        ...     time.sleep(1)
        foo costs 1.00000 s
        >>> @timeit("func foo")
        ... def foo():
        ...     time.sleep(1)
        func foo costs 1.00000 s
    """

    _has_tmpl: bool
    _print_tmpl: str
    _start_time: float

    @overload
    def __new__(cls, fn_or_print_tmpl: T) -> T: ...  # type: ignore
    @overload
    def __new__(cls, fn_or_print_tmpl: Optional[str] = None) -> "timeit": ...  # type: ignore
    def __new__(cls, fn_or_print_tmpl: Optional[Union[T, str]] = None) -> Union[T, "timeit"]:  # type: ignore
        instance = super().__new__(cls)
        if callable(fn_or_print_tmpl):  # handle case when decorator is used without parentheses
            instance._has_tmpl = False
            instance._print_tmpl = str(fn_or_print_tmpl.__name__) + " costs {:.5f} s"
            return instance(fn_or_print_tmpl)  # type: ignore
        return instance

    def __init__(self, fn_or_print_tmpl: Optional[Union[Callable, str]] = None):
        if callable(fn_or_print_tmpl):
            return  # skip initialization if called from __new__ with a function

        has_tmpl = fn_or_print_tmpl is not None
        if has_tmpl:
            # no placeholder in print_tmpl
            if "{" not in fn_or_print_tmpl and "}" not in fn_or_print_tmpl:  # type: ignore
                print_tmpl = fn_or_print_tmpl + " costs {:.5f} s"  # type: ignore
            else:
                print_tmpl = fn_or_print_tmpl  # type: ignore
        else:  # default template
            print_tmpl = "it costs {:.5f} s"
        self._has_tmpl = has_tmpl
        self._print_tmpl = print_tmpl

    def __enter__(self):
        self._start_time = perf_counter()

    def __exit__(self, exec_type, exec_value, traceback):
        logger.info(self._print_tmpl.format(perf_counter() - self._start_time))

    def __call__(self, func: T) -> T:
        if not self._has_tmpl:
            self._print_tmpl = str(func.__name__) + " costs {:.5f} s"

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper  # type: ignore


class cuda_timeit(timeit):
    """
    Measure the time of a block of code that may involve CUDA operations. We use CUDA events
    and synchronization for the accurate measurements.

    Args:
        print_tmpl (str, optional): The template to print the time. Defaults to None. Can be a
             string with a placeholder for the time, e.g., "func foo costs {:.5f} s" or a
             string without a placeholder, e.g., "func foo".
    """

    def __init__(self, print_tmpl: Optional[str] = None):
        super().__init__(print_tmpl)
        if not _TORCH_AVAILABLE or not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available")

        self._start_event = torch.cuda.Event(enable_timing=True)
        self._end_event = torch.cuda.Event(enable_timing=True)

    def __enter__(self):
        # Ref: https://pytorch.org/tutorials/intermediate/torch_compile_tutorial.html#demonstrating-speedups
        self._start_event.record()  # type: ignore

    def __exit__(self, exec_type, exec_value, traceback):
        self._end_event.record()  # type: ignore
        torch.cuda.synchronize()
        logger.info(self._print_tmpl.format(self._start_event.elapsed_time(self._end_event) / 1e3))


__all__ = ["timeit", "cuda_timeit"]
