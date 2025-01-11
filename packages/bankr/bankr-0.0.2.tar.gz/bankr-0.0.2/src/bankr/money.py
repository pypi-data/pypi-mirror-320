"""Class for internal representation of money as integers
Based on: https://github.com/ArjanCodes/examples/tree/main/2023/money
"""

from dataclasses import dataclass
from typing import Self

import numpy as np


@dataclass
class Money:
    cents: np.int64
    currency: str

    @classmethod
    def m(cls, amount: float, currency: str = "€") -> Self:
        return cls(np.int64(np.round(amount * 100)), currency)

    def __str__(self):
        return f"{self.cents / 100 : >10.2f}{self.currency}"

    def __add__(self, other: Self) -> Self:
        if isinstance(other, Money):
            return Money(self.cents + other.cents, self.currency)

    def __sub__(self, other: Self) -> Self:
        if isinstance(other, Money):
            return Money(self.cents - other.cents, self.currency)
