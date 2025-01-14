from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, TypeVar, Optional, Tuple, Set, NamedTuple

import networkx as nx

from wake.analysis.utils import pair_function_call_arguments
from wake.core import get_logger
from wake.ir import SourceUnit, VariableDeclaration, ExternalReference, UnaryOperation, BinaryOperation, \
    IdentifierPathPart, FunctionCall, MemberAccess, Identifier, Literal, ExpressionAbc, Assignment, IndexAccess, \
    EventDefinition, ErrorDefinition, FunctionDefinition, EnumValue, VariableDeclarationStatement, TupleExpression, \
    ContractDefinition, FunctionCallOptions, ElementaryTypeNameExpression, Conditional, StructDefinition, \
    UserDefinedTypeName, ArrayTypeName, ElementaryTypeName, FunctionTypeName, Mapping, IndexRangeAccess, Return, \
    NewExpression, ModifierDefinition, ModifierInvocation
from wake.ir.enums import FunctionCallKind, GlobalSymbol, FunctionKind, UnaryOpOperator
from wake.utils import StrEnum
from wake.utils.keyed_default_dict import KeyedDefaultDict

logger = get_logger(__name__, logging.DEBUG)


T = TypeVar("T")


class ConditionKind(StrEnum):
    IS_TRUE = "is_true"
    IS_FALSE = "is_false"


class ConditionalNode(NamedTuple):
    node: DdgNode
    conditions: Tuple[Tuple[ExpressionAbc, ConditionKind], ...]


def single_or_fail(iterable: Sequence[T]) -> T:
    assert len(iterable) == 1, f"Expected exactly one element, got {len(iterable)}"
    assert iterable[0] is not None, "Expected non-None value"
    return iterable[0]


