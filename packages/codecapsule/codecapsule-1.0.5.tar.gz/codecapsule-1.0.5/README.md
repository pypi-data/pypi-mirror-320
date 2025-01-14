# CodeCapsule 🚀📦

## Overview

CodeCapsule is a powerful Python utility that transforms entire project directories into a single, portable JSON file. Perfect for sharing code with AI models, archiving projects, or creating compact code representations.

## Features

- 🌐 Convert entire project structures to JSON
- 🧩 Supports multiple programming languages
- 🔍 Configurable file inclusion/exclusion
- 💡 Ideal for LLM code analysis and sharing

## Installation

Install CodeCapsule using pip:

```bash
pip install codecapsule
```

## Quick Start

### Basic Usage

```bash
# Convert current project to JSON
codecapsule

# Convert a specific project directory
codecapsule /path/to/your/project

# Save to a specific output file
codecapsule /path/to/project -o project_capsule.json
```

## Filtering and Handling

CodeCapsule provides robust file processing with the following features:

- 🚫 Automatically excludes:
  - Binary files
  - Large executables (`.exe`, `.dll`, `.so`)
  - Compiled Python files (`.pyc`)
  - Version control directories (`.git`)
  - Virtual environments (`.venv`)
  - Development databases

- 🔍 File Content Detection
  - Uses UTF-8 encoding
  - Skips files that cannot be decoded
  - Detects binary files using null-byte heuristic

## Example Output

```json
[
  {
    "path": "src/main.py",
    "content": "# Full contents of the Python file"
  },
  {
    "path": "README.md", 
    "content": "# Project documentation"
  }
]
```

## Limitations

- Large files may impact performance
- Only text-based files are processed
- Some binary or complex file types are automatically excluded

## Use Cases

- 📤 Sharing entire project contexts with AI models
- 🗄️ Lightweight project archiving
- 🔬 Code analysis and exploration

## License

BSD-3 License - See `LICENSE` file for details.

## Requirements

- Python 3.8+
- No external dependencies

## Disclaimer

CodeCapsule is designed for code sharing and analysis. Always review JSON contents before sharing sensitive code.