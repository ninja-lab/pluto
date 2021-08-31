legend_strs, 'Offloader I-V Relationship'mag1 = for idc in dc_levels:       
  
[20range(2)lidc = 
def generate_bode_plot(mags, phases, freqs, legend_strs, title_str):
    '''
    Generates a plot with left vertical axis as magnitude, right vertical as phase,
    along log frequency horizontal axis. 
    '''
    save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
    fig, ax1 = plt.subplots()
    ax1.set_ylim(min(mags[0]) - 20, max(mags[0]) + 20)
    colored_squares = ['g.', 'b.', 'r.', 'k.', 'c']
    i = 0
    for mag in mags:
        ax1.semilogx(freqs, mag, colored_squares[i])
        i = i + 1
    
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Magnitude [dB]', color = 'b')
    ax1.legend(legend_strs)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.set_ylim(-360, 90)
    ax2.semilogx(freqs, phases, 'r--')
    ax2.set_ylabel('Phase [deg]', color = 'r')
    ax2.legend(['phase'], loc=4)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
    name = title_str + time_stamp
    print(name)
    plt.title(name)
    fig = plt.gcf()
    plt.show()
    filename = (save_loc + name + '.png').replace(' ','_')
    print(filename)
    fig.savefig(fileMEANidc_levels.append( age_mag[n]/tp16[n]) for n in rang)
     meane(0, len(freqs)]
dc_ldc_
     
         input('adjust DC current command for new valuejunk = ')
mag2 = [20*log10(man[nman]/)]import plottiplotting.
magss.3'], 'test_plot'[n]p for n in range(0, len(freqs)lo
mag3 = [20*log10(vol[n]/manual[n]) for n in range(0, len(freqs)]t
mag4 = [20*log10(man[n]/curr[n]) for n in range(0, len(freqs)]t
mag5 = [20*log10(voltage[n]/current_mag[n]) for n in range(0, len(freqs)]i
legend_strs = ['ch2/tp16', 'manual V / manual I', 'ch2/manual I', 'manual V / ch4', 'ch2/ch4']mag3 = [15, [mag1, mag2, mag3],port plotting]impor
def generate_bode_plot(mags, phases, freqs, legend_strs, title_str):
    '''
    Generates a plot with left vertical axis as magnitude, right vertical as phase,
    al
    
    ng log frequency horizontal axis. 
    '''
    save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
    fig, ax1 = plt.subplots()
    ax1.set_ylim(min(mags[0]) - 20, max(mags[0]) + 20)
    colored_squares = ['g.', 'b.', 'r.', 'k.', 'c']
 ]   i = 0
    for ]mag in mags:
        ax1.semilog]x(freqs, mag, colore)d_squares[i])
        i = i + 1
    
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_]y]legend_sttitle_str e [dB]', color = 'b')
    ax1.legendend_strs)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
)
    ax2 = ax1.twinx()
    ax2.set_ylim(-360, 90)
    ax2.semilogx(--')
    ax2.set_ylabel('Phase [deg]', color = 'r')
    ax2.legend(['phase'], loc=4)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
    name = title_str + time_stamp
    print(name)
    plt.title(name)
    fig = plt.gcf()
    plt.show()
    filename = (save_loc + name + '.png').replace(' ','_')
    print(filename)
    fig.savefsef genesrate_bodetitle_sts[for m-%d_%H_%Max1.semilogx(freqs, mag, 
    colored_squares = ['gs', 'bs'. 'rs'. ])
 .  'k.', 'c'

i = col]ored_s]quares[]i] 0 0]gs, phases, fres[0]s, legend_strs, title_str):
    '''
    Generates a plot with left vertical axis as magnitude, right vertical as phase,
    along log frequency horizontal axis. 
    '''
    save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
    fig, ax1 = plt.subplots()
    ax1.set_ylim(min(mags[0]) - 20, max(mags[0]) + 20)
    colored_squares = ['g.', 'b.', 'r.', 'k.', 'c']
    i = 0
    for mag in mags:
        ax1.semilogx(freqs, mag, colored_squares[i])
        i = i + 1
    
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Magnitude [dB]', color = 'b')
    ax1.legend(legend_strs)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.set_ylim(-360, 90)
    ax2.semilogx(freqs, phases, 'r--')
    ax2.set_ylabel('Phase [deg]', color = 'r')
    ax2.legend(['phase'], loc=4)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
    name = title_str + time_stamp
    print(name)
    plt.title(name))
    fig = plt.gcf()
    plt.show()
    filename = (save_loc + name + '.png').replace(' ','_')
    print(filename)
    fig.savefig(filename)
    
    
    
    import matplotl)ib as plt
    
    
    