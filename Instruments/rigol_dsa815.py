import pyvisa
import datetime
import time
import re
import csv
from math import floor, log10
from Instruments.Visa_Instrument import Visa_Instrument
import pandas as pd
import numpy as np
from math import ceil 

class rigol_dsa815(Visa_Instrument):
        def __init__(self, resource, debug=False):
            super().__init__(resource, debug)
            self.inst.timeout = 50000
            
        def set_data_format(self, format='ASC'):
            ''' Sets the data format for waveform data transfer.
            Options are:
            ASC : ASCII
            REAL : Binary
            '''
            self.write(':FORMat:DATA {}'.format(format))

        def get_trace(self, trace_num=1):
            """Gets the trace data from the specified trace number.
            Default is trace 1.
            Returns a numpy array of the trace data (in dB)."""
            # 1) Correct SCPI syntax
            cmd = f":TRACe:DATA? TRACE{trace_num}"

            # 2) Single query (no extra read)
            data_str = self.query(cmd)

            # 3) Strip SCPI definite-length block header, if present
            #    e.g. "#9000009014 -2.017071e+01, -5.86e+01, ..."
            if data_str.startswith('#'):
                try:
                    first_space = data_str.index(' ')
                    payload = data_str[first_space + 1 :]
                except ValueError:
                    # Fallback if format is weird: just use the whole string
                    payload = data_str
            else:
                payload = data_str

            # 4) Split, clean, convert to floats
            parts = [p.strip() for p in payload.split(',') if p.strip()]
            data_floats = [float(p) for p in parts]

            return np.array(data_floats)

