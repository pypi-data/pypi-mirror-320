import os
from pathlib import Path

DEFAULT_PATTERNS = [
    ".git",
    ".git/",
    "__pycache__/",
    "__pycache__",
    ".pytest_cache",
    ".pytest_cache/",
    ".mypy_cache",
    ".mypy_cache/",
    ".pyc",
    ".bin",
    ".debhelper",
    ".debhelper/",
    ".pt",
    ".pth",
    ".gguf",
    ".ggml",
    ".tflife",
    ".onnx",
    ".sav",
    ".cpkt",
    ".h5",
    ".pb",
    ".model",
    ".pyo",
    ".pyd",
    ".class",
    ".db",
    ".exe",
    ".json",
    ".dll",
    ".so",
    ".Python",
    ".pypirc",
    "dist/",
    "sdist/",
    ".env/",
    "env/",
    "ENV/",
    "ENV",
    ".venv",
    ".venv/",
    "venv",
    "venv/",
    "vendors/",
    "vendors",
    "vendor/",
    "vendor",
    "node_modules/",
    "node_modules",
]


def is_binary_file(filepath, chunk_size=1024):
    """
    Heuristic: A file is considered binary if it contains a null byte
    in its first `chunk_size` bytes.
    """
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(chunk_size)
            if b"\0" in chunk:
                return True
    except OSError:
        # If there's an error opening the file in binary mode, treat as binary
        return True
    return False


def should_ignore(path, patterns):
    """
    Check if path should be ignored based on patterns.
    Handles:
    - Directory patterns (ending in /) vs file patterns
    - Case sensitivity (normalized on Windows)
    - Multiple trailing slashes
    - Unicode paths and patterns

    Args:
        path (Path): Path to check
        patterns (list): List of patterns to check against

    Returns:
        bool: True if path should be ignored
    """
    # Normalize the path for consistent handling
    path_str = str(path)
    path_parts = Path(path_str).parts

    # Handle case sensitivity on Windows
    if os.name == "nt":  # Windows
        path_str = path_str.lower()
        path_parts = tuple(part.lower() for part in path_parts)

    for pattern in patterns:
        # Remove trailing whitespace and normalize slashes
        pattern = pattern.strip()

        # Normalize pattern
        if os.name == "nt":
            pattern = pattern.lower()

        # Handle directory patterns (ending in one or more slashes)
        if pattern.endswith("/"):
            dir_pattern = pattern.rstrip("/")  # Remove all trailing slashes
            pattern_parts = Path(dir_pattern).parts

            # Get all directory combinations from the path
            for i in range(len(path_parts)):
                if path_parts[i : i + len(pattern_parts)] == pattern_parts:
                    return True
        # Handle file patterns
        else:
            try:
                if pattern in path_str or (
                    pattern.startswith(".") and path_str.endswith(pattern)
                ):
                    return True
            except UnicodeError:
                pattern_bytes = pattern.encode("utf-8")
                path_bytes = path_str.encode("utf-8")
                if pattern_bytes in path_bytes or (
                    pattern.startswith(".") and path_str.endswith(pattern)
                ):
                    return True
    return False


def create_capsule(root_dir, ignore_patterns=None):
    root_path = Path(root_dir).resolve()

    if (
        root_path == Path("/")  # Unix-like systems
        or root_path == Path("C:\\")  # Windows drive root
        or str(root_path).lower() in ["/", "\\", "c:\\", "c:"]
        or root_path.parent == root_path  # Covers edge cases
    ):
        print("Error: Refusing to run at the system root directory. Exiting ...")
        sys.exit(1)

    if ignore_patterns is None:
        ignore_patterns = set()

    ignore_patterns = ignore_patterns.union(set(DEFAULT_PATTERNS))
    project_files = []
    total_files = 0
    total_size_bytes = 0
    root = Path(root_dir)

    for path in root.rglob("*"):

        # 1. Skip directories
        if path.is_dir():
            continue

        # 2. Skip paths that match the ignore patterns
        if should_ignore(path, ignore_patterns):
            continue

        # 3. Skip binary files or executables
        if is_binary_file(path):
            continue

        # 4. Try reading the file as UTF-8 text
        try:
            file_size = path.stat().st_size
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            project_files.append(
                {"path": str(path.relative_to(root)), "content": content}
            )
            # Update counters
            total_files += 1
            total_size_bytes += file_size
        except UnicodeDecodeError:
            # Skip binary files
            continue

    print(f"Total files added: {total_files} ...")
    print(f"Total size: {total_size_bytes:,} bytes ...")

    return project_files


def prepare_output_path(output_path):
    """
    Prepare and validate the output file path.

    Args:
        output_path (str): The provided output path.

    Returns:
        str: A validated, absolute path for the output file.

    Raises:
        argparse.ArgumentTypeError: If the path is invalid or cannot be created.
    """
    try:
        # Expand user home directory and convert to absolute path
        full_path = os.path.abspath(os.path.expanduser(output_path))

        # Ensure the directory exists
        output_dir = os.path.dirname(full_path)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except PermissionError:
                raise argparse.ArgumentTypeError(
                    f"Permission denied: Cannot create directory {output_dir}"
                )

        # Check if we have write permissions
        if os.path.exists(output_dir) and not os.access(output_dir, os.W_OK):
            raise argparse.ArgumentTypeError(
                f"No write permission for directory {output_dir}"
            )

        # Ensure the file has a .json extension ONLY if it doesn't already have it
        if not full_path.lower().endswith(".json"):
            full_path += ".json"

        return full_path

    except Exception as e:
        raise argparse.ArgumentTypeError(f"Invalid output path: {e}")
