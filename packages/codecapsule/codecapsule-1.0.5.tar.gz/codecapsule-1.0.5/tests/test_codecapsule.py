from pathlib import Path
import os

from codecapsule import create_capsule, prepare_output_path, should_ignore

import pytest


def test_create_capsule():
    # Create a temporary directory with some test files
    import tempfile

    with tempfile.TemporaryDirectory() as tmpddir:
        # Create some test files
        os.makedirs(os.path.join(tmpddir, "src"))

        with open(os.path.join(tmpddir, "src", "test.py"), "w") as f:
            f.write("def hello():\n    return 'world'")

        with open(os.path.join(tmpddir, "README.md"), "w") as f:
            f.write("# Test Project")

        # Run create_capsule
        capsule = create_capsule(tmpddir)

        # Assertions
        assert len(capsule) == 2
        assert any(item["path"] == "src/test.py" for item in capsule)
        assert any(item["path"] == "README.md" for item in capsule)


def test_prepare_output_path(tmp_path):
    # Test absolute path
    abs_path = str(tmp_path / "test.json")
    result = prepare_output_path(abs_path)
    assert result == abs_path

    # Test path without .json extension
    abs_path_no_ext = str(tmp_path / "test")
    result = prepare_output_path(abs_path_no_ext)
    assert result == abs_path


def test_ignore_patterns():
    import tempfile

    with tempfile.TemporaryDirectory() as tmpddir:
        # Create various files to test ignore patterns
        os.makedirs(os.path.join(tmpddir, ".git"))
        os.makedirs(os.path.join(tmpddir, ".venv"))

        with open(os.path.join(tmpddir, "test.pyc"), "wb") as f:
            f.write(b"some binary content")

        with open(os.path.join(tmpddir, "test.txt"), "w") as f:
            f.write("Hello world")

        # Run create_capsule
        capsule = create_capsule(tmpddir)

        # Assertions
        assert len(capsule) == 1
        assert capsule[0]["path"] == "test.txt"


def test_should_ignore_basic():
    """Test basic pattern matching."""
    test_cases = [
        (Path("test/folder"), "test/", True),
        (Path("src/test.py"), ".py", True),
        (Path("src/test.txt"), ".py", False),
    ]

    for path, pattern, expected in test_cases:
        assert should_ignore(path, [pattern]) == expected


def test_should_ignore_multiple_slashes():
    """Test handling of multiple trailing slashes."""
    test_cases = [
        (Path("test/folder"), "test////", True),
        (Path("test/folder"), "test/  ", True),
        (Path("other/folder"), "test////", False),
    ]

    for path, pattern, expected in test_cases:
        assert should_ignore(path, [pattern]) == expected


def test_should_ignore_case_sensitivity(tmp_path):
    """Test case sensitivity handling (platform-dependent)."""
    import os

    test_cases = [
        (Path("Test/Folder"), "test/", True if os.name == "nt" else False),
        (Path("TEST/FOLDER"), "test/", True if os.name == "nt" else False),
    ]

    for path, pattern, expected in test_cases:
        assert should_ignore(path, [pattern]) == expected


def test_should_ignore_unicode(sample_files):
    """Test Unicode path handling."""
    test_cases = [
        (Path("тест/файл.txt"), "тест/", True),
        (Path("тест/файл.txt"), ".txt", True),
        (Path("тест/файл.txt"), "другой/", False),
    ]

    for path, pattern, expected in test_cases:
        assert should_ignore(path, [pattern]) == expected


def test_with_real_files(sample_files):
    """Test with actual files in a temporary directory."""
    patterns = ["node_modules/", ".py", "тест/"]

    # Should be ignored
    assert should_ignore(sample_files / "node_modules" / "package.json", patterns)
    assert should_ignore(sample_files / "src" / "test.py", patterns)
    assert should_ignore(sample_files / "тест" / "файл.txt", patterns)

    # Should not be ignored
    assert not should_ignore(sample_files / "src" / "test.txt", patterns)


@pytest.fixture
def sample_files(tmp_path):
    """Create a set of sample files for testing."""
    # Create test files and directories
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "test.py").write_text("print('hello')")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "package.json").write_text("{}")
    (tmp_path / "тест").mkdir()  # Unicode directory
    (tmp_path / "тест" / "файл.txt").write_text("тест")  # Unicode file
    return tmp_path


def test_should_ignore():
    """Test pattern matching with platform-specific cases."""
    # Basic test cases that should work on all platforms
    common_cases = [
        # Multiple trailing slashes
        (Path("test/folder"), "test////", True),
        (Path("test/folder"), "test/  ", True),
        # Unicode paths
        (Path("tést/földer"), "tést/", True),
        (Path("тест/папка"), "тест/", True),
        # Normal cases
        (Path("src/test.py"), ".py", True),
        (Path("src/test.py"), "src/", True),
        (Path("src/test.txt"), ".py", False),
    ]

    # Windows-specific cases
    windows_cases = [
        (Path("Test/Folder"), "test/", True),  # Case insensitive on Windows
    ]

    # Test common cases
    for path, pattern, expected in common_cases:
        result = should_ignore(path, [pattern])
        assert result == expected, f"Failed for path={path}, pattern={pattern}"

    # Test Windows-specific cases only on Windows
    if os.name == "nt":
        for path, pattern, expected in windows_cases:
            result = should_ignore(path, [pattern])
            assert result == expected, f"Failed for path={path}, pattern={pattern}"
    else:
        # On non-Windows, test with case-sensitive behavior
        for path, pattern, expected in windows_cases:
            result = should_ignore(path, [pattern])
            assert result == False, f"Failed for path={path}, pattern={pattern}"
