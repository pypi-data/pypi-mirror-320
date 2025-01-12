from collections.abc import Sequence
from typing import Any, TypeGuard


def is_sequence(
    obj: Any, base_type: tuple[type, ...] = (str, bytes)
) -> TypeGuard[Sequence]:
    return isinstance(obj, Sequence) and not isinstance(obj, base_type)