class DataDependencyGraph:
    _graph: nx.DiGraph
    _variable_declarations_lookup: Dict[Tuple[VariableDeclaration, ...], VariableDdgNode]
    _expressions_lookup: Dict[ExpressionAbc, Set[ConditionalNode]]
    _global_symbols_lookup: Dict[GlobalSymbol, GlobalSymbolDdgNode]
    _enum_values_lookup: Dict[EnumValue, EnumValueDdgNode]

    def __init__(self, source_units: Dict[Path, SourceUnit]):
        def variable_declarations_lookup_factory(vars: Tuple[VariableDeclaration, ...]) -> VariableDdgNode:
            node = VariableDdgNode(vars)
            self._graph.add_node(node)
            return node

        def global_symbols_lookup_factory(global_symbol: GlobalSymbol) -> GlobalSymbolDdgNode:
            node = GlobalSymbolDdgNode(global_symbol)
            self._graph.add_node(node)
            return node

        self._graph = nx.DiGraph()
        self._source_units = source_units
        self._variable_declarations_lookup = KeyedDefaultDict(variable_declarations_lookup_factory)
        self._expressions_lookup = {}
        self._global_symbols_lookup = KeyedDefaultDict(global_symbols_lookup_factory)
        self._enum_values_lookup = {}

        logger.debug("Adding variables to DDG")

        return_statements: List[Return] = []

        for source_unit in source_units.values():
            self._add_variables(source_unit.declared_variables)

            # TODO
            # ErrorDefinition,
            # EventDefinition,
            # FunctionTypeName,
            # ModifierDefinition,
            # VariableDeclarationStatement,
            # TryCatchClause,

            for enum in source_unit.enums:
                for enum_value in enum.values:
                    node = EnumValueDdgNode(enum_value)
                    self._graph.add_node(node)
                    self._enum_values_lookup[enum_value] = node

            for func in source_unit.functions:
                self._add_variables(func.parameters.parameters)
                self._add_variables(func.return_parameters.parameters)

                if func.body is not None:
                    for stmt in func.body.statements_iter():
                        if isinstance(stmt, VariableDeclarationStatement):
                            self._add_variables([decl for decl in stmt.declarations if decl is not None])
                        elif isinstance(stmt, Return):
                            return_statements.append(stmt)

            for contract in source_unit.contracts:
                self._add_variables(contract.declared_variables)

                for enum in contract.enums:
                    for enum_value in enum.values:
                        node = EnumValueDdgNode(enum_value)
                        self._graph.add_node(node)
                        self._enum_values_lookup[enum_value] = node

                for func in contract.functions:
                    self._add_variables(func.parameters.parameters)
                    self._add_variables(func.return_parameters.parameters)

                    if func.body is not None:
                        for stmt in func.body.statements_iter():
                            if isinstance(stmt, VariableDeclarationStatement):
                                self._add_variables([decl for decl in stmt.declarations if decl is not None])
                            elif isinstance(stmt, Return):
                                return_statements.append(stmt)

                for mod in contract.modifiers:
                    self._add_variables(mod.parameters.parameters)

                    if mod.body is not None:
                        for stmt in mod.body.statements_iter():
                            if isinstance(stmt, VariableDeclarationStatement):
                                self._add_variables([decl for decl in stmt.declarations if decl is not None])
                            elif isinstance(stmt, Return):
                                return_statements.append(stmt)

        for vars in list(self._variable_declarations_lookup.keys()):
            self._expand_variable(vars[0])

        for return_statement in return_statements:
            self._process_return(return_statement)

    @property
    def graph(self) -> nx.DiGraph:
        return self._graph.copy(as_view=True)

    def _add_variable(self, var: VariableDeclaration, keys: Optional[List[VariableDeclaration]] = None) -> None:
        if keys is None:
            keys = []
        else:
            node = VariableDdgNode((var,))
            self._graph.add_node(node)
            self._variable_declarations_lookup[(var,)] = node
        keys.append(var)

        type_name = var.type_name
        while not isinstance(type_name, (ElementaryTypeName, FunctionTypeName, UserDefinedTypeName)):
            if isinstance(type_name, ArrayTypeName):
                type_name = type_name.base_type
            elif isinstance(type_name, Mapping):
                type_name = type_name.value_type
            else:
                assert False, f"Unexpected type name: {type_name}"

        if isinstance(type_name, UserDefinedTypeName):
            if isinstance(type_name.referenced_declaration, ContractDefinition):
                for declared_var in type_name.referenced_declaration.declared_variables:
                    self._add_variable(declared_var, list(keys))
            elif isinstance(type_name.referenced_declaration, StructDefinition):
                for member in type_name.referenced_declaration.members:
                    self._add_variable(member, list(keys))

        node = VariableDdgNode(tuple(keys))
        self._graph.add_node(node)
        self._variable_declarations_lookup[tuple(keys)] = node

    def _add_variables(self, vars: Iterable[VariableDeclaration]) -> None:
        for var in vars:
            self._add_variable(var)

    def _process_expression_recursively(self, expr: ExpressionAbc) -> List[Optional[Set[ConditionalNode]]]:
        if isinstance(expr, TupleExpression):
            # TODO can we linearize?
            return [i for c in expr.components for i in (self._process_expression_recursively(c) if c is not None else [None])]  # TODO

        if expr in self._expressions_lookup:
            return [self._expressions_lookup[expr]]

        if isinstance(expr, Literal):
            node = LiteralDdgNode(expr)
            self._expressions_lookup[expr] = {ConditionalNode(node, tuple())}
            return [self._expressions_lookup[expr]]
        elif isinstance(expr, BinaryOperation):
            node = BinaryOperationDdgNode(expr)
            self._expressions_lookup[expr] = {ConditionalNode(node, tuple())}

            left = single_or_fail(self._process_expression_recursively(expr.left_expression))
            right = single_or_fail(self._process_expression_recursively(expr.right_expression))

            for l in left:
                self._graph.add_edge(l.node, node, conditions=l.conditions, side="left")
            for r in right:
                self._graph.add_edge(r.node, node, conditions=r.conditions, side="right")
            return [self._expressions_lookup[expr]]
        elif isinstance(expr, UnaryOperation):
            node = UnaryOperationDdgNode(expr)
            self._expressions_lookup[expr] = {ConditionalNode(node, tuple())}

            sub = single_or_fail(self._process_expression_recursively(expr.sub_expression))

            for s in sub:
                self._graph.add_edge(s.node, node, conditions=s.conditions)
                if expr.operator in {UnaryOpOperator.PLUS_PLUS, UnaryOpOperator.MINUS_MINUS, UnaryOpOperator.DELETE}:
                    self._graph.add_edge(node, s.node, conditions=s.conditions)
            return [self._expressions_lookup[expr]]
        elif isinstance(expr, FunctionCall):
            if expr.kind == FunctionCallKind.TYPE_CONVERSION:
                # TODO
                #node = TypeConversionDdgNode(expr)
                #self._expressions_lookup[expr] = {ConditionalNode(node, tuple())}

                sub = single_or_fail(self._process_expression_recursively(expr.arguments[0]))

                #for s in sub:
                    #self._graph.add_edge(s.node, node, conditions=s.conditions)
                #return [self._expressions_lookup[expr]]
                return [sub]
            elif expr.kind == FunctionCallKind.FUNCTION_CALL:
                function_called = expr.function_called
                if isinstance(function_called, GlobalSymbol):
                    node = self._global_symbols_lookup[function_called]

                    # for argument in function call arguments
                    for arg in expr.arguments:
                        # for component in tuple argument (typically single, multiple for abi.decode and others)
                        for arg_node in self._process_expression_recursively(arg):
                            # for conditional options
                            for arg_node_cond in arg_node:
                                self._graph.add_edge(arg_node_cond.node, node, conditions=arg_node_cond.conditions)
                    return [{ConditionalNode(node, tuple())}]
                elif isinstance(function_called, (EventDefinition, ErrorDefinition)):
                    return []  # TODO
                elif isinstance(function_called, ContractDefinition):
                    try:
                        constructor = next(f for f in function_called.functions if f.kind == FunctionKind.CONSTRUCTOR)
                        for var, arg in pair_function_call_arguments(constructor, expr):
                            var_node = self._variable_declarations_lookup[(var,)]
                            arg_node = single_or_fail(self._process_expression_recursively(arg))
                            for arg_node_cond in arg_node:
                                self._graph.add_edge(arg_node_cond.node, var_node, conditions=arg_node_cond.conditions)
                    except StopIteration:
                        pass

                    node = ContractConstructionDdgNode(expr)
                    self._expressions_lookup[expr] = {ConditionalNode(node, tuple())}
                    return [self._expressions_lookup[expr]]
                elif isinstance(function_called, ElementaryTypeName):
                    # TODO arguments
                    node = BytesConstructionNode(expr) if function_called.name == "bytes" else StringConstructionNode(expr)
                    self._expressions_lookup[expr] = {ConditionalNode(node, tuple())}
                    return [self._expressions_lookup[expr]]
                elif isinstance(function_called, ArrayTypeName):
                    # TODO arguments
                    node = ArrayConstructionNode(expr)
                    self._expressions_lookup[expr] = {ConditionalNode(node, tuple())}
                    return [self._expressions_lookup[expr]]
                elif isinstance(function_called, FunctionDefinition):
                    for var, arg in pair_function_call_arguments(function_called, expr):
                        var_node = self._variable_declarations_lookup[(var,)]
                        arg_node = single_or_fail(self._process_expression_recursively(arg))
                        for arg_node_cond in arg_node:
                            self._graph.add_edge(arg_node_cond.node, var_node, conditions=arg_node_cond.conditions)

                    return [{ConditionalNode(self._variable_declarations_lookup[(var,)], tuple())} for var in function_called.return_parameters.parameters]
                elif isinstance(function_called, VariableDeclaration):
                    getter = single_or_fail(self._process_expression_recursively(expr.expression))
                    return [getter]
                else:
                    raise NotImplementedError()
            elif expr.kind == FunctionCallKind.STRUCT_CONSTRUCTOR_CALL:
                for var, arg in pair_function_call_arguments(expr.function_called, expr):
                    var_node = self._variable_declarations_lookup[(var,)]
                    arg_node = single_or_fail(self._process_expression_recursively(arg))
                    for arg_node_cond in arg_node:
                        self._graph.add_edge(arg_node_cond.node, var_node, conditions=arg_node_cond.conditions)

                node = StructConstructionDdgNode(expr)
                self._expressions_lookup[expr] = {ConditionalNode(node, tuple())}
                return [self._expressions_lookup[expr]]
            else:
                raise AssertionError(f"Unexpected function call kind: {expr.kind}")
        elif isinstance(expr, (Identifier, MemberAccess)):
            ref_decl = expr.referenced_declaration

            if isinstance(ref_decl, GlobalSymbol):
                node = self._global_symbols_lookup[ref_decl]
                return [{ConditionalNode(node, tuple())}]
            elif isinstance(ref_decl, SourceUnit):
                return [set()]
            elif isinstance(ref_decl, VariableDeclaration):
                if isinstance(expr, MemberAccess):
                    subs = self._process_expression_recursively(expr.expression)
                else:
                    subs = []

                if len(subs) == 0:
                    return [{ConditionalNode(self._variable_declarations_lookup[(ref_decl,)], tuple())}]

                sub = single_or_fail(subs)
                assert all(isinstance(s.node, VariableDdgNode) for s in sub)
                return [{
                    ConditionalNode(self._variable_declarations_lookup[s.node.variable_declarations + (ref_decl,)], s.conditions)
                    for s in sub
                }]
            elif isinstance(ref_decl, EnumValue):
                return [{ConditionalNode(self._enum_values_lookup[ref_decl], tuple())}]
            elif isinstance(ref_decl, FunctionDefinition):
                return []
            elif isinstance(ref_decl, ContractDefinition):
                return []
            else:
                assert False, f"Unexpected reference: {expr.parent.source}"
        elif isinstance(expr, Assignment):
            # TODO operator
            left = self._process_expression_recursively(expr.left_expression)
            right = self._process_expression_recursively(expr.right_expression)
            assert len(left) == len(right) or len(right) == 1

            if len(right) == 1:
                for left_node in left:
                    if left_node is not None:
                        for l in left_node:
                            for r in right[0]:
                                self._graph.add_edge(r.node, l.node, conditions=l.conditions + r.conditions)
            else:
                for left_node, right_node in zip(left, right):
                    if left_node is not None:
                        for l in left_node:
                            for r in right_node:
                                self._graph.add_edge(r.node, l.node, conditions=(l.conditions + r.conditions))
            return left  # TODO or right? probably not
        elif isinstance(expr, IndexAccess):
            base = single_or_fail(self._process_expression_recursively(expr.base_expression))
            # TODO index?
            return [base]
        elif isinstance(expr, IndexRangeAccess):
            base = single_or_fail(self._process_expression_recursively(expr.base_expression))
            # TODO start, end?
            return [base]
        elif isinstance(expr, FunctionCallOptions):
            #e = single_or_fail(self._process_expression_recursively(expr.expression))
            # TODO options?
            return []
        elif isinstance(expr, NewExpression):
            return []  # TODO
        elif isinstance(expr, ElementaryTypeNameExpression):
            # needed in for example `abi.decode(payload, (string, string))`
            node = ElementaryTypeNameExpressionDdgNode(expr)
            self._expressions_lookup[expr] = {ConditionalNode(node, tuple())}
            return [self._expressions_lookup[expr]]
        elif isinstance(expr, Conditional):
            true_node = single_or_fail(self._process_expression_recursively(expr.true_expression))
            false_node = single_or_fail(self._process_expression_recursively(expr.false_expression))

            return [
                {ConditionalNode(n.node, ((expr.condition, ConditionKind.IS_TRUE),) + n.conditions) for n in true_node}.union(
                {ConditionalNode(n.node, ((expr.condition, ConditionKind.IS_FALSE),) + n.conditions) for n in false_node}
                )
            ]
        else:
            # TODO NewExpression
            assert False, f"Unexpected expression: {expr.parent.source}"

    def _expand_variable(self, var: VariableDeclaration) -> None:
        if var.value is not None:
            var_node = self._variable_declarations_lookup[(var,)]
            node = single_or_fail(self._process_expression_recursively(var.value))
            for n in node:
                self._graph.add_edge(n.node, var_node, conditions=n.conditions)

        if isinstance(var.parent, VariableDeclarationStatement):
            if var.parent.initial_value is not None:
                nodes = self._process_expression_recursively(var.parent.initial_value)
                assert len(var.parent.declarations) == len(nodes) or len(nodes) == 1
                var_node = self._variable_declarations_lookup[(var,)]

                if len(nodes) == 1:
                    # for example a global symbol function returning a tuple
                    for n in nodes[0]:
                        self._graph.add_edge(n.node, var_node, conditions=n.conditions)
                else:
                    for n in nodes[var.parent.declarations.index(var)]:
                        self._graph.add_edge(n.node, var_node, conditions=n.conditions)

        for ref in var.references:
            if isinstance(ref, ExternalReference):
                # TODO ignore Yul for now
                continue

            if isinstance(ref, (UnaryOperation, BinaryOperation)):
                # TODO is this even possible?
                assert False
                continue

            if isinstance(ref, IdentifierPathPart):
                assert False
                continue

            if isinstance(ref, Identifier):
                while isinstance(ref, ExpressionAbc):
                    self._process_expression_recursively(ref)
                    ref = ref.parent

            if isinstance(ref, MemberAccess):
                while isinstance(ref, ExpressionAbc):
                    self._process_expression_recursively(ref)
                    ref = ref.parent

    def _process_return(self, return_statement: Return) -> None:
        if return_statement.expression is None:
            return

        if isinstance(return_statement.declaration, ModifierDefinition):
            functions: List[FunctionDefinition] = []
            for ref in return_statement.declaration:
                if isinstance(ref, IdentifierPathPart):
                    ref = ref.underlying_node
                if isinstance(ref.parent, ModifierInvocation):
                    functions.append(ref.parent.parent)
        else:
            functions = [return_statement.declaration]

        expr = self._process_expression_recursively(return_statement.expression)

        for function in functions:
            assert len(expr) == len(function.return_parameters.parameters) or len(expr) == 1

            if len(expr) == 1:
                for var in function.return_parameters.parameters:
                    var_node = self._variable_declarations_lookup[(var,)]
                    for n in expr[0]:
                        self._graph.add_edge(n.node, var_node, conditions=n.conditions)
            else:
                for var, e in zip(function.return_parameters.parameters, expr):
                    var_node = self._variable_declarations_lookup[(var,)]
                    for n in e:
                        self._graph.add_edge(n.node, var_node, conditions=n.conditions)


