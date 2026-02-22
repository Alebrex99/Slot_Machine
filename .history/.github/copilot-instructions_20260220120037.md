# Project general coding guidelines

## Code Style
- Use semantic HTML5 elements (header, main, section, article, etc.)
- Prefer modern JavaScript (ES6+) features like const/let, arrow functions, and template literals

## Naming Conventions
- Use PascalCase for component names, interfaces, and type aliases
- Use camelCase for variables, functions, and methods
- Prefix private class members with underscore (_)
- Use ALL_CAPS for constants

## Code Quality
- Write clean, readable, and maintainable Python code
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all classes and functions

## Project Structure
- Separate concerns into different modules (game logic, UI, utilities)
- Keep functions small and focused on a single responsibility
- Use classes to encapsulate related data and behavior

## Python Specific
- Use f-strings for string formatting
- Prefer list comprehensions over traditional loops where appropriate
- Use `with` statements for resource management
- Handle exceptions with specific exception types, avoid bare `except`
- Use `__init__.py` files to define package structure

## Testing
- Write unit tests for all game logic functions
- Use `pytest` as the testing framework
- Name test functions with `test_` prefix

## Slot Machine Specific
- Define reel symbols and payouts as constants
- Separate random number generation from game logic for easier testing
- Validate all player inputs (bet amounts, number of lines, etc.)
- Keep track of player balance and prevent invalid bets
- Use meaningful variable and function names that clearly describe their purpose
- Include helpful comments for complex logic
- Add error handling for user inputs and API calls
