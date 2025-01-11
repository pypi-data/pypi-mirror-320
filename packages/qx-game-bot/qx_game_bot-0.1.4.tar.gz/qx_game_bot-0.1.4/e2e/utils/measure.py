from timeit import repeat

from numpy import average


def measure(fn, r=20):
    name = fn.__name__
    times = repeat(
        f"{name}()",
        setup=f"from __main__ import {name}",
        number=1,
        repeat=r,
    )
    best = min(times) * 1000
    worst = max(times) * 1000
    avg = average(times) * 1000
    print(f"{name}() - Best: {best:.2f}; Worst: {worst:.2f}; Avg: {avg:.2f}")
