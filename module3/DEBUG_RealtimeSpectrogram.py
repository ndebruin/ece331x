# written with the assistance of ChatGPT
# prompt: Can you help me to update this static spectrogram function that uses matplotlib to one that updates in realtime as I feed new buffers of samples to an update function? *Paste spectrogram function from Module 1*

import numpy as np
import matplotlib.pyplot as plt

class RealtimeSpectrogram:
    def __init__(self, sample_freq, samples_per_fft_slice, center_freq, history_seconds=5):
        """
        Initialize a real-time spectrogram plot.

        Parameters
        ----------
        sample_freq : float
            Sampling frequency in Hz.
        samples_per_fft_slice : int
            Number of samples per FFT window.
        center_freq : float
            Center frequency in Hz.
        history_secs : float
            Total time span to display on the x-axis.
        """
        self.sample_freq = sample_freq
        self.samples_per_fft_slice = samples_per_fft_slice
        self.center_freq = center_freq
        self.history_secs = history_seconds

        # Derived quantities
        self.n_time_bins = int(self.history_secs * sample_freq / samples_per_fft_slice)

        # Setup matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Spectrogram")
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Frequency [MHz]")

        # Pre-fill spectrogram with functionally "empty" data so it has something to display
        self.freqs = np.fft.fftfreq(samples_per_fft_slice, 1/sample_freq)
        self.freqs = np.fft.fftshift(self.freqs) / 1e6 + center_freq / 1e6
        self.data = np.full((len(self.freqs), self.n_time_bins), -100.0)  # dB values

        # create actual figure
        self.img = self.ax.imshow(
            self.data,
            extent=[0, self.history_secs, self.freqs[0], self.freqs[-1]],
            aspect='auto',
            origin='lower',
            cmap='viridis',
            vmin=-120,
            vmax=0,
        )
        self.cbar = plt.colorbar(self.img, ax=self.ax)
        self.cbar.set_label("Power [dB]")
        plt.tight_layout()
        plt.ion()
        plt.show(block=False)

    def update(self, samples):
        num_slices=len(samples)//self.samples_per_fft_slice #samples/(samples/num_slices)

        if num_slices == 0:
            return

        for i in range(num_slices):
            sample_slice=samples[i*self.samples_per_fft_slice:(i+1)*self.samples_per_fft_slice] #i= slice number multiplies by fft size to isolate FFT size samples ex: a 1024 point FFT needs exactly 1024 samples any more and rest of data is thrown away!
            fft_data = np.fft.fftshift(np.fft.fft(sample_slice))/self.samples_per_fft_slice #Kept this line same only divided by samples_per_fft to normalize values 
            power_db=20*np.log10(np.abs(fft_data)+1e-6) #This line exact same 
            self.data = np.roll(self.data, -1, axis=1)
            self.data[:, -1] = power_db
      
       

        # Update the image
        self.img.set_data(self.data)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()


########################################################SIMULATION########################################################################################
if __name__ == "__main__": #This entire section was written with the help of ChatGPT!
    SAMPLE_FREQ= 1e6
    FFT_SIZE=1024
    CENTER_FREQ=100e6

    spec=RealtimeSpectrogram(SAMPLE_FREQ,FFT_SIZE,CENTER_FREQ)
    N_SLICES=100

    print("Starting simulation.... Press CTRL+C to stop")

    try:
        for i in range(1000):
            batch_samples_t=np.arange(N_SLICES*FFT_SIZE)/SAMPLE_FREQ
            f_offset=200e3*np.sin(2*np.pi*(i*N_SLICES)/500)
            signal= 0.5*np.exp(1j*2*np.pi*f_offset*batch_samples_t)
            noise=0.1*(np.random.randn(N_SLICES*FFT_SIZE)+1j*np.random.randn(N_SLICES*FFT_SIZE))
            samples= signal+noise
            spec.update(samples)
            plt.pause(0.01)

    except KeyboardInterrupt: 
        print("Simulation stopped.")

    print("Simulation finished. Close the plot window to exit.")
    plt.ioff() # Turn off interactive mode
    plt.show()



        
        





