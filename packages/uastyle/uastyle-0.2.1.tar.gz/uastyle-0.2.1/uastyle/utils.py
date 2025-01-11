import matplotlib as mpl

# import matplotlib.pylab as plt
from cycler import cycler

from .constants import colors


def mm_to_inch(mm: float) -> float:
    return mm / 25.4


def make_default_colors():
    mpl.rcParams.update(
        {
            "axes.prop_cycle": cycler("color", colors),
        }
    )


# DEFAULT_MARKEREDGEWIDTH = 1
# DEFAULT_SIZE = 10


def make_default_font_size(font_size: int = 12):
    mpl.rcParams.update(
        {
            "font.size": font_size,
            "axes.titlesize": font_size,
            "axes.labelsize": font_size,
            "xtick.labelsize": font_size,
            "ytick.labelsize": font_size,
            "legend.fontsize": font_size,
            "figure.titlesize": font_size,
            "figure.labelsize": font_size,
        }
    )


# def reset
