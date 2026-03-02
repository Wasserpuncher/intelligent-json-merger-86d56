# Contributing to Intelligent JSON Merger

We welcome contributions to the `Intelligent JSON Merger` project! Whether it's reporting a bug, suggesting a new feature, improving documentation, or submitting code, your help is valuable.

Please read this guide to understand how to contribute effectively.

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md) (not included in this generation, but good practice). By participating, you are expected to uphold this code. Please report unacceptable behavior to [email@example.com].

## How to Contribute

### 1. Reporting Bugs

If you find a bug, please open an issue on our GitHub repository. Before doing so, please:

-   Check existing issues to see if the bug has already been reported.
-   Provide a clear and concise description of the bug.
-   Include steps to reproduce the bug.
-   Mention your operating system, Python version, and any relevant library versions.
-   If possible, include a minimal reproducible example.

### 2. Suggesting Enhancements

We love new ideas! If you have a suggestion for a new feature or an improvement to existing functionality:

-   Open an issue on GitHub.
-   Clearly describe the feature and why you think it would be beneficial.
-   Provide examples of how it might be used.

### 3. Submitting Code (Pull Requests)

Follow these steps to contribute code:

1.  **Fork the Repository**: Start by forking the `intelligent-json-merger` repository to your GitHub account.
2.  **Clone Your Fork**: Clone your forked repository to your local machine:
    ```bash
    git clone https://github.com/YOUR_USERNAME/intelligent-json-merger.git
    cd intelligent-json-merger
    ```
3.  **Create a New Branch**: Create a new branch for your feature or bug fix. Use a descriptive name (e.g., `feature/add-yaml-support`, `bugfix/list-deduplication-issue`).
    ```bash
    git checkout -b feature/your-feature-name
    ```
4.  **Set Up Your Environment**: Install the development dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Make Your Changes**: Implement your feature or fix the bug. Ensure your code adheres to the existing style and conventions.
    -   Use English variable names.
    -   Add German inline comments to explain complex logic.
    -   Include English docstrings for all classes and public methods.
    -   Add or update type hints.
6.  **Write Tests**: For new features, write unit tests. For bug fixes, add a test that reproduces the bug and then passes after your fix.
    -   Run tests: `pytest`
7.  **Lint Your Code**: Ensure your code passes linting and type checks:
    ```bash
    flake8 .
    mypy .
    ```
8.  **Commit Your Changes**: Write clear and concise commit messages. Reference the issue number if applicable.
    ```bash
    git commit -m "feat: Add YAML configuration loading (closes #123)"
    ```
9.  **Push to Your Fork**: Push your branch to your forked repository on GitHub.
    ```bash
    git push origin feature/your-feature-name
    ```
10. **Open a Pull Request**: Go to the original `intelligent-json-merger` repository on GitHub and open a pull request from your branch. Provide a detailed description of your changes, including:
    -   What problem does it solve?
    -   How was it implemented?
    -   Are there any breaking changes or special considerations?
    -   Reference the related issue(s).

## Code Style

-   Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code.
-   Use Black for code formatting (optional, but encouraged).
-   Use `flake8` for linting and `mypy` for type checking.

## Documentation

-   All public classes, methods, and functions should have English docstrings.
-   Inline comments should be in German to aid understanding for a broader audience.
-   If you add a new feature, consider updating the `README.md` and `README_de.md` files, and potentially the `docs/architecture_en.md` and `docs/architecture_de.md`.

Thank you for contributing to the Intelligent JSON Merger project!