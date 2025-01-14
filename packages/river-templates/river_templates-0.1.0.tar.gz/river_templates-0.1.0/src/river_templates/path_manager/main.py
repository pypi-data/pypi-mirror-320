import json
from pathlib import Path

import click
import river_print as rp

from .generate import generate_from_struct, save_pyfile
from .structure import new_structure


def generate_path_manager(
    project_root_dir: Path | str, tgt_path: Path | str = None, verbose: bool = True
):
    project_root_dir = Path(project_root_dir)
    toml = project_root_dir / "pyproject.toml"
    if not toml.exists():
        rp.action(f"pyproject.toml does not exist, creating it in {project_root_dir}")
        toml.touch()
        return

    if tgt_path is None:
        tgt_path = project_root_dir / "path_manager.py"
    else:
        tgt_path = Path(tgt_path)

    existed_structure = Path(project_root_dir) / "structure.json"
    if existed_structure.exists():
        structure = json.load(existed_structure.open("r", encoding="utf-8"))
        rp.action(f"using existed structure: {structure}")
    else:
        rp.action(
            f"structure.json does not exist, do you want to create it using current directory structure merged with default structure?"
        )
        if click.confirm("yes"):
            structure = new_structure(work_dir=project_root_dir)
            with open(project_root_dir / "structure.json", "w", encoding="utf-8") as f:
                json.dump(structure, f, indent=4, ensure_ascii=False, sort_keys=True)
        else:
            rp.action("cancelled")
            return
    code = generate_from_struct(structure=structure)
    save_pyfile(code=code, path=tgt_path, verbose=verbose)


if __name__ == "__main__":
    generate_path_manager()
