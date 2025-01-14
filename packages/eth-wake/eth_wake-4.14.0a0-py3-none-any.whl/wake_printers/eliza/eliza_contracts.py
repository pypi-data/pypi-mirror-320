from __future__ import annotations

import networkx as nx
import rich_click as click
from rich import print
from rich.tree import Tree

import wake.ir as ir
import wake.ir.types as types
from wake.printers import Printer, printer


class ElizaContractsPrinter(Printer):
    contracts: list[ir.ContractDefinition]

    def __init__(self) -> None:
        self.contracts = []

    def print(self) -> None:
        for contract in self.contracts:
            print(f"- {contract.name}: {contract.kind}")

    def visit_contract_definition(self, node: ir.ContractDefinition) -> None:
        self.contracts.append(node)

    @printer.command(name="eliza-contracts")
    def cli(self) -> None:
        pass
