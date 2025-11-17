# written with the assistance of ChatGPT
# prompt: Can you help me to update this static spectrogram function that uses matplotlib to one that updates in realtime as I feed new buffers of samples to an update function? *Paste spectrogram function from Module 1*

import numpy as np
import matplotlib.pyplot as plt

class RealtimeSpectrogram:
    def __init__(self, sample_freq, samples_per_fft_slice, center_freq, history_seconds=5, title=""):
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
        
        self.fig.suptitle = title

        # Pre-fill spectrogram with functionally "empty" data so it has something to display
        self.freqs = np.fft.fftfreq(samples_per_fft_slice, 1/sample_freq)
        self.freqs = np.fft.fftshift(self.freqs) / 1e6 + center_freq / 1e6
        self.data = np.full((len(self.freqs), self.n_time_bins), -120.0)  # dB values

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
        """Call this with a new buffer of samples."""
        # Compute power spectrum (in dB)
        fft_data = np.fft.fftshift(np.fft.fft(samples, 8192))
        power_db = 20 * np.log10(np.abs(fft_data) + 1e-6)

        # Shift existing data left and append new column
        self.data = np.roll(self.data, -1, axis=1)
        self.data[:, -1] = power_db

        # Update the image
        self.img.set_data(self.data)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()