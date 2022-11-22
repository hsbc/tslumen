"""Common plotting utilities."""
from typing import List, Callable

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex


__all__ = [
    "cmap_to_list",
    "cmapper",
    "ccontrast",
]


def cmap_to_list(colors: str, size: int) -> List[str]:
    """Convert a cmap to a list of specified size"""
    cmap = plt.get_cmap(colors)
    return [rgb2hex(cmap(ix / size)) for ix in range(size)]


def cmapper(
    vmin: float, vmax: float, cmap: str = "PuBu", clip: bool = True, as_hex: bool = True
) -> Callable:
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax, clip=clip)
    mapper = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    if as_hex:
        return lambda value: rgb2hex(mapper.to_rgba(value))
    return lambda value: mapper.to_rgba(value, bytes=True)


def ccontrast(
    r: int, g: int, b: int, dark: str = "#000000", light: str = "#ffffff", thresh: int = 186
) -> str:
    return dark if (r * 0.299 + g * 0.587 + b * 0.114) > thresh else light
