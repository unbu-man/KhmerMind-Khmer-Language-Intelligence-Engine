"""Example-budgeted memory policies for the rehearsal comparison."""
from dataclasses import dataclass, field

import numpy as np


@dataclass
class Reservoir:
    capacity: int
    items: list[int] = field(default_factory=list)
    count: int = 0

    def add(self, incoming: list[int], rng: np.random.Generator) -> None:
        for index in incoming:
            self.count += 1
            if len(self.items) < self.capacity:
                self.items.append(index)
                continue
            slot = rng.integers(self.count)
            if slot < self.capacity:
                self.items[slot] = index


def balanced_memory(
    retained: list[int], incoming: list[int], labels: np.ndarray,
    capacity: int, rng: np.random.Generator,
) -> list[int]:
    by_fact = {}
    for index in [*retained, *incoming]:
        by_fact.setdefault(int(labels[index]), []).append(index)
    fact_order = rng.permutation(sorted(by_fact))
    for candidates in by_fact.values():
        rng.shuffle(candidates)

    result = []
    while fact_order.size and len(result) < capacity:
        for fact in fact_order:
            if len(result) == capacity:
                break
            if by_fact[fact]:
                result.append(by_fact[fact].pop())
        fact_order = np.asarray([fact for fact in fact_order if by_fact[fact]], dtype=int)
    return result