id = 0


class DdgNode:
    id: int

    def __init__(self):
        global id
        self.id = id
        id += 1


class BytesConstructionNode(DdgNode):
    function_call: FunctionCall

    def __init__(self, function_call: FunctionCall):
        super().__init__()
        self.function_call = function_call

    def __str__(self):
        return "BYTES CONSTRUCTION\n" + self.function_call.source


class StringConstructionNode(DdgNode):
    function_call: FunctionCall

    def __init__(self, function_call: FunctionCall):
        super().__init__()
        self.function_call = function_call

    def __str__(self):
        return "STRING CONSTRUCTION\n" + self.function_call.source


class ArrayConstructionNode(DdgNode):
    function_call: FunctionCall

    def __init__(self, function_call: FunctionCall):
        super().__init__()
        self.function_call = function_call

    def __str__(self):
        return "ARRAY CONSTRUCTION\n" + self.function_call.source


class StructConstructionDdgNode(DdgNode):
    struct_construction: FunctionCall

    def __init__(self, struct_construction: FunctionCall):
        super().__init__()
        assert struct_construction.kind == FunctionCallKind.STRUCT_CONSTRUCTOR_CALL
        self.struct_construction = struct_construction

    def __str__(self):
        return "STRUCT CONSTRUCTION\n" + self.struct_construction.source


