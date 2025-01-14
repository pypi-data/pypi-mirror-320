import json
from pathlib import Path

_default_structure = {
    "root": {
        "data": {},
        "docs": {},
        "output": {},
        "logs": {},
        "src": {},
    }
}

ignore_dirs = ["__pycache__", ".git", ".vscode", ".venv", "node_modules"]


def new_structure(structure: dict = None, work_dir: str = None) -> dict:
    """a new structure with default structure and current directory structure merged"""
    if structure is None:
        structure = _default_structure
    if work_dir is None:
        raise ValueError("work_dir is required")
    curr_structure = read_curr_dir_structure(work_dir)
    merged_structure = merge_structure(structure, curr_structure)
    return merged_structure


def read_curr_dir_structure(work_dir: Path | str, structure: dict = None) -> dict:
    """read current directory structure"""
    work_dir = Path(work_dir)

    if structure is None:
        structure = {}
    for item in work_dir.iterdir():
        if is_ignore_dir(item):
            continue
        if item.is_dir():
            structure[item.name] = {}
            read_curr_dir_structure(item, structure[item.name])
    return structure


def is_ignore_dir(dir_path: Path) -> bool:
    """filter out empty directories"""
    # didn't use match case because it's not supported in python 3.9 or below

    # ignore startswith "."
    if dir_path.name.startswith("."):
        return True
    # ignore in ignore_dirs
    elif dir_path.name in ignore_dirs:
        return True
    else:
        return False


def merge_structure(default_structure: dict, curr_structure: dict) -> dict:
    """merge default structure and current directory structure"""
    merged_structure = default_structure.copy()
    merged_structure["root"].update(curr_structure)
    return merged_structure


if __name__ == "__main__":
    work_dir = Path.cwd()
    struct = new_structure(work_dir=work_dir)
    with open("struct.json", "w", encoding="utf-8") as f:
        json.dump(struct, f, ensure_ascii=False, indent=4, sort_keys=True)
