from pathlib import Path
from typing import Any, Dict

import river_print as rp

attr_names = []


def generate_from_struct(structure: Dict, verbose=True):
    """generate path manager file base on given structure"""
    code = generate_path_manager_code(structure)

    if verbose:
        rp.success(f"path manager code generated from : {structure}")
    return code


def save_pyfile(code: str, path: Path, verbose: bool = True):
    """save path manager code to file, if file exists, ask user to add timestamp to name"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    name = path.name
    if path.exists():
        input(f"path manager file already exists: {path}, press enter to add timestamp")
        from datetime import datetime

        name = name.replace(".py", f"__{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
        path = path.with_name(name)

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    if verbose:
        rp.success(f"path manager file generated: {path}")


def generate_path_manager_code(structure: Dict) -> str:
    """生成PathManager类的代码"""

    # 生成代码
    # import code
    code = [
        "from dataclasses import dataclass",
        "from pathlib import Path",
    ]
    # add find root_dir code
    code += [
        "",
        "def find_root_dir() -> Path:",
        "    parent = Path(__file__).parent",
        "    while True:",
        "        if (parent / 'pyproject.toml').exists():",
        "            return parent",
        "        parent = parent.parent",
        "    raise ValueError('pyproject.toml not found')",
    ]
    # add dataclass code
    code += [
        "",
        "",
        "@dataclass",
        "class PathManager:",
        "",
    ]
    # 生成属性定义
    attr_code = process_structure(structure)
    code += attr_code

    # 添加__post_init__方法
    code.extend(
        [
            "",
            "    def __post_init__(self):",
            "        for attr_name, value in self.__dict__.items():",
            "            if (",
            "                isinstance(value, Path)",
            '                and "dir" in attr_name',
            "                and not value.exists()",
            "                and not value.is_symlink()",
            "            ):",
            "                value.mkdir(parents=True, exist_ok=True)",
            '                print(f"create dir: {value}")',
        ]
    )

    # add single instance code
    code.extend(
        [
            "",
            "",
            "_pm_instance: PathManager | None = None",
            "",
            "def get_pm() -> PathManager:",
            "    global _pm_instance",
            "    if _pm_instance is None:",
            "        _pm_instance = PathManager()",
            "    return _pm_instance",
        ]
    )
    return "\n".join(code)


def process_structure(structure: Dict, parent_path: str = None) -> list[str]:
    """递归处理结构字典，返回属性定义列表"""
    attr_code = []

    for name, content in structure.items():
        # 处理目录
        current_path = f"{parent_path} / '{name}'" if parent_path else "find_root_dir()"
        if name != "root_dir":
            dir_attr_name = f"{name}_dir" if not name.endswith("_dir") else name
            attr_code.append(f"    {dir_attr_name}: Path = {current_path}")
            check_repeat(dir_attr_name)

        # 递归处理子目录和文件
        if isinstance(content, dict):
            current_var = f"{name}_dir" if name != "root_dir" else "root_dir"
            for sub_name, sub_content in content.items():
                if isinstance(sub_content, dict):
                    # 处理子目录
                    sub_attrs = process_structure(
                        {sub_name: sub_content}, f"{current_var}"
                    )
                    attr_code.extend(sub_attrs)
                else:
                    # 处理文件
                    file_attr_name = f"{sub_name.split('.')[0]}"
                    check_repeat(file_attr_name)
                    attr_code.append(
                        f"    {file_attr_name}: Path = {current_var} / '{sub_name}'"
                    )
    return attr_code


def check_repeat(name: str):
    if name not in attr_names:
        attr_names.append(name)
    else:
        raise ValueError(f"重复的属性名: {name}")
