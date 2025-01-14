__all__ = ["BaseColumn"]

from enum import Enum
from typing import Any, Sequence

from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.orm import InstrumentedAttribute


class Paginator:
    ...


class BaseColumn(Enum):
    def __new__(cls, value, column: InstrumentedAttribute):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._column = column
        return obj
    
    @property
    def column(self) -> InstrumentedAttribute:
        return self._column
    
    def like(self, value: str) -> ColumnExpressionArgument:
        return self.column.like(f"%{value}%")
    
    def in_(self, values: Sequence[Any]) -> ColumnExpressionArgument:
        return self.column.in_(values)
    
    def not_in(self, values: Sequence[Any]) -> ColumnExpressionArgument:
        return self.column.not_in(values)
    
    @property
    def asc(self):
        return self.column.asc()
    
    @property
    def desc(self):
        return self.column.desc()
    
    def __eq__(self, value: Any) -> ColumnExpressionArgument:
        return self.column == value
    
    def __ne__(self, value: Any) -> ColumnExpressionArgument:
        return self.column != value
    
    def __ge__(self, value: Any) -> ColumnExpressionArgument:
        return self.column >= value
    
    def __gt__(self, value: Any) -> ColumnExpressionArgument:
        return self.column > value
    
    def __le__(self, value: Any) -> ColumnExpressionArgument:
        return self.column <= value
    
    def __lt__(self, value: Any) -> ColumnExpressionArgument:
        return self.column < value
    
    