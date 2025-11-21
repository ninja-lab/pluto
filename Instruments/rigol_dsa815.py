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
            self.inst.timeout = 10000

            

