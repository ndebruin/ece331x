# derived from the RealtimeSpectrogram file

import numpy as np
import matplotlib.pyplot as plt

class IQPlot:
    def __init__(self, max_points=5000):

        self.max_points = max_points

        # Create figure and axes
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("IQ Plot")
        self.ax.set_xlabel("I")
        self.ax.set_ylabel("Q")
        self.ax.grid(True, alpha=0.3)

        # Pre-allocate data arrays
        self.i_data = np.zeros(max_points)
        self.q_data = np.zeros(max_points)

        # Create scatter object to be updated
        self.scatter = self.ax.scatter(self.i_data, self.q_data, s=2, color='royalblue')

        plt.tight_layout()
        plt.ion()
        plt.show(block=False)

    def update(self, samples):
        samples = np.asarray(samples)
        i_new = np.real(samples)
        q_new = np.imag(samples)

        # Keep only the most recent N samples
        n = len(i_new)
        if n >= self.max_points:
            self.i_data = i_new[-self.max_points:]
            self.q_data = q_new[-self.max_points:]
        else:
            self.i_data = np.roll(self.i_data, -n)
            self.q_data = np.roll(self.q_data, -n)
            self.i_data[-n:] = i_new
            self.q_data[-n:] = q_new

        # Update scatter plot data
        self.scatter.set_offsets(np.column_stack((self.i_data, self.q_data)))
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
