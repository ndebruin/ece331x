# derived from the RealtimeSpectrogram file

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class MagPhasePlot:
    def __init__(self, sample_freq, max_points=5000):

        self.sample_rate = sample_freq
        self.max_points = max_points
        
        # pre-fill data arrays with something so that it has something when the program starts
        self.mag_data = np.zeros(max_points)
        self.phase_data = np.zeros(max_points)
        
        self.time = np.arange(max_points) / self.sample_rate

        # create figure objects
        self.fig, (self.ax_mag, self.ax_phase) = plt.subplots(2,1)
        
        # Setup magnitude figure
        self.ax_mag.set_title("Magnitude over Time")
        self.ax_mag.set_xlabel("Time [s]")
        self.ax_mag.set_ylabel("Magnitude [|s(n)|]")
        self.line_mag = self.ax_mag.plot(self.time, self.mag_data)
        
        # Setup phase figure
        self.ax_phase.set_title("Phase over Time")
        self.ax_phase.set_xlabel("Time [s]")
        self.ax_phase.set_ylabel("Phase [Degrees]")
        self.ax_phase.set_ylim(-200,200)
        self.line_phase = self.ax_phase.plot(self.time, self.phase_data)
        
        plt.tight_layout()
        plt.ion()
        plt.show(block=False)

    def update(self, samples):
        
        samples = np.asarray(samples)
        new_buffer_magnitude = np.abs(samples) # use builtins
        new_buffer_phase = np.rad2deg(np.angle(samples)) # use numpy builtins rather than doing it manually
        
        self.ax_mag.clear()
        self.ax_phase.clear()
        
        # shift out old data if new data comes in
        num_new_samples = len(samples)
        if num_new_samples >= self.max_points:
            self.mag_data = new_buffer_magnitude[-self.max_points:]
            self.phase_data = new_buffer_phase[-self.max_points:]
        else:
            self.mag_data = np.roll(self.mag_data, -num_new_samples)
            self.phase_data = np.roll(self.phase_data, -num_new_samples)
            self.mag_data[-num_new_samples:] = new_buffer_magnitude
            self.phase_data[-num_new_samples:] = new_buffer_phase
            
        # update actual plots
        self.ax_mag.set_title("Magnitude over Time")
        self.ax_mag.set_xlabel("Time [s]")
        self.ax_mag.set_ylabel("Magnitude [|s(n)|]")
        self.line_mag = self.ax_mag.plot(self.time, self.mag_data)
        
        # Setup phase figure
        self.ax_phase.set_title("Phase over Time")
        self.ax_phase.set_xlabel("Time [s]")
        self.ax_phase.set_ylabel("Phase [Degrees]")
        self.line_phase = self.ax_phase.plot(self.time, self.phase_data)
        
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
