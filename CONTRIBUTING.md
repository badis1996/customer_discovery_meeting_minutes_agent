# Contributing to Customer Discovery Meeting Minutes Agent

Thank you for your interest in contributing to the Customer Discovery Meeting Minutes Agent project! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions related to this project. Harassment and other exclusionary behavior are not acceptable.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to see if the problem has already been reported. When you are creating a bug report, please include as many details as possible:

- A clear and descriptive title
- Steps to reproduce the behavior
- Expected behavior
- Actual behavior
- Screenshots or logs if applicable
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome. Please include:

- A clear and descriptive title
- A step-by-step description of the suggested enhancement
- Any relevant examples to demonstrate the enhancement
- Explain why this enhancement would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Implement your changes
4. Add or update tests as needed
5. Make sure all tests pass
6. Submit a pull request

## Development Environment Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/customer_discovery_meeting_minutes_agent.git
cd customer_discovery_meeting_minutes_agent
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a local config file:

```bash
cp config.example.yml config.yml
# Edit config.yml with your settings
```

## Testing

Run tests using pytest:

```bash
python -m pytest
```

## Style Guide

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Include docstrings for all functions, classes, and modules
- Keep functions small and focused on a single task
- Write comments for complex sections of code

## Documentation

Please update the documentation when making changes. This includes:

- Code comments and docstrings
- README.md and other markdown files
- Example configurations

## Questions?

If you have any questions about contributing, please open an issue and label it as a question.
