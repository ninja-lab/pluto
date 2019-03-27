# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 13:26:01 2019

@author: Erik
"""

import time
from PWRTestIO import *
import numpy as np
from pwr_board_test_class import quantity
import pandas as pd
from datetime import datetime
import pyvisa
from InstrumentConnections import InstrumentConnections
class SelfTester():

    
    def __init__(self, myResources):
        super().__init__()
        self.myResources = myResources
        self.myResources.Connect()
        self.daq = self.myResources.get_daq()
        load1_off(self.daq)
        load2_off(self.daq)
        load3_off(self.daq)
        
        self.lv_supply = self.myResources.get_lv_supply()
        self.lv_supply.set_output_mode(0)
        self.lv_supply.set_rising_voltage_slew('MAX')
        
        self.hv_supply = self.myResources.get_hv_supply()
        self.hv_supply.set_output_mode(0)
        self.mystr = 'Test {}: Readback: {:.2f}, Input: {:.2f}, Result: {}'
        self.quantity_df = pd.read_excel('C:\\Users\\Erik\\git\\pluto\\PWRAutomatedTest\\385-0030-TestSet\\PWR_Board_TestReportTemplate2.xlsx', 'Quantities')          
        self.testInfo = None
        self.quantities = {}
        for row in self.quantity_df.iterrows():
            ser = row[1] #(index, Series) comes from iterrows()
            column_names = ser.index.tolist()
            my_dict = {}
            for column_name in column_names:
                my_dict[column_name] = ser[column_name]
            new_quantity = quantity(my_dict)
            self.quantities[new_quantity.getStringName()] = new_quantity

    def checkPSUAm(self):
        '''
        Feed the 80V instek to PSUAm with SelfTest Cable __
        Adjust a few times and verify the readback matches
        '''
        close_rl5(self.daq)
        time.sleep(1)
        self.lv_supply.apply(0,1)
        self.lv_supply.set_output('ON')
        for voltage in np.arange(5,30,5,dtype=float):
            self.lv_supply.apply(voltage, 5)
            time.sleep(1)
            readback = self.quantities['PSUA'].measure(self.daq) 
            stimulus = self.lv_supply.get_voltage()
            result = .99*readback < stimulus < 1.01*readback
            print(self.mystr.format(1, readback, stimulus, result ))
        self.lv_supply.apply(0,.2)
        return 
    
    def checkPSUBm(self):
        '''
        Feed the 80V instek to PSUAm with SelfTest Cable __
        Adjust a few times and verify the readback matches
        '''
        open_rl5(self.daq)
        self.lv_supply.apply(0,1)
        self.lv_supply.set_output('ON')
        for voltage in np.arange(5,30,5,dtype=float):
            self.lv_supply.apply(voltage, 5)
            time.sleep(1)
            readback = self.quantities['PSUB'].measure(self.daq) 
            stimulus = self.lv_supply.get_voltage()
            result = .99*readback < stimulus < 1.01*readback
            print(self.mystr.format(2, readback, stimulus, result ))
        self.lv_supply.apply(0,.2)
        self.lv_supply.set_output('OFF')
        return
    
    def checkTP5B(self):
        '''
        Output HV supply to PBUS/NBUS 
        '''
        close_rl1(self.daq)
        open_rl2(self.daq)
        self.hv_supply.apply(0, .2)
        self.hv_supply.set_output('ON')
        for voltage in np.arange(50,300,50,dtype=float):
            self.hv_supply.apply(voltage, 1)
            time.sleep(3)
            readback = self.quantities['TP5B'].measure(self.daq) 
            stimulus = self.hv_supply.get_voltage()
            result = .99*readback < stimulus < 1.01*readback
            print(self.mystr.format(3, readback, stimulus, result ))
        self.hv_supply.apply(0,.2)
        self.hv_supply.set_output('OFF')
        return
            
    def checkTP1B(self):
        '''
        Output HV supply to PBUS/NBUS 
        '''
        close_rl1(self.daq)
        close_rl2(self.daq)
        self.hv_supply.apply(0, .2)
        self.hv_supply.set_output('ON')
        for voltage in np.arange(50,300,50,dtype=float):
            print('programmed: {}'.format(voltage))
            self.hv_supply.apply(voltage, 1)
            time.sleep(2)
            readback = self.quantities['TP1B'].measure(self.daq) 
            stimulus = self.hv_supply.get_voltage()
            result = .99*readback < stimulus < 1.01*readback
            print(self.mystr.format(3, readback, stimulus, result ))
        self.hv_supply.apply(0,.2)
        self.hv_supply.set_output('OFF')
        return        

    def checkHVCAP(self):
        '''
        Output HV supply to PBUS/NBUS 
        '''
        open_rl1(self.daq)
        open_rl2(self.daq)
        close_rl3(self.daq)
        close_rl4(self.daq)
        self.hv_supply.apply(0, 1)
        self.hv_supply.set_output('ON')
        for voltage in np.arange(50,300,50,dtype=float):
            self.hv_supply.apply(voltage, .2)
            time.sleep(1)
            readback = self.quantities['HVCAP'].measure(self.daq) 
            stimulus = self.hv_supply.get_voltage()
            result = .99*readback < stimulus < 1.01*readback
            print(self.mystr.format(4, readback, stimulus, result ))
        self.hv_supply.apply(0,.2)
        self.hv_supply.set_output('OFF')
        return

    def exercise_relays(self):
        
        for i in range(5):
            close_rl1(self.daq)
            time.sleep(.2)
            close_rl2(self.daq)
            time.sleep(.2)
            close_rl3(self.daq)
            time.sleep(.2)
            close_rl4(self.daq)
            time.sleep(.2)
            close_rl5(self.daq)
            time.sleep(2)
            open_rl1(self.daq)
            time.sleep(.2)
            open_rl2(self.daq)
            time.sleep(.2)
            open_rl3(self.daq)
            time.sleep(.2)
            open_rl4(self.daq)
            time.sleep(.2)
            open_rl5(self.daq)
            time.sleep(2)
        return 
    
    def testLoads(self):
        load1_off(self.daq)
        load2_off(self.daq)
        load3_off(self.daq)
        load = self.daq.measure_Resistance(self.quantities['24Vout'].getChannel())
        result = load > 1e6
        print(self.mystr.format(5, load, 1e9, result))
        
        load1_on(self.daq)
        load = self.daq.measure_Resistance(self.quantities['24Vout'].getChannel())
        result = .9*10 < load < 1.1*10
        print(self.mystr.format(5, load, 10, result))
        load1_off(self.daq)
        
        load2_on(self.daq)
        load = self.daq.measure_Resistance(self.quantities['24Vout'].getChannel())
        result = .9*10 < load < 1.1*10
        print(self.mystr.format(5, load, 10, result))
        load2_off(self.daq)
        
        load3_on(self.daq)
        load = self.daq.measure_Resistance(self.quantities['24Vout'].getChannel())
        result = .9*10 < load < 1.1*10
        print(self.mystr.format(5, load, 10, result))
        load3_off(self.daq)
        
        return
    def testRibbon(self):
        buck_off(self.daq)
        time.sleep(1)
        readback = self.quantities['PSU_FLT'].measure(self.daq)
        result = readback < .2
        print(self.mystr.format(6, readback, 0, result))
        
        buck_on(self.daq)
        time.sleep(1)
        readback = self.quantities['PSU_FLT'].measure(self.daq)
        result = readback > 4
        print(self.mystr.format(6, readback, 5, result))
        
        flyback_off(self.daq)
        time.sleep(1)
        readback = self.quantities['SPM'].measure(self.daq)
        result = readback > 4
        print(self.mystr.format(7, readback, 5, result))
        
        flyback_on(self.daq)
        time.sleep(1)
        readback = self.quantities['SPM'].measure(self.daq)
        result = readback < .2
        print(self.mystr.format(7, readback, 0, result))
        
        readback = self.quantities['FLT_OUT'].measure(self.daq)
        result = 3.8 < readback < 4.2
        print(self.mystr.format(8, readback, 4, result))
        
        
selfTester = SelfTester(InstrumentConnections(pyvisa.ResourceManager()))
#selfTester.checkPSUAm()
#selfTester.checkPSUBm()
#selfTester.checkTP1B()
#selfTester.checkTP5B()
#selfTester.checkHVCAP()
#selfTester.testLoads()
selfTester.testRibbon()