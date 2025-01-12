# yacli_menu

`yacli_menu` simplifies the creation of CLI menus and interactive command-line interfaces.
It allows you to define commands, prompt the user for input, and execute the chosen command.

## Installation

```bash
pip install yacli_menu
```

## Example

```python
# file: example.py
from yacli_menu import command, run_menu

@command("Add Numbers")
def add():
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))
    print(f"Result: {a + b}")

@command("Subtract Numbers")
def subtract():
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))
    print(f"Result: {a - b}")

@command("Multiply Numbers")
def multiply():
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))
    print(f"Result: {a * b}")

if __name__ == "__main__":
    run_menu() 

```

```bash
$ python example.py
1. Add Numbers
2. Subtract Numbers
3. Multiply Numbers
Enter command: 1
...
```

You can find more examples in the [examples](./examples) directory.


## API Reference

### `@command(name: str)`

Decorator that registers a function as a menu command.

Parameters:
- `name` (str): The name that will be displayed in the menu for this command

The decorated function should take no arguments.

```python
@command("Your command name")
def your_function():
    # ... command implementation ...
    pass
```

### `run_menu(**kwargs)`

Starts the interactive menu loop.

Parameters:
- `prompt: (str, optional)` - Input prompt text. Defaults to `"Enter choice: "`;
- `show_menu_on_invalid: (bool, optional)` -  Re-display menu if the user inserts an invalid option. Defaults to `False`;
- `show_menu_on_empty: (bool, optional)` - Re-display menu after empty input. Defaults to `False`;
- `item_formatter: (Callable[[str, str], str], optional)` - Function to format menu items. Defaults to "{order}. {name}";
- `order_formatter: (Callable[[int], str], optional)` - Function to format menu item numbers. By default returns the string representation of the number;
- `order_start: (int, optional)` - Starting number for menu items. Defaults to 1;
- `exit_order_last: (bool, optional)` - If this option is True, the exit command will be Place exit option last instead of 0. Defaults to `False`;
- `exit_name: (str, optional)` - Text for exit option. Defaults to "Exit";

```python
# Basic usage
run_menu()

# Customized menu
run_menu(
    prompt="> ",
    show_menu_on_invalid=True,
    item_formatter=lambda o, n: f"{o}) {n}",
    exit_name="Quit",
)
```

## Contributing

Contributions to `yacli_menu` are welcome! If you find issues or have suggestions for improvements, please open an [issue](https://github.com/afonsocrg/yacli_menu/issues) or submit a [pull request](https://github.com/afonsocrg/yacli_menu/pulls).

## License

Licensed under the Apache License 2.0, Copyright © 2023-present afonsocrg

See [LICENSE](./LICENSE) for more information.