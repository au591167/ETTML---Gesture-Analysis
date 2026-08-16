"""Generate the before/after 3D-axis visual used by the exam presentation."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, FancyBboxPatch


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "assets" / "adxl343-axis-orientation.png"


def double_arrow(ax, start, end, color, label, label_xy, linewidth=4.5):
    arrow = FancyArrowPatch(
        start, end, arrowstyle="<|-|>", mutation_scale=18,
        linewidth=linewidth, color=color, shrinkA=0, shrinkB=0,
    )
    ax.add_patch(arrow)
    ax.text(*label_xy, label, color=color, fontsize=17, fontweight="bold",
            ha="center", va="center")


def draw_board(ax):
    """Draw a simple perspective board so the three directions read as 3D."""
    board = Polygon(
        [(0.12, 0.23), (0.72, 0.13), (0.90, 0.42), (0.30, 0.53)],
        closed=True, facecolor="#dbeafe", edgecolor="#2563eb", linewidth=2.6,
    )
    ax.add_patch(board)
    chip = Polygon(
        [(0.40, 0.29), (0.58, 0.26), (0.65, 0.37), (0.47, 0.40)],
        closed=True, facecolor="#0f172a", edgecolor="#334155", linewidth=1.2,
    )
    ax.add_patch(chip)
    ax.text(0.525, 0.333, "ADXL343", color="white", fontsize=8.5,
            fontweight="bold", rotation=-8, ha="center", va="center")


def setup_panel(ax, title, title_color, subtitle):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    card = FancyBboxPatch(
        (0.015, 0.025), 0.97, 0.95,
        boxstyle="round,pad=0.01,rounding_size=0.025",
        facecolor="white", edgecolor="#cbd5e1", linewidth=1.6,
    )
    ax.add_patch(card)
    ax.text(0.50, 0.915, title, color=title_color, fontsize=18,
            fontweight="bold", ha="center", va="center")
    ax.text(0.50, 0.855, subtitle, color="#475569", fontsize=11.5,
            ha="center", va="center")


def main() -> None:
    fig, (before, after) = plt.subplots(1, 2, figsize=(12, 6.75), dpi=160)
    fig.patch.set_facecolor("#f6f9fc")

    setup_panel(before, "FØR · STARTANTAGELSE", "#c2410c",
                "Jeg troede, at Y var op/ned")
    draw_board(before)
    origin = (0.52, 0.34)
    double_arrow(before, (origin[0], 0.20), (origin[0], 0.79),
                 "#f97316", "Y ?", (0.60, 0.72), 5.5)
    before.text(0.50, 0.105, "Y blev tolket som den lodrette tapakse",
                color="#9a3412", fontsize=11.5, fontweight="bold",
                ha="center", va="center")

    setup_panel(after, "EFTER · MÅLT ORIENTERING", "#166534",
                "Data viste den faktiske retning")
    draw_board(after)
    # Directions relative to the physical prototype: Y left/right,
    # X forward/back, and Z up/down.
    double_arrow(after, (0.18, 0.34), (0.84, 0.34),
                 "#16a34a", "Y · venstre / højre", (0.52, 0.57))
    double_arrow(after, (0.35, 0.18), (0.70, 0.52),
                 "#dc2626", "X · frem / tilbage", (0.70, 0.22))
    double_arrow(after, (0.52, 0.20), (0.52, 0.79),
                 "#2563eb", "Z · op / ned", (0.64, 0.73), 5.5)
    after.text(0.50, 0.105, "Registerrækkefølgen er stadig X, Y, Z",
               color="#0f172a", fontsize=11.5, fontweight="bold",
               ha="center", va="center")

    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.02, top=0.98, wspace=0.035)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, bbox_inches="tight", pad_inches=0.04,
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
