# TODO: Add timing function
# TODO: Change steps to step (eg. # to step size)
# TODO: Change speed so that not coupled to 25 fps
# TODO: Link parser arguments to specific modes
# TODO: Add datapoint density to plots
# TODO: Fix bug with window and x array sizes
# TODO: Add option to disable window function and relax even constraint
# TODO: Use optimised coupling length from pickle instead of brute forcing
# TODO: Move calculations out of init to speed up

import argparse
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from scipy.stats import norm
import time
import datetime
import pickle

parser = argparse.ArgumentParser(description="A script that simulates the coupling of acoustic waves between an input waveguide and a resonant ring waveguide.")
parser.add_argument('mode', type=str, choices=["animation", "max_amp_vs_coupling_length", "max-amp-vs-velocity-ratio"])

parser.add_argument('--iterations', type=int, default="1000")
parser.add_argument('--datapoint_density', type=int, default="100")
parser.add_argument('--fps', type=int, default="25")
parser.add_argument('--coupling_coeff', type=float, default="0.05")
parser.add_argument('--decay_exponent', type=float, default="3")
parser.add_argument('--coupling_length', type=float, default="1")
parser.add_argument('--input_velocity', type=float, default="2")
parser.add_argument('--velocity_ratio', type=float, default="1.5")
parser.add_argument('--edge_length', type=float, default="0.5")
parser.add_argument('--ring_length', type=float, default="15")

parser.add_argument('--coupling-step', type=float, default="0.01")
parser.add_argument('--min-coupling-length', type=float, default="0")
parser.add_argument('--max-coupling-length', type=float, default="3")

parser.add_argument('--velocity-step', type=int, default="100")
parser.add_argument('--min-velocity-ratio', type=float, default="1")
parser.add_argument('--max-velocity-ratio', type=float, default="2")

args = parser.parse_args()

animations_path = "animations/output/"
figures_path = "figures/output/"
pickles_path = "pickles/output/"

calcs, time_dict = 0, {}

def get_plot_text():
    plot_text = ''
    plot_text += "Coupling coefficient: " + str(args.coupling_coeff)
    plot_text += "\nDecay exponent: " + str(args.decay_exponent)
    plot_text += "\nEdge length: " + str(args.edge_length)
    if args.mode == "animation":
        plot_text += "\nCoupling length: " + str(args.coupling_length)
    if args.mode == "max_amp_vs_coupling_length" or args.mode == "animation":
        plot_text += "\nRing length: " + str(args.ring_length)
        plot_text += "\nVelocity ratio: " + str(args.velocity_ratio)
    if args.mode == "animation":
        plot_text += "\nDatapoints: " + str(args.datapoint_density)
    if args.mode == "max_amp_vs_coupling_length" or args.mode == "max_amp-vs-velocity-ratio":
        plot_text += "\nIterations: " + str(args.iterations)
        plot_text += "\nCoupling step: " + str(args.coupling_step)
    if args.mode == "max-amp-vs-velocity-ratio":
        plot_text += "\nVelocity step: " + str(args.velocity_step)
    plot_text += "\nDatapoint density: " + str(args.datapoint_density)

    return plot_text

