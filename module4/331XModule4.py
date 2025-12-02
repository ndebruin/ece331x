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
center_freq = 915.0e6 #Hz
sample_rate= 2e6 #Msps
rf_bandwidth = 1e6 #Hz
rf_gain = 30.0 #dB
capture_duration_sec = 0.05 # copy samples over in this blocks of this amount of time
capture_duration_total = 30.0 # total time to capture over
num_samps=int(capture_duration_sec*sample_rate) #If duration of DTS(T) = N/fs then T*Fs = N
num_buffers = int(capture_duration_total/capture_duration_sec)

# signal_threshold = int(50) # magnitude


# print((num_buffers*num_samps))
############################################################################## SDR OBJECT CREATION ###########################################################################################################

# create and configure actual radio object
plutoConnected = True

try:
    sdr = adi.Pluto("ip:192.168.2.1") #class in adi.ad936x device
    sdr.sample_rate= int(sample_rate) #
    sdr.rx_lo = int(center_freq) # carrier freq of Rx
    sdr.gain_control_mode_chan0 = "manual" # disable AGC, which is desirable when dealing with a non-constant signal
    sdr.rx_hardwaregain_chan0 = rf_gain
    sdr.rx_rf_bandwidth=int(rf_bandwidth)
    sdr.rx_buffer_size = num_samps # number of samples returned
except:
    print("No Pluto found, playing back data")
    plutoConnected = False
    



############################################################################## NUMPY FILE-BACKED ARRAY CREATION ###########################################################################################################

# create a file-backed numpy array for storing all raw samples for use at a later time.
# this is acceptable performance-wise, as all processing happens on the current buffer when it initally comes in
# this was written with the assistance of a ChatGPT agent

# create a filename with the current datetime

if plutoConnected:
    filename = "sample-capture_" + datetime.now().strftime("%Y-%m-%d_%H-%M") + ".bin"
    all_samples = np.memmap(filename, dtype=np.complex64, mode='w+', shape=(num_buffers*num_samps))
else:
    filename = input("Please enter the path to a filename to playback: ")
    print(filename)
    all_samples = np.memmap(filename, dtype=np.complex64, mode='r', shape=(num_buffers*num_samps))

# create our actual file-backed numpy array

# register a ctrl-c listener so that we can safely finalize the file on program exit
running = True
def handle_exit(sig, frame):
    global running
    print("\nStopping Capture...")
    running = False
signal.signal(signal.SIGINT, handle_exit)


############################################################################## DISPLAY CONFIGURATION #######################################################################################################################################


fft_bin_size_freq = 20
fft_size = sample_rate/fft_bin_size_freq

# create a spectrogram object from our other file
spectrogram_raw = RealtimeSpectrogram(
    sample_freq = sample_rate,
    samples_per_fft_slice = int(fft_size),
    center_freq = center_freq,
    title = "Raw Spectrogram"
)

# spectrogram_corrected = RealtimeSpectrogram(
#     sample_freq = sample_rate,
#     samples_per_fft_slice = int(fft_size),
#     center_freq = center_freq,
#     title = "Corrected Spectrogram"
# )

max_points = int(5e4)

# # create a IQ scatter plot object from other file
# iq_plot_raw = IQPlot(
#     max_points = max_points,
#     title="Raw IQ Plot"
# )

# # create the magnitude/phase plots object from the other file
# mag_phase_plot_raw = MagPhasePlot(
#     sample_freq = sample_rate,
#     max_points = max_points,
#     title="Raw Mag-Phase Plot"
# )

# # create a IQ scatter plot object from other file
# iq_plot_corrected = IQPlot(
#     max_points = max_points,
#     title="Corrected IQ Plot"
# )

# # create the magnitude/phase plots object from the other file
# mag_phase_plot_corrected = MagPhasePlot(
#     sample_freq = sample_rate,
#     max_points = max_points,
#     title="Corrected Mag-Phase Plot"
# )

def updateGraphs(buffer):
    # print(buffer)
            
    # update our raw plots
    # iq_plot_raw.update(buffer)
    # mag_phase_plot_raw.update(buffer)
    spectrogram_raw.update(buffer)
    
    N = len(buffer)
            
    # determine coarse frequency correction offset from finding the max power sample in an FFT
    # buffer_fft = np.fft.fftshift(np.fft.fft(buffer))
    # frequencies = np.fft.fftshift(np.fft.fftfreq(N, 1/sample_rate))
    # peak_power_frequency_index = np.argmax(np.abs(buffer_fft))
    # coarse_frequency_offset = frequencies[peak_power_frequency_index]
    
    # print(coarse_frequency_offset)
    # # print(N)
    
    # # apply our coarse correction
    # # create time vector
    # t = np.arange(N)/int(sample_rate)
    # correction_sinusoid = np.exp(-1j * 2 * np.pi * coarse_frequency_offset *t)
    # buffer_corrected = buffer * correction_sinusoid
    
    # # update our corrected plots
    # iq_plot_corrected.update(buffer_corrected)
    # mag_phase_plot_corrected.update(buffer_corrected)
    # spectrogram_corrected.update(buffer_corrected)

    # flush this buffer of samples to our file before grabbing a new buffer

########################################## start of buffer iterator
capture = False
current_buffer_num = 0 # which buffer of capture are we on?
try:
    # iterate as long as we can
    while running and current_buffer_num < num_buffers:
        current_buffer_num = current_buffer_num + 1
        
        print(f'{round(100.0*current_buffer_num/num_buffers,2)}%',)
        
############################################################################## BUFFER ITERATOR #############################################################################################################################
        current_samples = 0
        if plutoConnected:
            current_samples = sdr.rx() # get a single buffer of samples
        else:
            current_samples = all_samples[current_buffer_num*num_samps:(current_buffer_num+1)*num_samps]
            
        # print(current_samples)
        
        # flush to file
        if plutoConnected:
            all_samples[current_buffer_num*num_samps:(current_buffer_num+1)*num_samps] = current_samples
            all_samples.flush()
        
        
        # if any sample in the buffer is above our magnitude threshold, then let's record and display that buffer
        # if np.any(np.abs(current_samples) > signal_threshold):
            # capture = True
        else:
            updateGraphs(buffer=current_samples)
            
    
        
        # capture an additional buffer after the signal ends to get a trailing edge
        # elif(capture):
            # capture = False
            
            # update(storage=all_samples, buffer=current_samples)





############################################################################## PROGRAM CLOSE #############################################################################################################################
# written by ChatGPT from the same result as the above code for the file-backed array
finally:
    all_samples.flush()
    del all_samples # safely closes file
    if plutoConnected:
        sdr.rx_destroy_buffer() # clear SDR buffer
    print("File Closed. Exiting...")
