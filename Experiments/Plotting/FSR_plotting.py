# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 13:38:17 2021

@author: Erik.Iverson
"""

import pyvisa
import instrument_strings
import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt

filename = 'junk'
results = pd.read_csv(filename)

