# atlaz/io_operations/file_mediator.py
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List
from flask import jsonify
from pydantic import ValidationError

from atlaz.codeGen.schema import Files

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def file_exists(path: Path) -> bool:
    """
    Check if a file/directory at `path` exists.
    """
    return path.exists()


def unlink_file(path: Path) -> None:
    """
    Delete a file at `path` if it exists.
    """
    if path.exists():
        path.unlink()


def read_txt(path: Path) -> str:
    """
    Read and return text from a .txt file at `path`.
    """
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def write_txt(content: str, path: Path) -> None:
    """
    Write `content` to a .txt file at `path`, ensuring parent dirs exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content)


def read_json(path: Path) -> Any:
    """
    Read JSON data from `path` and return the parsed object.
    """
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(data: Any, path: Path) -> None:
    """
    Serialize `data` as JSON and write to `path`, ensuring parent dirs exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def is_binary(file_path: Path) -> bool:
    """
    A simple check for binary content by scanning the first 1024 bytes for null bytes.
    """
    try:
        with file_path.open('rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except Exception:
        # If we can't read it, treat it as binary/unreadable
        return True


def is_large_or_binary(file_path: Path) -> bool:
    """
    Returns True if the file is likely binary or if it's larger than 1 MB.
    """
    one_mb_in_bytes = 1024 * 1024
    if file_path.exists():
        if file_path.stat().st_size > one_mb_in_bytes:
            return True
        if is_binary(file_path):
            return True
    return False


def load_files(selected_files: List[str]) -> List[Dict[str, Any]]:
    """
    Load a list of file paths, skipping large or binary files, returning 
    a list of dicts conforming to Pydantic schema `Files`.
    """
    loaded_files = []
    for file_path_str in selected_files:
        file_path = Path(file_path_str)
        if not file_exists(file_path):
            logger.warning(f"File does not exist: {file_path}")
            continue
        if is_large_or_binary(file_path):
            logger.warning(f"Skipping binary or large file: {file_path}")
            continue
        try:
            content = read_txt(file_path)
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            continue
        try:
            # Create the Pydantic model instance
            
            file_record = Files(name=file_path_str, content=content)
            # Convert to dict before appending to the list
            loaded_files.append(file_record.dict())
            logger.info(f"Loaded file: {file_path.name}")
        except ValidationError as ve:
            logger.error(f"Validation error for file {file_path}: {ve}")
            continue

    return loaded_files


def build_directory_tree_json(root_path: Path, ignore=None, max_depth=20, level=0):
    """
    Recursively build a nested JSON representation of the directory tree.
    """
    if ignore is None:
        ignore = set()
    if level > max_depth:
        return []
    items = []
    try:
        for entry in sorted(os.scandir(root_path), key=lambda e: e.name.lower()):
            if entry.name in ignore or entry.name.startswith('.'):
                continue
            entry_path = Path(entry.path)
            if entry.is_dir():
                items.append({
                    "name": entry.name,
                    "type": "directory",
                    "path": str(entry_path),
                    "children": build_directory_tree_json(
                        entry_path,
                        ignore=ignore,
                        max_depth=max_depth,
                        level=level + 1
                    )
                })
            else:
                items.append({
                    "name": entry.name,
                    "type": "file",
                    "path": str(entry_path)
                })
    except PermissionError:
        pass
    return items


def make_paths_relative(tree_list, root_path: Path):
    """
    Recursively convert each item's 'path' from absolute to relative
    relative to `root_path`.
    """
    new_list = []
    for item in tree_list:
        new_item = item.copy()
        abs_path = Path(new_item['path'])
        try:
            rel_path = abs_path.relative_to(root_path)
            new_item['path'] = str(rel_path)
        except ValueError:
            pass
        if 'children' in new_item:
            new_item['children'] = make_paths_relative(new_item['children'], root_path)
        new_list.append(new_item)
    return new_list


def build_directory_tree_string(selected_files: List[str]) -> str:
    """
    Builds an ASCII directory tree string from a list of file paths.
    """
    tree = {}
    directories = set()
    files = set()

    # 1. Separate directories and files
    for file_path in selected_files:
        path = Path(file_path)
        if file_path.endswith('/'):
            # It's a directory; remove trailing '/'
            directories.add(path.as_posix().rstrip('/'))
        else:
            files.add(path.as_posix())

    # 2. Add parent directories of files
    for file_path in files:
        path = Path(file_path)
        for parent in path.parents:
            if parent == Path('/'):
                continue
            directories.add(parent.as_posix())

    # 3. Detect conflicts (treated as file and directory)
    conflicting_paths = directories.intersection(files)
    if conflicting_paths:
        conflict_path = conflicting_paths.pop()
        raise ValueError(f"Conflict at '{conflict_path}': path is both a file and a directory.")

    # 4. Build the tree for directories
    sorted_directories = sorted(directories, key=lambda x: x.count('/'))
    for dir_path in sorted_directories:
        path = Path(dir_path)
        parts = path.parts
        current_level = tree
        for part in parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

    # 5. Add files to the tree
    for file_path in sorted(files):
        path = Path(file_path)
        parts = path.parts
        current_level = tree
        for part in parts[:-1]:
            current_level = current_level[part]
        file_name = parts[-1]
        current_level[file_name] = None  # Represent files as None

    # 6. Convert the nested dict to a string
    lines = []
    def traverse(current_dict: Dict[str, Any], prefix: str = ""):
        dirs = sorted([k for k, v in current_dict.items() if isinstance(v, dict)], key=lambda x: x.lower())
        files_sorted = sorted([k for k, v in current_dict.items() if v is None], key=lambda x: x.lower())
        sorted_keys = dirs + files_sorted
        total_items = len(sorted_keys)
        for idx, key in enumerate(sorted_keys):
            is_last = (idx == total_items - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{key}")
            if isinstance(current_dict[key], dict):
                extension = "    " if is_last else "│   "
                traverse(current_dict[key], prefix + extension)
    traverse(tree)
    return "\n".join(lines)


def obtain_write_paths():
    """
    Creates or clears out the standard 3 directories we use:
    original/, replacing/, created/.
    Also unlinks the 'files.json' if it exists.
    Returns a tuple of (replacing_dir, created_dir, original_dir, files_json_path).
    """
    atlaz_helper_dir = Path(__file__).parent.parent.parent.parent / ".atlaz_helper"
    original_dir = atlaz_helper_dir / "original"
    replacing_dir = atlaz_helper_dir / "replacing"
    created_dir = atlaz_helper_dir / "created"
    original_dir.mkdir(parents=True, exist_ok=True)
    replacing_dir.mkdir(parents=True, exist_ok=True)
    created_dir.mkdir(parents=True, exist_ok=True)
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    files_json_path = frontend_dir / 'files.json'
    unlink_file(files_json_path)
    return replacing_dir, created_dir, original_dir, files_json_path, frontend_dir

def remove_json_files():
    """
    Delete atlaz/frontend/files.json if it exists.
    """
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    files_json_path = frontend_dir / 'files.json'
    unlink_file(files_json_path)

def remove_explanation_file():
    """
    Delete atlaz/frontend/explanation.txt if it exists.
    """
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    explanation_file_path = frontend_dir / 'explanation.txt'
    unlink_file(explanation_file_path)

def handle_apply_changes():
    # 1) Determine the root or base directory of your repo
    #    You can adjust `parents[2]` depending on your structure
    project_root = Path(__file__).resolve().parents[2]  
    cmd_root = Path.cwd()
    
    frontend_dir = project_root / 'atlaz' / 'frontend'
    files_json_path = frontend_dir / 'files.json'
    
    if not files_json_path.exists():
        return jsonify({"status": "error", "message": "No files.json found."}), 404
    
    # 2) Load the JSON that lists generated files
    with files_json_path.open("r", encoding="utf-8") as f:
        generated_files = json.load(f)
    
    # 3) Iterate the list of file objects and update real files
    for file_info in generated_files:
        file_type = file_info.get('type')
        full_name = file_info.get('full_name')
        content = file_info.get('content', '')
        if not full_name:
            continue
        
        # Remove the prefix from full_name to get the *real* relative path
        if file_type == 'replacing':
            # Remove "replacing-" prefix
            real_relative = full_name.replace('replacing-', '', 1)
        elif file_type == 'created':
            # Remove "created-" prefix
            real_relative = full_name.replace('created-', '', 1)
        else:
            # If it's "original" or something else, skip or handle differently
            continue
        
        # 4) Construct the actual path to your project
        real_path = cmd_root / real_relative
        
        # 5) Ensure parent directories exist, then write the content
        real_path.parent.mkdir(parents=True, exist_ok=True)
        real_path.write_text(content, encoding='utf-8')
    
    return jsonify({"status": "success", "message": "Applied changes successfully."})