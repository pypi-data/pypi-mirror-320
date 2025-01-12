from collections.abc import Iterable
from typing import Any, TypeGuard


def is_iterable(
    obj: Any, base_type: tuple[type, ...] = (str, bytes)
) -> TypeGuard[Iterable]:
    return isinstance(obj, Iterable) and not isinstance(obj, base_type)
