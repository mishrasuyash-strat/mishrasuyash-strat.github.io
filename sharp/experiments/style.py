"""
style.py — one visual identity for every SHARP figure.

Deep-indigo = SHARP (the estimate that survives its own success).
Burnt-coral = the naive snapshot trap.
Warm-paper ground, ochre accent for regime markers.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt

INK      = "#22212b"   # primary text
PAPER    = "#f6f3ec"   # figure background
PANEL    = "#fbfaf5"   # axes background
GRID     = "#e4ddcf"
SHARP   = "#2b3a67"   # deep indigo
INDIGO_2 = "#5b6fa6"
NAIVE    = "#cf6a45"   # burnt coral
NAIVE_2  = "#e0a07f"
OCHRE    = "#c7a24a"   # regime / accent
TEAL     = "#2f7d78"   # secondary accent
MUTED    = "#8c8577"


def apply():
    mpl.rcParams.update({
        "figure.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "axes.facecolor": PANEL,
        "axes.edgecolor": "#c9c1b1",
        "axes.linewidth": 1.0,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.9,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "figure.dpi": 130,
    })


def titleblock(ax, kicker, title):
    """A two-line editorial title: small ochre kicker above a bold title."""
    ax.set_title("")
    ax.text(0.0, 1.14, kicker, transform=ax.transAxes,
            fontsize=10.5, color=OCHRE, fontweight="bold")
    ax.text(0.0, 1.045, title, transform=ax.transAxes,
            fontsize=14.5, color=INK, fontweight="bold")
