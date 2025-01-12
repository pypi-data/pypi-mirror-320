from functools import wraps
from typing import Callable

commands = {}

def command(name: str) -> Callable[[Callable], Callable]:
    """
    This decorator registers the decorated function as a command.
    If name is specified, it will be used as the command name,
    otherwise the function name will be used.
    """

    def decorator(f):
        @wraps(f)
        def wrapper():
            return f()

        key = name
        commands[key] = wrapper
        return wrapper

    return decorator

def _exit():
    raise SystemExit


def print_menu(
    item_formatter: Callable[[str, str], str] = lambda order, name: f"{order}. {name}",
    order_formatter: Callable[[int], str] = str,
    order_start: int = 1,
    exit_order_last: bool = False,
    exit_name: str = "Exit",
) -> dict:
    # This is the mapping of the symbol that the user will input to the command that will be executed
    menu_items = {}

    # Starting from 1 because 0 is reserved for the exit command
    for i, name in list(enumerate(commands.keys(), start=order_start)):
        order = order_formatter(i)
        print(item_formatter(order, name))
        menu_items[order] = commands[name]
    
    exit_order = len(commands.keys()) + order_start if exit_order_last  else 0
    order = order_formatter(exit_order)
    print(item_formatter(order, exit_name))
    menu_items[order] = _exit

    return menu_items


def menu(
    prompt: str = "Enter choice: ",
    show_menu_on_invalid: bool = False,
    show_menu_on_empty: bool = False,
    **kwargs
):
    mapping = print_menu(**kwargs)
    choice = None
    while choice is None:
        choice = input(prompt).strip()
        if choice in mapping:
            return mapping[choice]()
        else:
            if choice == "":
                if show_menu_on_empty:
                    print_menu(**kwargs)
            else:
                print("Invalid choice. Try again.")
                if show_menu_on_invalid:
                    print_menu(**kwargs)

            choice = None

def run_menu(**kwargs):
    try:
        while True:
            menu(**kwargs)
    except SystemExit:
        print("Exiting...")
    except KeyboardInterrupt:
        print("\nExiting...")
    except EOFError:
        print("\n End of input. Exiting...")