class ContractConstructionDdgNode(DdgNode):
    contract_construction: FunctionCall

    def __init__(self, contract_construction: FunctionCall):
        super().__init__()
        self.contract_construction = contract_construction

    def __str__(self):
        return "CONTRACT CONSTRUCTION\n" + self.contract_construction.source


class GlobalSymbolDdgNode(DdgNode):
    global_symbol: GlobalSymbol

    def __init__(self, global_symbol: GlobalSymbol):
        super().__init__()
        # TODO make msg.sender & others context dependent?
        self.global_symbol = global_symbol

    def __str__(self):
        return "GLOBAL SYMBOL\n" + repr(self.global_symbol)


class VariableDdgNode(DdgNode):
    variable_declarations: Tuple[VariableDeclaration, ...]

    def __init__(self, vars: Tuple[VariableDeclaration, ...]):
        super().__init__()
        self.variable_declarations = vars

    def __str__(self):
        return "VARIABLE\n" + f"{self.variable_declarations[-1].type_name.source} {'.'.join(v.name for v in self.variable_declarations)}"


class LiteralDdgNode(DdgNode):
    literal: Literal

    def __init__(self, literal: Literal):
        super().__init__()
        self.literal = literal

    def __str__(self):
        return "LITERAL\n" + self.literal.source


