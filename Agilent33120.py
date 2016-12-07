import visa
import time
rm = visa.ResourceManager()
print(rm.list_resources())
func_gen = rm.open_resource('ASRL17::INSTR')
#func_gen.write("*CLS")

#func_gen.write("DISPlay:TEXT:CLEar")
#func_gen.write("SYSTEM:REMOTE")
#func_gen.read()
print(func_gen.query("*IDN?"))
print("version:")
print(func_gen.query("SYSTem:VERSion?"))
print("Output Load is set to: "+ func_gen.query("OUTPut:Load?")+" [ohms]")
freqs = ("100,", "200,", "500,", "1000,")
for freq in freqs:
	func_gen.write("APPL:SIN "+freq+ " 3.0, 0")
	time.sleep(1)
	
#func_gen.write("DISPlay:TEXT 'Goodbye'")
func_gen.query("SYSTem:ERRor?")
rm.close()