def init_simulate_coupling(ring_length, coupling_length, velocity_ratio):
    cfg, init_arrs = {}, {}

    # Timestep
    cfg["delta_t"] = 1 / args.fps

    # Total input waveguide length
    cfg["input_length"] = coupling_length + args.edge_length

    # Number of waveguide datapoints
    coupling_datapoints = int(round(coupling_length*args.datapoint_density, 4))
    edge_datapoints = int(args.edge_length * args.datapoint_density)
    cfg["input_datapoints"] = int(round(cfg["input_length"] * args.datapoint_density, 4))
    ring_datapoints = int(ring_length * args.datapoint_density)

    # Ensure velocities are actually as desired
    input_roll = cfg["delta_t"] * args.datapoint_density * args.input_velocity
    ring_velocity = args.input_velocity * velocity_ratio
    cfg["ring_roll"] = int(cfg["delta_t"] * args.datapoint_density * ring_velocity)
    if cfg["ring_roll"]/input_roll != ring_velocity/args.input_velocity:
        print(f"WARNING - exact rolls:\n- Input: {input_roll}\n- Ring: {cfg['ring_roll']}")

    # x axes and ring y axis
    init_arrs["x_input"] = np.linspace(0, cfg["input_length"], cfg["input_datapoints"])
    init_arrs["x_ring"] = np.linspace(0, ring_length, ring_datapoints)
    init_arrs["y_ring"] = np.zeros(ring_datapoints)

    # Coupling window
    init_arrs["window"] = np.concatenate((0.5*(1+np.sin(np.linspace(-np.pi/2, np.pi/2, int(edge_datapoints/2)))),
                             np.ones(coupling_datapoints),
                             0.5*(1-np.sin(np.linspace(-np.pi/2, np.pi/2, int(edge_datapoints/2))))
                             ))

    # print("\n\n")
    # print(f"x_input: {len(init_arrs['x_input'])}")
    # print(f"ring_length: {ring_length}")
    # print(f"ring_datapoints: {ring_length}")
    # print(f"window: {len(init_arrs['window'])}")
    # print(f"edge_datapoints/2: {int(edge_datapoints/2)}")
    # print(f"coupling_datapoints: {coupling_datapoints}")
    # print(f"coupling_length: {coupling_length}")
    # print(f"datapoint_density: {args.datapoint_density}")
    # print(f"coupling_length*datpoint_density: {coupling_length*args.datapoint_density}")

    return cfg, init_arrs

def simulate_coupling(i, y_ring, init_arrs, cfg):
    # Input waveguide travelling wave
    y_input = np.sin(2 * np.pi * (init_arrs["x_input"] - cfg["delta_t"] * args.input_velocity * i)) * init_arrs["window"]

    # Coupling into ring waveguide and travelling wave
    y_ring = (1 - 0.1**args.decay_exponent) * y_ring # Decay
    y_ring[:cfg["input_datapoints"]] += args.coupling_coeff * y_input # Coupling
    y_ring = np.roll(y_ring, cfg["ring_roll"]) # Travelling

    return y_input, y_ring

def get_max_amplitude(cfg, init_arrs):
    max_amplitude = 0
    y_ring = init_arrs["y_ring"]

    for i in range(args.iterations):
        y_input, y_ring = simulate_coupling(i, y_ring, init_arrs, cfg)
        max_y_ring = max(y_ring)
        if max_y_ring > max_amplitude:
            max_amplitude = max_y_ring

    return max_amplitude

def print_completion(total_calcs, n_calcs):
    global calcs, time_dict

    if calcs % n_calcs == 0:
        time_dict["start_time"] = time.time()
    elif calcs % n_calcs == n_calcs - 1:
        time_dict["n_calcs_time"] = time.time() - time_dict["start_time"]

    print(f"\rCompletion: {(calcs*100/total_calcs):05.2f}%", end="")
    if calcs > n_calcs:
        print(f"\nEstimated time: {str(datetime.timedelta(seconds=int(time_dict['n_calcs_time']*(total_calcs-calcs)/n_calcs))).zfill(8)}\033[F", end="")

    calcs += 1

def init_animate(): 
    global time_dict
    time_dict = {}
    line_input.set_data([], [])
    line_ring.set_data([], [])
    return line_input, line_ring,

def animate(i):
    global y_ring, init_arrs, cfg

    # Display iteration number
    iteration_text.set_text(f'Iteration: {i}')

    calcs = i
    print_completion(args.iterations, 100)

    y_input, y_ring = simulate_coupling(i, y_ring, init_arrs, cfg)

    # Assign data
    line_input.set_data(init_arrs["x_input"], y_input)
    line_ring.set_data(init_arrs["x_ring"], y_ring)

    return line_input, line_ring,

def animate_simulation():
    global cfg, init_arrs, y_ring, line_input, line_ring, iteration_text
    cfg, init_arrs = init_simulate_coupling(args.ring_length, args.coupling_length, args.velocity_ratio)

    # Plot parameters
    fig = plt.figure()
    ax = plt.axes(xlim=(0, args.ring_length), ylim=(-2, 2))
    ax.set_title(f"Waveguide Coupling Simulation")
    ax.set_xlabel("Length (# of input $\lambda$)")
    ax.set_ylabel("Amplitude (arb.)")
    line_input, = ax.plot([], [], lw = 3, label='Input')
    line_ring, = ax.plot([], [], lw = 3, label='Ring')
    iteration_text = ax.text(0.02, 0.98, '', ha='left', va='top', transform=plt.gca().transAxes)
    plt.text(0.98, 0.02, get_plot_text(), ha='right', va='bottom', transform=plt.gca().transAxes)
    ax.legend(loc="upper right")
    plt.tight_layout()

    # Run animation and save
    y_ring = init_arrs["y_ring"]
    anim = FuncAnimation(fig, animate, init_func=init_animate, frames=args.iterations, interval=cfg["delta_t"]*1000)

    file_name = args.mode + current_time
    anim.save(animations_path+file_name+".mp4", writer = 'ffmpeg', fps = args.fps)

