"""
Copyright Wenyi Tang 2024-2025

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

from typing import Optional, Set, Type, TypeVar

T = TypeVar("T")


def want_input(
    prompt: str,
    dtype: Type[T] = str,
    choices: Optional[Set[str]] = None,
    defaults: Optional[T] = None,
) -> Optional[T]:
    """Handle a user input value from console."""

    if choices and defaults is not None:
        assert defaults in choices, "default value must be in choices"
    while True:
        user_str = input(prompt)
        if user_str == "" and defaults is not None:
            return defaults
        try:
            user_data = dtype(user_str)
            if choices and user_data not in choices:
                raise ValueError(f"Invalid input, please choose from {choices}")
            return user_data
        except Exception as e:  # pylint: disable=broad-except
            print(e)
            print("Invalid input, please try again.")