class ElementaryTypeNameExpressionDdgNode(DdgNode):
    elementary_type_name: ElementaryTypeNameExpression

    def __init__(self, elementary_type_name: ElementaryTypeNameExpression):
        super().__init__()
        self.elementary_type_name = elementary_type_name

    def __str__(self):
        return "ELEMENTARY TYPE NAME\n" + self.elementary_type_name.source


class EnumValueDdgNode(DdgNode):
    enum_value: EnumValue

    def __init__(self, enum_value: EnumValue):
        super().__init__()
        self.enum_value = enum_value

    def __str__(self):
        return "ENUM VALUE\n" + f"{self.enum_value.parent.name}.{self.enum_value.name}"


class BinaryOperationDdgNode(DdgNode):
    binary_operation: BinaryOperation

    def __init__(self, binary_operation: BinaryOperation):
        super().__init__()
        self.binary_operation = binary_operation

    def __str__(self):
        return "BINARY OPERATION\n" + self.binary_operation.source


class UnaryOperationDdgNode(DdgNode):
    unary_operation: UnaryOperation

    def __init__(self, unary_operation: UnaryOperation):
        super().__init__()
        self.unary_operation = unary_operation

    def __str__(self):
        return "UNARY OPERATION\n" + self.unary_operation.source


class TypeConversionDdgNode(DdgNode):
    type_conversion: FunctionCall

    def __init__(self, type_conversion: FunctionCall):
        super().__init__()
        assert type_conversion.kind == FunctionCallKind.TYPE_CONVERSION
        self.type_conversion = type_conversion

    def __str__(self):
        return "TYPE CONVERSION\n" + self.type_conversion.source
