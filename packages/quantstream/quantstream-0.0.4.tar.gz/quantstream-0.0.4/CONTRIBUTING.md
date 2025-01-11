# Contributing to QuantStream

Thank you for your interest in contributing to QuantStream! We welcome contributions from the community. This document outlines the process for contributing to the project.

## How to Contribute

1. **Fork the Repository**: Start by forking the repository to your GitHub account.

1. **Create a Branch**: Create a new branch in your forked repository for your changes. Use a meaningful name, such as `feature/add-new-model` or `fix/bug-description`.

   ```bash
   git checkout -b feature/add-new-model
   ```

1. **Make Your Changes**: Develop your feature or fix. Ensure your code adheres to the project’s coding standards (see Code Style and Linting).

1. **Run Tests**: Run all tests to make sure your changes do not break any existing functionality.

   ```bash
   uv run pytest tests/
   ```

1. **Run Code Linting**: Make sure your code passes the linting checks. We use `ruff` for linting:

   ```bash
   uv run ruff check .
   ```

1. **Commit Your Changes**: Commit your changes with a meaningful commit message. Please follow conventional commit guidelines (e.g., `feat: add new data model`, `fix: resolve API key issue`).

   ```bash
   git add .
   git commit -m "feat: add new financial model for stock analysis"
   ```

1. **Push Your Branch**: Push the branch to your forked repository:

   ```bash
   git push origin feature/add-new-model
   ```

1. **Open a Pull Request**: Open a pull request (PR) from your forked repository to the main QuantStream repository. Please provide a detailed description of the changes in your PR and reference any related issues.

1. **Review Process**: Your pull request will be reviewed by project maintainers. Please be open to feedback and make any necessary changes.

## Code Style and Linting

QuantStream follows standard Python coding conventions and uses `ruff` for code linting. Please ensure that your code adheres to the following style guidelines:

- **Code Linting**: Run `ruff` to check code style:

  ```bash
  uv run ruff check .
  ```

- **Code Formatting**: Use `black` to format the code before submitting a pull request.

  ```bash
  uv run black .
  ```

## Running Tests

We use `pytest` for testing. Ensure all tests pass before submitting your contribution:

```bash
uv run pytest tests/
```

You can also add new tests for any features you contribute.

## License

By contributing to QuantStream, you agree that your contributions will be licensed under the MIT License.

Thank you for your contribution!
