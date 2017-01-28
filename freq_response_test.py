import tek2024b
import Agilent33120
import pyvisa
import time
import matplotlib.pyplot as plt
from math import log10

rm = pyvisa.ResourceManager()
print(rm.list_resources())

func_gen = Agilent33120.f33120a(rm.list_resources()[3], rm)
func_gen.displayText("'Hi Erik'")
tek = tek2024b.tek2024(rm.list_resources()[2], rm)
ch1 = tek2024b.channel(tek, 1)
tek.setup_measurements()
ch1.set_Position(0)
ch1.set_vScale(.5)
tek.trigger('DC', 1, 'NORMal')
tek.set_averaging(False)
tek.setImmedMeas(1, "FREQ")
tek.setup_measurements()
freqs = [1, 2, 5, 10, 20, 50]
mag = [] #dB
phase = []
input_amplitude = 2 #pk2pk
func_gen.applyFunction('SIN', 1, 2, 0)
tek.acquisition(True)

for freq in freqs:
    func_gen.outputFreq(freq)
    print()
    print('Programmed Frequency is: ' + str(freq) + 'Hz')
    tek.set_hScale(frequency = freq, cycles = 4)
    tek.setImmedMeas(1, "PK2pk")
    time.sleep(tek.get_timeToCapture(freq, 4)[1])
    mag_value = tek.getImmedMeas()
    mag.append(20*log10(float(mag_value)/input_amplitude))
    phase.append(45)
    tek.setImmedMeas(1, "FREQ")
    time.sleep(.5)
    print('Frequency measured is: ' + tek.getImmedMeas())
    time.sleep(.5)

fig, ax1 = plt.subplots()
ax1.set_ylim(-20, 40)
ax1.plot(freqs, mag, 'b-')
#ax1.set_ylim(-20, 40)
ax1.set_xlabel('Frequency [Hz]')
ax1.set_ylabel('Magnitude [dB]', color = 'b')
for tl in ax1.get_yticklabels():
    tl.set_color('b')

ax2 = ax1.twinx()
ax2.set_ylim(0, 90)
ax2.plot(freqs, phase, 'r-')
ax2.set_ylabel('Phase [deg]', color = 'r')
for tl in ax2.get_yticklabels():
    tl.set_color('r')
plt.show()

'''
plt.semilogx(freqs, mag)
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude [dB]')
plt.ylim([-20, 40])
plt.title('Underwhelming Frequency Response Data')
plt.grid(True)
plt.savefig("test.png")
plt.show()

'''
