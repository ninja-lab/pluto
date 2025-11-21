#%%



from pathlib import Path

import matplotlib.pyplot as plt
matplotlib.use("module://matplotlib_inline.backend_inline")
import numpy as np


def load_curve(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return frequency (MHz) and limit level (dBuV/m) arrays from a CSV file."""
    data = np.loadtxt(path, delimiter=",")
    return data[:, 0], data[:, 1]


def main() -> None:
    base_dir = Path(__file__).parent
    above_freq, above_limit = load_curve(base_dir / "above_deck.csv")
    below_freq, below_limit = load_curve(base_dir / "below_deck.csv")

    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.set_xscale("log")
    ax.set_xlim(0.01, 100000)
    ax.set_ylim(20, 110)
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Limit Level (dBuV/m)")

    ax.plot(above_freq, above_limit, label="Above deck & exposed below deck", linewidth=2)
    ax.plot(below_freq, below_limit, label="Below deck", linewidth=2)

    ax.grid(True, which="both", color="0.85", linestyle="-")
    ax.legend()
    fig.tight_layout()

    plt.show()


if __name__ == "__main__":
    main()

# %%
