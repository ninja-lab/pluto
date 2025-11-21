from __future__ import annotations

import ast
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyvisa

from Instruments import instrument_strings
from Instruments.rigol_dsa815 import rigol_dsa815

# Measurement configuration
BANDS = [
    {"label": "10 kHz - 150 kHz", "start_hz": 10_000, "stop_hz": 150_000, "rbw_hz": 200, "ref_level": 20},
    {"label": "150 kHz - 10 MHz", "start_hz": 150_000, "stop_hz": 10_000_000, "rbw_hz": 9_000, "ref_level": 30},
    {"label": "10 MHz - 30 MHz", "start_hz": 10_000_000, "stop_hz": 30_000_000, "rbw_hz": 9_000, "ref_level": 30},
    {"label": "30 MHz - 1500 MHz", "start_hz": 30_000_000, "stop_hz": 1_500_000_000, "rbw_hz": 120_000, "ref_level": 40},
]
PLOT_PATH = Path(__file__).with_name("dp_emi_ant.png")
PLOT_PATH2 = Path(__file__).with_name("dp_emi_ant-samescale.png")
AMPLITUDE_UNITS = "DBUV"


def band_key_from_range(start_hz: float, stop_hz: float) -> tuple[int, int]:
    """Return a tuple key that uniquely identifies a frequency span."""
    return int(round(start_hz)), int(round(stop_hz))


def find_spectrum_analyzer() -> rigol_dsa815:
    """Return the first connected Rigol DSA815 spectrum analyzer."""
    rm = pyvisa.ResourceManager()
    spec_an = None

    for resource_id in rm.list_resources():
        try:
            inst = rm.open_resource(resource_id, send_end=True)
            name_str = inst.query("*IDN?").strip()
            if name_str == instrument_strings.RigolDSA815:
                spec_an = rigol_dsa815(inst)
                print(f"Connected to: {spec_an.name.rstrip()}")
                break
            inst.close()
        except pyvisa.errors.VisaIOError:
            print(f"{resource_id} is not what we're looking for, continuing...\n")

    if spec_an is None:
        raise RuntimeError("Rigol DSA815 not found on any VISA resource.")

    return spec_an


def freq_axis(freqs_hz: np.ndarray) -> tuple[np.ndarray, str]:
    """Return frequency axis scaled for plotting and the axis label."""
    if freqs_hz[-1] < 1e6:
        return freqs_hz / 1e3, "Frequency (kHz)"
    return freqs_hz / 1e6, "Frequency (MHz)"


def format_rbw(rbw_hz: float) -> str:
    """Return a string representation of the RBW in Hz/kHz."""
    return f"{rbw_hz / 1e3:g} kHz" if rbw_hz >= 1_000 else f"{rbw_hz:g} Hz"


def load_baseline(path: Path | None = None) -> list[dict[str, np.ndarray]]:
    """Load baseline sweeps from CSV and return band-to-trace entries."""
    csv_path = path or Path(__file__).with_name("dp_emi_baseline.csv")
    if not csv_path.exists():
        print(f"Baseline file {csv_path} not found; skipping baseline overlay.")
        return []

    bands: dict[str, dict[str, list[float]]] = {}
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_band = row["band"]
            try:
                parsed_band = ast.literal_eval(raw_band)
                band_label = parsed_band.get("label") if isinstance(parsed_band, dict) else str(parsed_band)
            except (ValueError, SyntaxError):
                band_label = raw_band

            bands.setdefault(band_label, {"freqs": [], "trace": []})
            bands[band_label]["freqs"].append(float(row["freq_Hz"]))
            bands[band_label]["trace"].append(float(row["amplitude_dBuV"]))

    measurements_loaded: list[dict[str, np.ndarray]] = []
    for band_label, data in bands.items():
        freqs = np.array(data["freqs"])
        trace = np.array(data["trace"])
        if freqs.size == 0:
            continue
        key = band_key_from_range(freqs[0], freqs[-1])
        measurements_loaded.append({"band": band_label, "freqs": freqs, "trace": trace, "key": key})

    if measurements_loaded:
        loaded_labels = ", ".join(entry["band"] for entry in measurements_loaded)
        print(f"Loaded baseline data for: {loaded_labels}")
    return measurements_loaded


