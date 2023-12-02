from ast import Expression
from typing import Any

class BooleanExpression(Expression):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)