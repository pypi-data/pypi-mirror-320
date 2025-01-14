from __future__ import annotations

import functools
import time
from typing import Optional, Union

import pandas as pd


def time_it(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        value = func(*args, **kwargs)
        print(time.perf_counter() - start)
        return value

    return wrapper


def os_cut(
    x: Union[list[Union[int, float]], pd.Series],
    bins: list,
    start_label: str = "lager dan",
    end_label: str = "en hoger",
    add_edge: Optional[int] = None,
    sep: str = " - ",
) -> pd.Series:
    # Add non_overlap to left edge/boundary
    if not add_edge:
        add_edge = 0

    start_l = [f"{start_label} {bins[1]}"]
    inbetween_labels = [
        f"{bins[i] + add_edge}{sep}{bins[i+1]}" for i in range(1, len(bins) - 2)
    ]
    end_l = [f"{bins[-2]} {end_label}"]

    return pd.cut(x, bins=bins, labels=start_l + inbetween_labels + end_l)  # type: ignore
