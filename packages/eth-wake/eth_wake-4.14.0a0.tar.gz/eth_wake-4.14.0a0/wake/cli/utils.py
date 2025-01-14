import time

from wake.compiler.compiler import SolidityCompiler
from wake.compiler.solc_frontend.input_data_model import SolcOutputSelectionEnum
from wake.config import WakeConfig
from wake.utils import wake_contracts_path, change_cwd
from .console import console
from ..development.pytypes_generator import TypeGenerator


async def generate_wake_contract_pytypes(config: WakeConfig, return_tx_obj: bool):
    sol_files = list(wake_contracts_path.joinpath("wake").rglob("**/*.sol"))

    with change_cwd(wake_contracts_path / "wake"):
        compiler = SolidityCompiler(WakeConfig.fromdict({
            "compiler": {
                "solc": {
                    "evm_version": "istanbul",
                    "optimizer": {
                        "enabled": True,
                    }
                }
            }
        }))
        _, errors = await compiler.compile(
            sol_files,
            [SolcOutputSelectionEnum.ALL],
            write_artifacts=False,
            force_recompile=False,
            console=console,
            no_warnings=True,
            incremental=False,
        )

    start = time.perf_counter()
    with console.status("[bold green]Generating global pytypes..."):
        type_generator = TypeGenerator(config.global_data_path / "pytypes", return_tx_obj)
        type_generator.generate_types(compiler)
    end = time.perf_counter()
    console.log(f"[green]Generated global pytypes in [bold green]{end - start:.2f} s[/]")
