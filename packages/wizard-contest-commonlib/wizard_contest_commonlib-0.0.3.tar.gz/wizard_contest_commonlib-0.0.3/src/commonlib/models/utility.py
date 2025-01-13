from __future__ import annotations

import typing as tp

from pydantic import BaseModel


class Pair[T](BaseModel):
    first: T
    second: T

    def __init__(self, values: tp.Iterable[T]) -> None:
        iterator = iter(values)
        first = next(iterator)
        second = next(iterator)
        try:
            next(iterator)
        except StopIteration:
            super().__init__(
                first=first,
                second=second,
            )
            return
        raise ValueError('Expected 2 values, got more')

    def __getattr__(self, item) -> Pair[tp.Any]:
        return Pair([getattr(self.first, item), getattr(self.second, item)])

    def __iter__(self) -> tp.Iterator[T]:
        return iter((self.first, self.second))

    def __getitem__(self, index: int) -> T:
        if index == 0:
            return self.first
        elif index == 1:
            return self.second
        else:
            raise ValueError('Index out of range')
