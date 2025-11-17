import plotting
'''
def generate_bode_plot(mag1, mag2, phase, freqs, quantity):
    
    Generates a plot with left vertical axis as magnitude, right vertical as phase,
    along log frequency horizontal axis. 
    
    save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
    fig, ax1 = plt.subplots()
    ax1.set_ylim(min(mag1) - 20, max(mag1) + 20)
    ax1.semilogx(freqs, mag1, 'gs', freqs, mag2, 'bs')
    mag3 = [15, 15, 15, 15]
    ax1.semilogx(freqs, mag3, 'ys')
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Magnitude [dB]', color = 'b')
    ax1.legend(['scope measured', 'cursor measured'])
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.set_ylim(-360, 360)
    ax2.semilogx(freqs, phase, 'r--')
    ax2.set_ylabel('Phase [deg]', color = 'r')
    ax2.legend(['phase'], loc=4)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
    name = quantity + ' FreqResp ' + time_stamp
    print(name)
    plt.title(name)
    fig = plt.gcf()
    plt.show()
    filename = (save_loc + name + '.png').replace(' ','_')
    print(filename)
    fig.savefig(filename)
  '''  
mag1 = [20, 20, 20, 20]
mag2 = [10, 10, 10, 10]
mag3 = [15, 15, 15, 15]
phase = [0, 0, 0, 0]
freqs = [1, 2, 5, 10]

#plotting.generate_bode_plot([mag1, mag2, mag3], phase, freqs, ['mag1', 'mag2', 'mag3'], 'test_plot')
L1 = [.1, .1, .12, .13, .15]
L2 = [.09, .1, .14, .15, .16]
plotting.generate_inductance_plot([L1, L2], [1, 2, 5, 10, 20], ['L1', 'L2'], 'inductances vs freq')
