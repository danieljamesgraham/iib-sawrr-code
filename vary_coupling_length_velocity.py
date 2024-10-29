from matplotlib import pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from scipy.stats import norm

def iterate_coupling_length(coupling_length, velocity_ratio):
    ### Variables

    max_amplitude = 0

    # Coupling coefficient
    coupling_coeff = 0.02

    # Wave velocities
    input_velocity = 2.5
    ring_velocity = input_velocity * velocity_ratio

    # Input waveguide lengths
    edge_length = 0.5

    # Ring waveguide length
    ring_length = 10 * velocity_ratio

    # Plot y-limit
    y_lim = 1

    # Simulation parameters
    datapoints = 100
    frames = 1000
    fps = 25

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
        y_ring[:input_datapoints] += coupling_coeff * y_input
        y_ring = np.roll(y_ring, ring_roll)

        return y_ring

    for i in range(5000):
        y_ring = animate(i, y_ring, window, x_input, delta_t)
        if max(y_ring) > max_amplitude:
            max_amplitude = max(y_ring)

    return max_amplitude

max_amplitudes = []

coupling_lengths = np.linspace(0, 3, 10)
velocity_ratios = np.linspace(1, 2, 11)

for velocity_ratio in velocity_ratios:
    print(velocity_ratio)
    amplitudes = []
    for coupling_length in coupling_lengths:
        amplitudes.append(iterate_coupling_length(coupling_length, velocity_ratio))

    max_amplitudes.append(max(amplitudes))

plt.plot(velocity_ratios, max_amplitudes)
plt.xlim(1, 2)
plt.ylim(0, 35)
plt.rc('text', usetex=True)
plt.xlabel(r"$v_\text{ring}/v_\text{input}$")
plt.ylabel("Maximum Amplitude (arb.)")
plt.title("Varation in Maxmimum Ring Amplitude with Velocity Ratio\n (Coupling Length Optimised)")
plt.savefig("amplitude_coupling_length_velocity.png", format='png', dpi=300)
