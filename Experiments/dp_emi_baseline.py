from __future__ import annotations

import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyvisa
import csv
from Instruments import instrument_strings
from Instruments.rigol_dsa815 import rigol_dsa815

# Measurement configuration
#READINGS_PER_BAND = 4
BANDS = [
    {"label": "10 kHz – 150 kHz", "start_hz": 10_000, "stop_hz": 150_000, "rbw_hz": 200, "ref_level": 20 },
    {"label": "150 kHz – 10 MHz", "start_hz": 150_000, "stop_hz": 10_000_000, "rbw_hz": 9_000, "ref_level": 30 },
    {"label": "10 MHz – 30 MHz", "start_hz": 10_000_000, "stop_hz": 30_000_000, "rbw_hz": 9_000, "ref_level": 30 },
    {"label": "30 MHz – 1500 MHz", "start_hz": 30_000_000, "stop_hz": 1_500_000_000, "rbw_hz": 120_000, "ref_level": 40 },
]
PLOT_PATH = Path(__file__).with_name("dp_emi_baseline.png")
PLOT_PATH2 = Path(__file__).with_name("dp_emi_baseline-samescale.png")
AMPLITUDE_UNITS = "DBUV"


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


def main():
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
            measurements.append(
                {
                    "band": band,
                    "freqs": freqs,
                    "trace": sweep,
                }
            )

        fig, ax = plt.subplots(2, 2, figsize=(14, 8))
        axes = ax.flatten()
        for axis, measurement in zip(axes, measurements):
            band = measurement["band"]
            rbw_label = format_rbw(band["rbw_hz"])
            freq_scale, x_label = freq_axis(measurement["freqs"])

            axis.plot(
                freq_scale,
                measurement["trace"],
                color="C0",
                linewidth=1.5,
                label="",
            )

            axis.set_title(f"{band['label']} (RBW {rbw_label})")
            axis.set_xlabel(x_label)
            axis.set_ylabel(f"Amplitude ({y_units})")
            axis.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.6)
            axis.legend(loc="best")

        fig.suptitle(f"DP EMI Baseline", fontsize=14)
        fig.tight_layout()
        fig.savefig(PLOT_PATH, dpi=300, bbox_inches="tight")
        print(f"\nPlot saved to {PLOT_PATH}")
        plt.show()

        for axis, measurement in zip(axes, measurements):
                band = measurement["band"]
                rbw_label = format_rbw(band["rbw_hz"])
                freq_scale, x_label = freq_axis(measurement["freqs"])

                axis.plot(
                    freq_scale,
                    measurement["trace"],
                    color="C0",
                    linewidth=1.5,
                    label="",
                )

                axis.set_title(f"{band['label']} (RBW {rbw_label})")
                axis.set_xlabel(x_label)
                axis.set_ylabel(f"Amplitude ({y_units})")
                axis.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.6)
                axis.legend(loc="best")
                axis.set_ylim((-10, 40))

        fig.suptitle(f"DP EMI Baseline - Same Scale", fontsize=14)
        fig.tight_layout()
        fig.savefig(PLOT_PATH2, dpi=300, bbox_inches="tight")
        print(f"\nPlot saved to {PLOT_PATH}")
        plt.show()
    finally:
        spec_an.close()
        csv_path = "dp_emi_baseline.csv"
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
