import matplotlib.pyplot as plt
from datetime import datetime


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
    fig.savefig(filename)
    
def generate_inductance_plot(mags, freqs, legend_strs, title_str):
    '''
    Generates a plot with left vertical axis as magnitude, right vertical as phase,
    along log frequency horizontal axis. 
    '''
    save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
    fig, ax1 = plt.subplots()
    #ax1.set_ylim(min(mags[0]) max(mags[0]))
    colored_dashes = ['g--', 'b--', 'r--', 'k--', 'c--']
    i = 0
    for mag in mags:
        ax1.semilogx(freqs, mag, colored_dashes[i])
        i = i + 1
    
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Inductance [H]', color = 'b')
    ax1.legend(legend_strs)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
    name = title_str + time_stamp
    print(name)
    plt.title(name)
    fig = plt.gcf()
    plt.show()
    filename = (save_loc + name + '.png').replace(' ','_')
    print(filename)
    fig.savefig(filename)