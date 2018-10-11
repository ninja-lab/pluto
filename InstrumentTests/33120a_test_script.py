import visa
import time
import serialInstrument
import Agilent33120

rm = visa.ResourceManager()
print(rm.list_resources())

func_gen = Agilent33120.f33120a(rm.list_resources()[3], rm)
print(func_gen.getName())
print("version:")
print(func_gen.query("SYSTem:VERSion?"))
#print(func_gen.selfTest())
func_gen.displayText("'Hi Erik'")

freqs = [1, 2, 5, 10, 20, 50]
func_gen.applyFunction('SIN', 1, 2, 0)

for freq in freqs:
    func_gen.outputFreq(freq)
    time.sleep(3)

















