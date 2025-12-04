import numpy as np
from numpy.fft import fft, fftshift
import matplotlib.pyplot as plt


#-----------------------------------------------------------------------------------------

def plotme(thing, name = "", show_grid = False, show_pips = False):
	#return # use as global plotting disable
	plt.plot(thing)
	if show_pips: plt.plot(thing, "bo")
	plt.title(name)
	if show_grid: plt.grid()
	plt.show()


#-----------------------------------------------------------------------------------------

# len(x) needs to be larger than fft_size
def spectrogram(x, rx_center, rx_sample_rate):
	# fft_size and row_offset must be powers of two, and row offset should be no larger than fft_size
	fft_size = 2**10
	row_offset = 2**5 # added to make the spectrogram smoother
	num_rows = int(np.floor(row_offset*len(x)/fft_size))-row_offset # fixes overrunning the end of the data array
	spectrogram = np.zeros((num_rows, fft_size))
	for i in range(num_rows):
		start_idx = i*fft_size//row_offset
		stop_idx = start_idx + fft_size
		spectrogram[i,:] = 10*np.log10(np.abs(fftshift(fft(x[start_idx:stop_idx])))**2)
	
	plt.imshow(spectrogram[::-1], aspect='auto', extent = [(rx_center-rx_sample_rate/2)/1e6, (rx_center+rx_sample_rate/2)/1e6, 0, len(x)/rx_sample_rate])
	plt.xlabel("Frequency [MHz]")
	plt.ylabel("Time [s]")
	plt.show()


#-----------------------------------------------------------------------------------------