# in rigol_dsa815.py, inside class rigol_dsa815

        def get_start_freq(self):
            """Return start frequency in Hz."""
            return float(self.query(':FREQuency:STARt?'))

        def get_stop_freq(self):
            """Return stop frequency in Hz."""
            return float(self.query(':FREQuency:STOP?'))

        def set_units(self, unit: str = "DBM"):
            """
            Set the Y-axis amplitude units.

            SCPI: :UNIT:POWer <unit>

            Typical options (see DSA800 manual):
                DBM, DBUV, DBMV, V, W, etc.
            We don't validate here; we just pass through to the instrument.
            """
            self.write(f":UNIT:POWer {unit}")

        def get_units(self) -> str:
            """
            Query the current Y-axis amplitude units.

            SCPI: :UNIT:POWer?
            """
            return self.query(":UNIT:POWer?").strip()

        # --- Frequency range: start / stop ---

        def set_start_freq(self, start_hz: float):
            """
            Set start frequency, in Hz.

            SCPI: :SENSe:FREQuency:STARt <freq>
            """
            self.write(f":SENSe:FREQuency:STARt {start_hz}")

        def set_stop_freq(self, stop_hz: float):
            """
            Set stop frequency, in Hz.

            SCPI: :SENSe:FREQuency:STOP <freq>
            """
            self.write(f":SENSe:FREQuency:STOP {stop_hz}")

        def set_start_stop_freq(self, start_hz: float, stop_hz: float):
            """
            Convenience method to set start and stop frequency together.

            Both values are in Hz.
            """
            self.set_start_freq(start_hz)
            self.set_stop_freq(stop_hz)

        def get_start_freq(self) -> float:
            """
            Query start frequency (Hz).

            SCPI: :SENSe:FREQuency:STARt?
            """
            return float(self.query(":SENSe:FREQuency:STARt?"))

        def get_stop_freq(self) -> float:
            """
            Query stop frequency (Hz).

            SCPI: :SENSe:FREQuency:STOP?
            """
            return float(self.query(":SENSe:FREQuency:STOP?"))

        # --- RBW / VBW and VBW/RBW ratio ---

        def set_rbw(self, rbw_hz: float, auto: bool = False):
            """
            Set resolution bandwidth (RBW) in Hz.

            SCPI:
                Auto on/off: :SENSe:BANDwidth:RESolution:AUTO ON|OFF
                Value:       :SENSe:BANDwidth:RESolution <rbw>
            """
            if auto:
                self.write(":SENSe:BANDwidth:RESolution:AUTO ON")
            else:
                self.write(":SENSe:BANDwidth:RESolution:AUTO OFF")
                self.write(f":SENSe:BANDwidth:RESolution {rbw_hz}")

        def get_rbw(self) -> float:
            """
            Query resolution bandwidth (RBW) in Hz.

            SCPI: :SENSe:BANDwidth:RESolution?
            """
            return float(self.query(":SENSe:BANDwidth:RESolution?"))

        def set_vbw(self, vbw_hz: float, auto: bool = False):
            """
            Set video bandwidth (VBW) in Hz.

            SCPI:
                Auto on/off: :SENSe:BANDwidth:VIDeo:AUTO ON|OFF
                Value:       :SENSe:BANDwidth:VIDeo <vbw>
            """
            if auto:
                self.write(":SENSe:BANDwidth:VIDeo:AUTO ON")
            else:
                self.write(":SENSe:BANDwidth:VIDeo:AUTO OFF")
                self.write(f":SENSe:BANDwidth:VIDeo {vbw_hz}")

        def get_vbw(self) -> float:
            """
            Query video bandwidth (VBW) in Hz.

            SCPI: :SENSe:BANDwidth:VIDeo?
            """
            return float(self.query(":SENSe:BANDwidth:VIDeo?"))

        def set_vbw_rbw_ratio(self, ratio: float):
            """
            Set the VBW/RBW ratio.

            SCPI: :SENSe:BANDwidth:VIDeo:RATio <ratio>

            Example: ratio = 0.1  -> VBW = 0.1 * RBW
            """
            self.write(f":SENSe:BANDwidth:VIDeo:RATio {ratio}")

        def get_vbw_rbw_ratio(self) -> float:
            """
            Query the VBW/RBW ratio.

            SCPI: :SENSe:BANDwidth:VIDeo:RATio?
            """
            return float(self.query(":SENSe:BANDwidth:VIDeo:RATio?"))

        # --- Detector type ---

        def set_detector(self, det_type: str = "POSitive"):
            """
            Set detector type for the active trace.

            SCPI: :SENSe:DETector:FUNCtion <type>

            Typical values (check your firmware/manual):
                POSitive, NEGative, SAMPle, AVERage, RMS, QPEak, etc.

            Default here is POSitive (pos peak).
            """
            self.write(f":SENSe:DETector:FUNCtion {det_type}")

        def get_detector(self) -> str:
            """
            Query detector type.

            SCPI: :SENSe:DETector:FUNCtion?
            """
            return self.query(":SENSe:DETector:FUNCtion?").strip()
        
        def get_sweep_time(self) -> float:
            """
            Return the current sweep time in seconds.

            SCPI: [:SENSe]:SWEep:TIME?
            """
            return float(self.query(":SENSe:SWEep:TIME?"))

        def wait_for_sweeps(self, n_sweeps: int = 1, margin: float = 0.1) -> None:
            """
            Sleep long enough for n_sweeps complete sweeps, with a safety margin.

            n_sweeps: how many sweeps you want to wait for
            margin:  extra fractional margin (0.1 = +10%)
            """
            t = self.get_sweep_time()  # seconds per sweep
            delay = max(0.0, n_sweeps * t * (1.0 + margin))
            time.sleep(delay)

        def auto_range(self):
            """
            Execute auto range.

            This adjusts amplitude-related parameters (ref level, RF attenuation, etc.)
            within the current span for easier observation of the signal.
            """
            self.write(":SENSe:POWer:ARANge")

        # inside class rigol_dsa815

        def set_continuous_sweep(self, enable: bool = True):
            """
            Enable/disable continuous sweep mode.

            True  -> continuous sweep (INIT:CONT ON)
            False -> single sweep mode (INIT:CONT OFF)
            """
            state = "ON" if enable else "OFF"
            self.write(f":INITiate:CONTinuous {state}")

        def trigger_single_sweep(self, wait: bool = True):
            """
            Trigger a single sweep. If wait=True, block until it’s complete
            using *OPC?.
            """
            # Assumes continuous sweep is OFF
            self.write(":INITiate:IMMediate")
            if wait:
                # *OPC? returns '1' when all preceding operations complete
                self.query("*OPC?")

        def set_ref_level(self, level_dbuV: float):
            self.write(f":DISPlay:WINDow:TRACe:Y:SCALe:RLEVel {level_dbuV}")