def vary_coupling_length(ring_length, velocity_ratio, completion=False):
    global calcs, time_dict
    max_amplitudes = []

    coupling_lengths = np.arange(args.min_coupling_length, args.max_coupling_length+args.coupling_step, args.coupling_step)
    total_calcs = len(coupling_lengths)

    for coupling_length in coupling_lengths:
        cfg, init_arrs = init_simulate_coupling(ring_length, round(coupling_length,8), velocity_ratio)
        max_amplitudes.append(get_max_amplitude(cfg, init_arrs))

        if completion == True:
            print_completion(total_calcs, 10)

    return coupling_lengths, max_amplitudes

def plot_max_amp_vs_coupling_length():
    coupling_lengths, max_amplitudes = vary_coupling_length(args.ring_length, args.velocity_ratio, True)
    max_amplitudes = max_amplitudes / max(max_amplitudes)

    # Plot and save figure
    plt.plot(coupling_lengths+args.edge_length, max_amplitudes)
    plt.xlim(args.min_coupling_length+args.edge_length, args.max_coupling_length+args.edge_length)
    plt.ylim(0, 1.05)
    plt.title("Variation in Maximum Ring Acoustic\nWave Amplitude with Coupling Length")
    plt.xlabel("Coupling length (# of $\lambda$)")
    plt.ylabel("Normalised Maximum Amplitude")
    plt.text(0.98, 0.02, get_plot_text(), ha='right', va='bottom', transform=plt.gca().transAxes)
    plt.tight_layout()

    file_name = "max_amp_vs_coupling_length" + current_time
    plt.savefig(figures_path+file_name+".png", format='png', dpi=300)
    with open(pickles_path+file_name+".pickle", "wb") as f:
        pickle.dump([coupling_lengths, max_amplitudes], f)

def plot_max_amp_vs_velocity_ratio():
    global calcs, time_dict
    amplitudes = []

    velocity_ratios = np.arange(args.min_velocity_ratio, args.max_velocity_ratio+args.velocity_step, args.velocity_step)
    total_calcs = len(velocity_ratios)

    for velocity_ratio in velocity_ratios:
        ring_length = velocity_ratio * args.ring_length
        coupling_lengths, max_amplitudes = vary_coupling_length(ring_length, velocity_ratio)
        amplitudes.append(max(max_amplitudes))

        print_completion(total_calcs, 10)

    amplitudes = amplitudes / max(amplitudes)

    # Plot and save figure
    plt.plot(velocity_ratios, amplitudes)
    plt.xlim(args.min_velocity_ratio, args.max_velocity_ratio)
    plt.ylim(0, 1.05)
    plt.rc('text', usetex=True)
    plt.title("Varation in Maxmimum Ring Amplitude with Velocity Ratio\n (Coupling Length Optimised)")
    plt.xlabel(r"$v_\text{ring}/v_\text{input}$")
    plt.ylabel("Normalised Maximum Amplitude")
    plt.text(0.98, 0.98, get_plot_text(), ha='right', va='top', transform=plt.gca().transAxes)
    plt.tight_layout()

    file_name = args.mode + current_time
    plt.savefig(figures_path+file_name+".png", format='png', dpi=300)
    with open(pickles_path+file_name+".pickle", "wb") as f:
        pickle.dump([velocity_ratios, amplitudes], f)

# Get current date and time
now = datetime.datetime.now()
current_time = now.strftime("-%m%d-%H%M%S")

if args.datapoint_density % 2 != 0:
    raise ValueError("Number of datapoints must be even")

if args.mode == "animation":
    animate_simulation()
elif args.mode == "max_amp_vs_coupling_length":
    plot_max_amp_vs_coupling_length()
elif args.mode == "max-amp-vs-velocity-ratio":
    plot_max_amp_vs_velocity_ratio()
