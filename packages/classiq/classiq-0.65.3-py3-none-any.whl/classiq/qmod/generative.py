from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Optional

from classiq.interface.exceptions import ClassiqError
from classiq.interface.generator.expressions.expression import Expression

if TYPE_CHECKING:
    from classiq.model_expansions.interpreters.base_interpreter import BaseInterpreter

_GENERATIVE_MODE: bool = False
_FRONTEND_INTERPRETER: Optional["BaseInterpreter"] = None


def is_generative_mode() -> bool:
    return _GENERATIVE_MODE


@contextmanager
def generative_mode_context(generative: bool) -> Iterator[None]:
    global _GENERATIVE_MODE
    previous = _GENERATIVE_MODE
    _GENERATIVE_MODE = generative
    try:
        yield
    finally:
        _GENERATIVE_MODE = previous


def set_frontend_interpreter(interpreter: "BaseInterpreter") -> None:
    global _FRONTEND_INTERPRETER
    _FRONTEND_INTERPRETER = interpreter


def get_frontend_interpreter() -> "BaseInterpreter":
    if _FRONTEND_INTERPRETER is None:
        raise ClassiqError("Interpreter was not set")
    return _FRONTEND_INTERPRETER


def interpret_expression(expr: str) -> Any:
    return get_frontend_interpreter().evaluate(Expression(expr=expr)).value
