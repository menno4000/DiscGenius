import evaluator
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal


def plot_filter(b, a, name):
    freq, response = signal.freqz(b, a)
    response_in_db = 20 * np.log10(abs(response))
    # freq_in_hz = freq*evaluator.SAMPLE_RATE/(2*np.pi)
    freq_in_hz = np.linspace(0, 20000, len(response_in_db))

    plt.plot(freq_in_hz, response_in_db)
    plt.title(name)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Amplitude [dB]')
    plt.grid(which='both', axis='both')

    # limit boundaries of graph
    # plt.ylim(-20, 5)
    # if name == "Low Shelf Filter":
    #    plt.xlim(0.01, 500)
    #    plt.axvline(200, color='green')
    # elif name == "High Shelf Filter":
    #    plt.xlim(500, 4000)
    #    plt.axvline(2000, color='green')

    plt.show()


def plot_audio_channel(audio_channel, name):
    time_axis = np.linspace(0, len(audio_channel) / evaluator.SAMPLE_RATE / 60, num=len(audio_channel))
    plt.figure()
    plt.plot(time_axis, audio_channel, color="blue")
    plt.ylabel('Audio Channel')
    plt.xlabel('Time (in mins)')
    plt.title(name)
    plt.show()


# todo
def plot_frequency_spectrum(spectrum):
    T = 1.0 / 800.0
    N = 600
    xf = np.linspace(0.0, 1.0 / (2.0 * T), N // 2)
    plt.plot(xf, 2.0 / N * np.abs(spectrum[0:N // 2]))
    plt.grid()
    plt.show()