def plot_measurements(
    measurements: list[dict[str, object]],
    baseline_lookup: dict[tuple[int, int], dict[str, np.ndarray]],
    y_units: str,
    title: str,
    output_path: Path,
    y_limits: tuple[float, float] | None = None,
) -> None:
    """Plot the antenna measurements with optional baseline overlays."""
    fig, ax = plt.subplots(2, 2, figsize=(14, 8))
    axes = ax.flatten()

    for axis, measurement in zip(axes, measurements):
        band = measurement["band"]
        freqs: np.ndarray = measurement["freqs"]
        trace: np.ndarray = measurement["trace"]
        band_label = band["label"]
        rbw_label = format_rbw(band["rbw_hz"])
        freq_scale, x_label = freq_axis(freqs)

        axis.plot(freq_scale, trace, color="C0", linewidth=1.5, label="Antenna sweep")

        baseline_key = band_key_from_range(band["start_hz"], band["stop_hz"])
        baseline = baseline_lookup.get(baseline_key)
        if baseline is not None:
            scale_factor = freq_scale[-1] / freqs[-1] if freqs[-1] else 1.0
            axis.plot(
                baseline["freqs"] * scale_factor,
                baseline["trace"],
                color="C1",
                linewidth=1.2,
                linestyle="--",
                label="Baseline",
            )

        axis.set_title(f"{band_label} (RBW {rbw_label})")
        axis.set_xlabel(x_label)
        axis.set_ylabel(f"Amplitude ({y_units})")
        axis.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.6)
        if y_limits:
            axis.set_ylim(y_limits)
        axis.legend(loc="best")

    for axis in axes[len(measurements) :]:
        axis.axis("off")

    fig.suptitle(title, fontsize=14)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"\nPlot saved to {output_path}")
    plt.show()


def main():
    baseline_measurements = load_baseline()
    baseline_lookup = {entry["key"]: entry for entry in baseline_measurements}

    spec_an = find_spectrum_analyzer()
    try:
        spec_an.set_data_format("ASC")
        spec_an.set_units(AMPLITUDE_UNITS)
        y_units = spec_an.get_units()

        measurements = []
        for band in BANDS:
            start_hz = band["start_hz"]
            stop_hz = band["stop_hz"]
            rbw_hz = band["rbw_hz"]
            label = band["label"]

            print(f"\nMeasuring {label} with RBW {format_rbw(rbw_hz)}")
            spec_an.set_start_stop_freq(start_hz, stop_hz)
            spec_an.set_rbw(rbw_hz)
            spec_an.set_ref_level(band["ref_level"])
            spec_an.wait_for_sweeps(n_sweeps=1, margin=0.2)
            sweep = spec_an.get_trace(trace_num=1)

            print(f"  Captured sweep for {label}")

            freqs = np.linspace(start_hz, stop_hz, sweep.size)
            measurements.append({"band": band, "freqs": freqs, "trace": sweep})

        plot_measurements(
            measurements,
            baseline_lookup,
            y_units,
            "DP EMI Antenna",
            PLOT_PATH,
        )

        plot_measurements(
            measurements,
            baseline_lookup,
            y_units,
            "DP EMI Antenna - Same Scale",
            PLOT_PATH2,
            y_limits=(-10, 40),
        )
    finally:
        spec_an.close()
        csv_path = "./Experiments/dp_emi_antenna.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            # header
            writer.writerow(["band", "point", "freq_Hz", "amplitude_dBuV"])

            for m in measurements:
                band = m["band"]
                freqs = np.asarray(m["freqs"])
                trace = np.asarray(m["trace"])

                for i, (f_hz, amp) in enumerate(zip(freqs, trace)):
                    writer.writerow([band, i, f_hz, amp])

        print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
