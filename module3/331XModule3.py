############################################################################## IMPORTS ###########################################################################################################
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import iio
import adi 
from datetime import datetime
import signal
from RealtimeSpectrogram import RealtimeSpectrogram
from IQPlot import IQPlot
from MagPhasePlot import MagPhasePlot

############################################################################## RADIO CONFIGURATION ###########################################################################################################

# define radio configuration
center_freq = 433.935e6 #Hz
sample_rate= 2e6 #Msps
rf_bandwidth = 1e4 #Hz
rf_gain = 60.0 #dB
capture_duration_sec = 0.1 # copy samples over in this blocks of this amount of time
capture_duration_total = 60.0 # total time to capture over
num_samps=int(capture_duration_sec*sample_rate) #If duration of DTS(T) = N/fs then T*Fs = N
num_buffers = int(capture_duration_total/capture_duration_sec)

signal_threshold = int(250) # magnitude

############################################################################## SDR OBJECT CREATION ###########################################################################################################

# create and configure actual radio object
sdr = adi.Pluto("ip:192.168.2.1") #class in adi.ad936x device
sdr.sample_rate= int(sample_rate) #
sdr.rx_lo = int(center_freq) # carrier freq of Rx
sdr.gain_control_mode_chan0 = "manual" # disable AGC, which is desirable when dealing with a non-constant signal
sdr.rx_hardwaregain_chan0 = rf_gain
sdr.rx_rf_bandwidth=int(rf_bandwidth)
sdr.rx_buffer_size = num_samps # number of samples returned

############################################################################## NUMPY FILE-BACKED ARRAY CREATION ###########################################################################################################

# create a file-backed numpy array for storing all raw samples for use at a later time.
# this is acceptable performance-wise, as all processing happens on the current buffer when it initally comes in
# this was written with the assistance of a ChatGPT agent

# create a filename with the current datetime
filename = "sample-capture_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%s") + ".bin"

# create our actual file-backed numpy array
all_samples = np.memmap(filename, dtype=np.complex64, mode='w+', shape=(num_buffers*num_samps))

# register a ctrl-c listener so that we can safely finalize the file on program exit
running = True
def handle_exit(sig, frame):
    global running
    print("\nStopping Capture...")
    running = False
signal.signal(signal.SIGINT, handle_exit)


############################################################################## DISPLAY CONFIGURATION #######################################################################################################################################

# create a spectrogram object from our other file
# spectrogram = RealtimeSpectrogram(
#     sample_freq = sample_rate,
#     samples_per_fft_slice = int(2**13),
#     center_freq = center_freq
# )

max_points = int(100000)

# create a IQ scatter plot object from other file
iq_plot_raw = IQPlot(
    max_points = max_points
)

# create the magnitude/phase plots object from the other file
mag_phase_plot_raw = MagPhasePlot(
    sample_freq = sample_rate,
    max_points = max_points
)

# create a IQ scatter plot object from other file
iq_plot_corrected = IQPlot(
    max_points = max_points
)

# create the magnitude/phase plots object from the other file
mag_phase_plot_corrected = MagPhasePlot(
    sample_freq = sample_rate,
    max_points = max_points
)

def update(storage, buffer):
    # print(buffer)
    
    # update our spectrogram
    # spectrogram.update(buffer)
            
    # update our raw plots
    iq_plot_raw.update(buffer)
    mag_phase_plot_raw.update(buffer)
            
    # determine coarse frequency correction offset from finding the max power sample in an FFT
    buffer_fft = np.fft.fftshift(np.fft.fft(buffer))
    frequencies = np.fft.fftshift(np.fft.fftfreq(len(buffer), 1/int(sample_rate)))
    peak_power_frequency_index = np.argmax(np.abs(buffer_fft))
    coarse_frequency_offset = frequencies[peak_power_frequency_index]
    
    print(coarse_frequency_offset)
    
    # apply our coarse correction
    correction_sinusoid = np.exp(-1j * 2 * np.pi * coarse_frequency_offset * (np.arange(len(buffer))*2))
    buffer_corrected = buffer * correction_sinusoid
    
    # update our corrected plots
    iq_plot_corrected.update(buffer_corrected)
    mag_phase_plot_corrected.update(buffer_corrected)

    # flush this buffer of samples to our file before grabbing a new buffer
    storage = np.concatenate((storage, buffer))


########################################## start of buffer iterator
capture = False
current_buffer_num = 0 # which buffer of capture are we on?
try:
    # iterate as long as we can
    while running and current_buffer_num < num_buffers:
        num_buffers = num_buffers + 1
        
############################################################################## BUFFER ITERATOR #############################################################################################################################
        current_samples = sdr.rx() # get a single buffer of samples
          
        
        # if any sample in the buffer is above our magnitude threshold, then let's record and display that buffer
        if np.any(np.abs(current_samples) > signal_threshold):
            capture = True
            
            update(storage=all_samples, buffer=current_samples)
        
        # capture an additional buffer after the signal ends to get a trailing edge
        elif(capture):
            capture = False
            
            # update(storage=all_samples, buffer=current_samples)





############################################################################## PROGRAM CLOSE #############################################################################################################################
# written by ChatGPT from the same result as the above code for the file-backed array
finally:
    del all_samples # safely closes file
    sdr.rx_destroy_buffer() # clear SDR buffer
    print("File Closed. Exiting...")
