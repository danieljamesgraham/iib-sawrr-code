from matplotlib import pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from scipy.stats import norm

### Variables

# Coupling coefficient
coupling_coeff = 0.02

# Wave velocities
input_velocity = 2
ring_velocity = 3

# Input waveguide lengths
coupling_length = 2.242
edge_length = 0.5

# Ring waveguide length
ring_length = 15

# Plot y-limit
y_lim = 1

# Simulation parameters
datapoints = 100
frames = 750
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

### Initialise plot

# Plot parameters
fig = plt.figure()
ax = plt.axes(xlim=(0, ring_length), ylim=(-y_lim, y_lim))
ax.set_title(f"Waveguide Coupling Simulation (Coupling Length = {input_length}$\lambda$)")
ax.set_xlabel("Length (# of input $\lambda$)")
ax.set_ylabel("Amplitude (arb.)")
iteration_text = ax.text(0.75, 0.9, '', transform=ax.transAxes)
line_input, = ax.plot([], [], lw = 3, label='Input')
line_ring, = ax.plot([], [], lw = 3, label='Ring')
ax.legend(loc="lower right")
plt.tight_layout()

# x axes and ring y axis
x_input = np.linspace(0, input_length, input_datapoints)
x_ring = np.linspace(0, ring_length, ring_datapoints)
y_ring = np.zeros(ring_datapoints)

# Coupling window
window = np.concatenate((0.5*(1+np.sin(np.linspace(-np.pi/2, np.pi/2, int(edge_datapoints/2)))),
                         np.ones(coupling_datapoints),
                         0.5*(1-np.sin(np.linspace(-np.pi/2, np.pi/2, int(edge_datapoints/2))))
                         ))

### Initialisation function
def init(): 
    line_input.set_data([], [])
    line_ring.set_data([], [])
    return line_input, line_ring,

### Animation function
def animate(i):
    global window, y_ring

    # Display iteration number
    iteration_text.set_text(f'Iteration: {i}')

    # Input waveguide travelling wave
    y_input = np.sin(2 * np.pi * (x_input - delta_t * input_velocity * i)) * window

    # Coupling into ring waveguide and travelling wave
    y_ring[:input_datapoints] += coupling_coeff * y_input
    y_ring = np.roll(y_ring, ring_roll)

    # Assign data
    line_input.set_data(x_input, y_input)
    line_ring.set_data(x_ring, y_ring)

    return line_input, line_ring,

# Run animation and save
anim = FuncAnimation(fig, animate, init_func=init, frames=frames, interval=delta_t*1000)
anim.save('coupling_simulation.mp4', writer = 'ffmpeg', fps = fps)
