# Intelligent JSON Merger

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![CI/CD](https://github.com/Wasserpuncher/intelligent-json-merger-86d56/actions/workflows/python-app.yml/badge.svg)](https://github.com/Wasserpuncher/intelligent-json-merger-86d56/actions/workflows/python-app.yml)

## 💡 About

`Intelligent JSON Merger` is a robust, enterprise-ready, and open-source Python library designed to intelligently merge JSON configuration files and dictionaries. It provides a flexible and powerful way to manage application settings, allowing for hierarchical overwrites, deep merging of objects, and intelligent handling of lists, ensuring your configurations are always consistent and predictable.

This project aims to solve the common problem of managing complex configurations across different environments (development, staging, production) or for modular applications where settings are defined in multiple places. It goes beyond simple overwrites by understanding the structure of JSON data and applying context-aware merging strategies.

## ✨ Features

-   **Deep Merging**: Recursively merges nested JSON objects.
-   **List Handling**: Appends unique elements to lists, avoiding duplicates by default.
-   **Flexible Input**: Merge from file paths or directly from Python dictionaries.
-   **Hierarchical Overwrites**: Later configurations take precedence over earlier ones.
-   **Error Handling**: Robust error reporting for invalid file paths or malformed JSON.
-   **Extensible Design**: Built with modularity in mind, allowing for custom merge strategies in the future.
-   **Type Hinting**: Fully type-hinted for better code quality and maintainability.

## 🚀 Installation

```bash
git clone https://github.com/Wasserpuncher/intelligent-json-merger-86d56.git
cd intelligent-json-merger
pip install -r requirements.txt
```

## 📖 Usage

### Basic Merging

To merge multiple JSON files or dictionaries, simply pass them to the `merge_configs` method:

Create `config_base.json`:

```json
{
  "app_name": "MyWebApp",
  "version": "1.0.0",
  "settings": {
    "debug": true,
    "port": 8080,
    "features": ["auth", "logging"]
  },
  "database": {
    "host": "localhost"
  }
}
```

Create `config_env_dev.json`:

```json
{
  "version": "1.0.1-dev",
  "settings": {
    "debug": true,
    "port": 9000,
    "features": ["dev-tools", "auth"]
  },
  "database": {
    "user": "dev_user",
    "password": "dev_pass"
  }
}
```

Now, merge them:

```python
from main import JsonMerger
import json

merger = JsonMerger()

merged_config = merger.merge_configs(
    "config_base.json",
    "config_env_dev.json",
    {
        "settings": {
            "debug": True, # Override again
            "log_level": "DEBUG"
        }
    }
)

print(json.dumps(merged_config, indent=4))
```

Output:

```json
{
    "app_name": "MyWebApp",
    "version": "1.0.1-dev",
    "settings": {
        "debug": true,
        "port": 9000,
        "features": [
            "auth",
            "logging",
            "dev-tools"
        ],
        "log_level": "DEBUG"
    },
    "database": {
        "host": "localhost",
        "user": "dev_user",
        "password": "dev_pass"
    }
}
```

### Error Handling

The `merge_configs` method will raise `ValueError` for file-related issues or invalid JSON, and `TypeError` for incorrect input types.

```python
try:
    merger.merge_configs("non_existent_file.json")
except ValueError as e:
    print(f"Error: {e}")

try:
    merger.merge_configs({"valid": true}, "{"invalid": "json"}") # Malformed string
except ValueError as e:
    print(f"Error: {e}")
```

### Configuration-file driven merges

Instead of listing the files to merge in code, a whole run can be described in a
single JSON control file. It names the input files to load and merge, and where
to write the result:

```json
{
  "inputs": ["config1.json", "config2.json", "config3.json"],
  "output": "merged.json"
}
```

*   `inputs` (required): ordered list of JSON files to load and deep-merge,
    earlier first.
*   `output` (optional): path the merged result is written to. If omitted, the
    result is printed to stdout.

Run it from the command line (see `merge-config.example.json` for a template):

```bash
python main.py --config merge-config.json
```

Or programmatically:

```python
from main import run_from_config

merged = run_from_config("merge-config.json")
```

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.