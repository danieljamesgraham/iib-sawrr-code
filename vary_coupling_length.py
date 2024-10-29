from matplotlib import pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from scipy.stats import norm
from datetime import datetime

def iterate_coupling_length(coupling_length):
    global plot_text
    ### Variables

    max_amplitude = 0

    # Coupling coefficient
    coupling_coeff = 0.05

    decay_exponent = 3

    # Wave velocities
    input_velocity = 2
    ring_velocity = 3

    # Input waveguide lengths
    edge_length = 0.5

    # Ring waveguide length
    ring_length = 15

    # Plot y-limit
    y_lim = 1

    # Simulation parameters
    datapoints = 100
    frames = 1000
    fps = 25

    plot_text = "Coupling coefficient: " + str(coupling_coeff) +\
                "\nDecay exponent: "    + str(decay_exponent) +\
                "\nVelocity ratio: "    + str(round(ring_velocity/input_velocity, 2)) +\
                "\nCoupling length: "   + str(round(edge_length+coupling_length, 2)) +\
                "\nRing length: "       + str(ring_length) +\
                "\nDatapoints: "        + str(datapoints)

    ### Preliminary calculations

    # Timestep
    delta_t = 1 / fps

    # Total input waveguide length
    input_length = coupling_length + edge_length

    # Number of waveguide datapoints
    coupling_datapoints = int(coupling_length * datapoints)
    edge_datapoints = int(edge_length * datapoints)
    input_datapoints = int(input_length * datapoints)
    ring_datapoints = int(ring_length * datapoints)

    # Ensure velocities are actually as desired
    input_roll = delta_t * datapoints * input_velocity
    ring_roll = int(delta_t * datapoints * ring_velocity)
    if ring_roll/input_roll != ring_velocity/input_velocity:
        print(f"WARNING - exact rolls:\n- Input: {input_roll}\n- Ring: {ring_roll}")

    # x axes and ring y axis
    x_input = np.linspace(0, input_length, input_datapoints)
    x_ring = np.linspace(0, ring_length, ring_datapoints)
    y_ring = np.zeros(ring_datapoints)

    # Coupling window
    window = np.concatenate((0.5*(1+np.sin(np.linspace(-np.pi/2, np.pi/2, int(edge_datapoints/2)))),
                             np.ones(coupling_datapoints),
                             0.5*(1-np.sin(np.linspace(-np.pi/2, np.pi/2, int(edge_datapoints/2))))
                             ))

    ### Animation function
    def animate(i, y_ring, window, x_input, delta_t):

        # Input waveguide travelling wave
        y_input = np.sin(2 * np.pi * (x_input - delta_t * input_velocity * i)) * window

        # Coupling into ring waveguide and travelling wave
        y_ring = (1 - 0.1**decay_exponent) * y_ring
        y_ring[:input_datapoints] += coupling_coeff * y_input
        y_ring = np.roll(y_ring, ring_roll)

        return y_ring

    for i in range(5000):
        y_ring = animate(i, y_ring, window, x_input, delta_t)
        if max(y_ring) > max_amplitude:
            max_amplitude = max(y_ring)

    return max_amplitude

max_amplitudes = []

x_vals = np.linspace(0, 14.5, 1000)

for i in x_vals:
    max_amplitudes.append(iterate_coupling_length(i))

max_amplitudes = max_amplitudes / max(max_amplitudes)

# print(max_amplitudes)

# Get current date and time
now = datetime.now()
current_time = now.strftime("_%m%d_%H%M%S")
directory = "figures/"
file_name = "amplitude_coupling_length"
file_format = "png"
relative_path = directory + file_name + current_time + '.' + file_format

plt.plot(x_vals, max_amplitudes)
plt.xlim(0, 14.5)
plt.ylim(0, 1.05)
plt.xlabel("Coupling length - 0.5$\lambda$")
plt.ylabel("Maximum Amplitude (arb.)")
plt.title("Variation in Maximum Ring Amplitude with Coupling length")
plt.text(0.98, 0.02, plot_text, ha='right', va='bottom', transform=plt.gca().transAxes)
plt.savefig(relative_path, format=file_format, dpi=300)
