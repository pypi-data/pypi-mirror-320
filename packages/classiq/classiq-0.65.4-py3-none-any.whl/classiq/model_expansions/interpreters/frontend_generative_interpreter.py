from classiq.interface.model.quantum_function_call import QuantumFunctionCall

from classiq.model_expansions.closure import FunctionClosure, GenerativeFunctionClosure
from classiq.model_expansions.interpreters.generative_interpreter import (
    GenerativeInterpreter,
)
from classiq.model_expansions.quantum_operations.quantum_function_call import (
    DeclarativeQuantumFunctionCallEmitter,
)
from classiq.model_expansions.scope import Scope


class FrontendGenerativeInterpreter(GenerativeInterpreter):
    def emit_quantum_function_call(self, call: QuantumFunctionCall) -> None:
        DeclarativeQuantumFunctionCallEmitter(self).emit(call)

    def _get_main_closure(self, main_func: FunctionClosure) -> FunctionClosure:
        if isinstance(main_func, GenerativeFunctionClosure):
            return GenerativeFunctionClosure.create(
                name=main_func.name,
                positional_arg_declarations=main_func.positional_arg_declarations,
                scope=Scope(parent=self._top_level_scope),
                expr_renamer=self.get_main_renamer(),
                _depth=0,
                generative_blocks={"body": main_func.generative_blocks["body"]},
            )

        return super()._get_main_closure(main_func)
