from __future__ import annotations

from pydantic import BaseModel

CPU_TIME_RE = r'^(?:(?P<days>\d+)-)?(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)$'


class PostFixUnit:
    def __init__(self, value: str) -> None:
        self.value: float | None = None
        if value.endswith('K'):
            self.value = float(value[:-1]) / 1024
            return

        if value.endswith('M'):
            self.value = float(value[:-1])
            return

        if value.endswith('G'):
            self.value = float(value[:-1]) * 1024
            return

        try:
            self.value = float(value) / (1024 * 1204)
        except ValueError:
            self.value = None

    def __str__(self) -> str:
        if self.value is None:
            return '-'
        return f'{self.value}'

    def __repr__(self) -> str:
        if self.value is None:
            return '-'
        return f'{self.value}'


class MemoryUsed:
    def __init__(self, value: str | int | float | None = None) -> None:
        self.value: float | None = None
        if value is None:
            self.value = None
            return

        if isinstance(value, str):
            if value.endswith('K'):
                self.value = float(value[:-1]) / 1024
                return

            if value.endswith('M'):
                self.value = float(value[:-1])
                return

            if value.endswith('G'):
                self.value = float(value[:-1]) * 1024
                return

        try:
            self.value = float(value) / (1024 * 1024)
        except ValueError:
            self.value = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MemoryUsed):
            return NotImplemented
        return self.value == other.value

    def __str__(self) -> str:
        return f'{self.GB} GB'

    def __repr__(self) -> str:
        return f'{self.GB} GB'

    def __add__(self, other: MemoryUsed) -> MemoryUsed:
        if self.value is None or other.value is None:
            raise TypeError('Cannot add MemoryUsed and MemoryUsed where one value is None ')

        return MemoryUsed.from_mb(self.value + other.value)

    def __sub__(self, other: MemoryUsed) -> MemoryUsed:
        if self.value is None or other.value is None:
            raise TypeError('Cannot subtract MemoryUsed and MemoryUsed where one value is None ')

        return MemoryUsed.from_mb(self.value - other.value)

    def __truediv__(self, other: int | float) -> MemoryUsed:
        if self.value is None:
            raise TypeError('Cannot divide MemoryUsed when value is None ')

        return MemoryUsed.from_mb(self.value / other)

    @classmethod
    def from_mb(cls, value: float) -> MemoryUsed:
        val = cls()
        val.value = value
        return val

    @property
    def MB(self) -> float:  # pylint: disable=invalid-name
        if self.value is None:
            return 0
        return self.value

    @property
    def GB(self) -> float:  # pylint: disable=invalid-name
        if self.value is None:
            return 0
        return self.value // 1024


class Number(BaseModel):
    """ Class for capturing certain number information in the JSON output. """
    set: bool = False
    infinite: bool = False
    number: int = -1

    def __str__(self) -> str:
        if not self.set:
            return 'NA'

        if self.infinite:
            return '∞'

        return str(self.number)
