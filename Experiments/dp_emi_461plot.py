from __future__ import annotations

import ast
import csv
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

# File names relative to this script
LIMIT_FILES = {
    "above": ("above_deck.csv", "Above deck & exposed below deck"),
    "below": ("below_deck.csv", "Below deck"),
}
MEASUREMENT_FILES = [
    ("dp_emi_baseline.csv", "DP EMI baseline (no antenna)"),
    ("dp_emi_antenna.csv", "DP EMI antenna"),
]

# Conversion factor from dBuV to dBuV/m (user-supplied scale)
DBUV_TO_DBUVM_DELTA = 1.0


def load_limit_curve(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Return frequency (MHz) and limit (dBuV/m) arrays."""
    data = np.loadtxt(path, delimiter=",")
    if data.ndim != 2 or data.shape[1] < 2:
        raise ValueError(f"{path} does not look like a two-column CSV file")
    return data[:, 0], data[:, 1]


def _parse_band_key(band_str: str) -> Tuple[float, str]:
    """Extract the start frequency to preserve band ordering."""
    try:
        parsed = ast.literal_eval(band_str)
        if isinstance(parsed, dict) and "start_hz" in parsed:
            return float(parsed["start_hz"]), parsed.get("label", band_str)
    except (ValueError, SyntaxError):
        pass

    # Fallback: no metadata encoded, rely on original string as label.
    # Use zero start so sorting at least groups unknown entries together.
    return 0.0, band_str


def load_measurement(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load a measurement CSV (baseline / antenna) and stitch bands together.

    Returns frequency (MHz) and amplitude (dBuV/m).
    """
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header row")

        bands: Dict[str, Dict[str, List[float]]] = {}
        for row in reader:
            band_key = row["band"]
            bands.setdefault(band_key, {"freqs": [], "amps": []})
            bands[band_key]["freqs"].append(float(row["freq_Hz"]))
            amp_dbuV = float(row["amplitude_dBuV"])
            bands[band_key]["amps"].append(amp_dbuV - DBUV_TO_DBUVM_DELTA)

    stitched_freqs: List[np.ndarray] = []
    stitched_amps: List[np.ndarray] = []

    segments = []
    for band_str, data in bands.items():
        start_hz, _ = _parse_band_key(band_str)
        freq_arr = np.asarray(data["freqs"])
        amp_arr = np.asarray(data["amps"])
        segments.append((start_hz or freq_arr[0], freq_arr, amp_arr))

    # Order by start frequency to build one continuous sweep
    for _, freq_arr, amp_arr in sorted(segments, key=lambda seg: seg[0]):
        stitched_freqs.append(freq_arr)
        stitched_amps.append(amp_arr)

    freqs_MHz = np.concatenate(stitched_freqs) / 1e6
    amps_dBuVm = np.concatenate(stitched_amps)
    return freqs_MHz, amps_dBuVm


def plot_curves(
    deck_curves: Iterable[Tuple[str, np.ndarray, np.ndarray]],
    measurement_curves: Iterable[Tuple[str, np.ndarray, np.ndarray]],
) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.set_xscale("log")
    ax.set_xlim(0.01, 100000)
    ax.set_ylim(0, 110)
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Electric Field Strength (dBuV/m)")

    for label, freq, limit in deck_curves:
        ax.plot(freq, limit, linewidth=2, label=label)

    for label, freq, amps in measurement_curves:
        ax.plot(freq, amps, linewidth=1.2, label=label)

    ax.grid(True, which="both", color="0.85", linestyle="-")
    ax.legend()
    fig.tight_layout()
    plt.show()


def main() -> None:
    base_dir = Path(__file__).parent

    deck_curves = []
    for key, (filename, label) in LIMIT_FILES.items():
        path = base_dir / filename
        freq, limit = load_limit_curve(path)
        deck_curves.append((label, freq, limit))

    measurement_curves = []
    for filename, label in MEASUREMENT_FILES:
        path = base_dir / filename
        freq, amps = load_measurement(path)
        measurement_curves.append((label, freq, amps))

    plot_curves(deck_curves, measurement_curves)


if __name__ == "__main__":
    main()
