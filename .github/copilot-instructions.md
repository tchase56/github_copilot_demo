## Docstrings

- All functions, classes, and methods **must** include docstrings.
- Docstrings must follow the **Google docstring convention**.

## Type Hints

- All function and method signatures **must** include type hints for all parameters and return values.
- Use built-in types (`list`, `dict`, `tuple`) and `typing` module where needed (e.g., `Optional`, `Union`).

### Google Docstring Example with Type Hints

```python
def example_function(arg1: int, arg2: str) -> bool:
    """Summary line.

    Args:
        arg1 (int): Description of arg1.
        arg2 (str): Description of arg2.

    Returns:
        bool: Description of the return value.

    Raises:
        ValueError: If arg1 is negative.
    """
```
