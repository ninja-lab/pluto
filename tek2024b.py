import visa
rm = visa.ResourceManager()
tek = rm.open_resource(rm.list_resources()[2])
def setup_measurements():
    #5 measurements can be taken,
    # from 4 different channels + math
    #change to suit needs:
    tek.write('MEASU:MEAS1:SOUrce CH1')
    tek.write('MEASU:MEAS1:TYPe PK2pk')
    tek.write('MEASU:MEAS2:SOUrce CH2')
    tek.write('MEASU:MEAS2:TYPe FREQ')
    tek.write('MEASU:MEAS3:SOUrce CH3')
    tek.write('MEASU:MEAS3:TYPe PERIod')
    tek.write('MEASU:MEAS4:SOUrce CH4')
    tek.write('MEASU:MEAS4:typ maxi')
    
    

def measure(meas_num):
    #set vertical scale
    
    #use measure command
    tek.query('MEASU:MEAS'+str(meas_num)+':VALue?')
    #check if successful:
    #FILL ME IN
    #set cursors using max and min measurement
    tek.write(CURSor:HBArs)
    tek.write(CURSor:HBArs:POSITION1
    
setup_measurements()

def set_horizontal(freq):
    #freq must be number
    #sets scale to be 2 divisions / period
    tek.write('HORizontal:MAin:SCAle ' + str(.5/freq))

set_horizontal(1000)

def zero_pos():
    #center everything vertically and horizontally
    
