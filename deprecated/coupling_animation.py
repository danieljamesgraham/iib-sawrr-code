import argparse
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import time
import datetime
# from scipy.stats import norm
# import pickle

animations_path = "animations/output/"
figures_path = "figures/output/"
pickles_path = "pickles/output/"

num_calcs = 0
sim_times = {}

### Simulation

def init_simulation(rr_length, wg_length, rr_vel):
    global cfg, x_wg, x_rr, saw_wg, saw_rr

    cfg = {}

    # Timestep
    cfg["delta_t"] = 1 / args.fps

    # Total input waveguide length
    cfg["input_length"] = wg_length + args.wg_edge_length

    # Number of waveguide datapoints
    coupling_datapoints = int(round(wg_length*args.datapoint_density, 4))
    edge_datapoints = int(args.wg_edge_length * args.datapoint_density)
    cfg["num_wg_datapoints"] = int(round(cfg["input_length"] * args.datapoint_density, 4))
    ring_datapoints = int(rr_length * args.datapoint_density)

    # Ensure velocities are actually as desired
    input_roll = cfg["delta_t"] * args.datapoint_density * args.wg_vel
    ring_velocity = args.wg_vel * rr_vel
    cfg["ring_roll"] = int(cfg["delta_t"] * args.datapoint_density * ring_velocity)
    if cfg["ring_roll"]/input_roll != ring_velocity/args.wg_vel:
        print(f"WARNING - exact rolls:\n- Input: {input_roll}\n- Ring: {cfg['ring_roll']}")

    # WG and RR x-axes
    x_wg = np.linspace(0, cfg["input_length"]-1, cfg["num_wg_datapoints"])
    x_rr = np.linspace(0, rr_length, ring_datapoints)

    # WG and RR initial SAWs
    saw_wg = []
    saw_rr = np.zeros(ring_datapoints)

    # WG edge window
    cfg["window_arr"] = np.concatenate((0.5*(1+np.sin(np.linspace(-np.pi/2, np.pi/2, int(edge_datapoints/2)))),
                             np.ones(coupling_datapoints),
                             0.5*(1-np.sin(np.linspace(-np.pi/2, np.pi/2, int(edge_datapoints/2))))
                             ))

def iterate_simulation(i):
    global cfg, x_wg, x_rr, saw_wg, saw_rr

    # Iterate WG SAW
    saw_wg = np.sin(2 * np.pi * (x_wg - cfg["delta_t"] * args.wg_vel * i)) * cfg["window_arr"]

    # Iterate RR SAW
    saw_rr = (1 - 0.1**args.rr_decay_exp) * saw_rr # Decay
    saw_rr[:cfg["num_wg_datapoints"]] += args.wg2rr_coeff * saw_wg # Coupling
    saw_rr= np.roll(saw_rr, cfg["ring_roll"]) # Travelling

    return saw_wg, saw_rr

def print_progress(total_calcs, refresh_calcs):
    global num_calcs, sim_times 

    if num_calcs % refresh_calcs == 0:
        sim_times["start_time"] = time.time()
    elif num_calcs % refresh_calcs == refresh_calcs - 1:
        sim_times["refresh_calcs_time"] = time.time() - sim_times["start_time"]

    print(f"\rCompletion: {(num_calcs*100/total_calcs):05.2f}%", end="")
    if num_calcs > refresh_calcs:
        print(f"\nEstimated time: {str(datetime.timedelta(seconds=int(sim_times['refresh_calcs_time']*(total_calcs-num_calcs)/refresh_calcs))).zfill(8)}\033[F", end="")

    num_calcs += 1

def get_plot_text():
    plot_text = ''
    plot_text += "Coupling coefficient: " + str(args.wg2rr_coeff)
    plot_text += "\nDecay exponent: " + str(args.rr_decay_exp)
    plot_text += "\nEdge length: " + str(args.wg_edge_length)
    plot_text += "\nCoupling length: " + str(args.wg_length)
    plot_text += "\nDatapoints: " + str(args.datapoint_density)
    plot_text += "\nDatapoint density: " + str(args.datapoint_density)

    return plot_text

def init_animation(): 
    global sim_times 
    sim_times = {}
    line_input.set_data([], [])
    line_ring.set_data([], [])
    return line_input, line_ring,

def animate(i):
    global x_wg, x_rr, saw_wg, saw_rr

    # Display iteration number
    iteration_text.set_text(f'Iteration: {i}')

    # Count number of calculations completed and print progress
    num_calcs = i
    print_progress(args.iterations, 100)

    saw_wg, saw_rr = iterate_simulation(i)

    # Assign data
    line_input.set_data(x_wg, saw_wg)
    line_ring.set_data(x_rr, saw_rr)

    return line_input, line_ring,

def run_simulation():
    global cfg, saw_rr, line_input, line_ring, iteration_text

    init_simulation(args.rr_length, args.wg_length, args.rr_vel)

    if args.mode == "animation":
        # Plot parameters
        fig = plt.figure()
        ax = plt.axes(xlim=(0, args.rr_length), ylim=(-2, 2))
        ax.set_title(f"Waveguide Coupling Simulation")
        ax.set_xlabel("Length (# of input $\lambda$)")
        ax.set_ylabel("Amplitude (arb.)")
        line_input, = ax.plot([], [], lw = 3, label='Input')
        line_ring, = ax.plot([], [], lw = 3, label='Ring')
        iteration_text = ax.text(0.02, 0.98, '', ha='left', va='top', transform=plt.gca().transAxes)
        plt.text(0.98, 0.02, get_plot_text(), ha='right', va='bottom', transform=plt.gca().transAxes)
        ax.legend(loc="upper right")
        plt.tight_layout()

        # Run simulation as animation and save
        anim = FuncAnimation(fig, animate, init_func=init_animation, frames=args.iterations, interval=cfg["delta_t"]*1000)

        # Save animation as mp4 with current time and date
        now = datetime.datetime.now()
        current_time = now.strftime("-%m%d-%H%M%S")
        file_name = args.mode + current_time
        anim.save(animations_path+file_name+".mp4", writer = 'ffmpeg', fps = args.fps)

    elif args.mode == "simulation":
        # for i in range(args.iterations):
        #     saw_wg, saw_rr = iterate_simulation(i, saw_rr)
        # return saw_wg, saw_rr
        raise ValueError("I have not finished non-animated simulations!")

### Main

parser = argparse.ArgumentParser(description="A script that simulates the coupling of SAWs between an input waveguide and a RR.")

# Simulation parameters
parser.add_argument("mode", type=str, choices=["animation", "simulation"])
parser.add_argument("--iterations", type=int, default=1000, help="Number of simulation iterations - default: 1000")
parser.add_argument("--datapoint-density", type=int, default=100, help="Number of simulation datapoints per unit length - default: 100")
parser.add_argument("--fps", type=int, default=25, help="Number of simulation frames per second - default: 25")

# Waveguide geometry
parser.add_argument("--wg-length", type=float, default=1, help="Waveguide length - default: 1")
parser.add_argument("--wg-edge-length", type=float, default=1, help="Waveguide window function (total) edge length - default: 1")
# Waveguide SAW properties
parser.add_argument("--wg-vel", type=float, default=2, help="Waveguide SAW velocity - default: 2")
parser.add_argument("--wg2rr-coeff", type=float, default=0.05, help="Waveguide to ring resonator SAW coupling coefficient - default: 0.05")
parser.add_argument("--wg-decay-exp", type=float, default=3, help="Waveguide SAW decay exponent - default: 3")

# Ring resonator geometry
parser.add_argument("--rr-length", type=float, default=15, help="Ring resonator length - default: 15")
# Ring resonator SAW properties
parser.add_argument("--rr-vel", type=float, default=1.5, help="Ring resonator SAW velocity (ratio) - default: 1.5")
parser.add_argument("--rr2wg-coeff", type=float, default=0.05, help="Ring resonator to waveguide SAW coupling coefficient - default: 0.05")
parser.add_argument("--rr-decay-exp", type=float, default=3, help="Ring resonator SAW decay exponent - default: 3")

args = parser.parse_args()

if (args.datapoint_density % 2 != 0) or (not isinstance(args.datapoint_density, int)):
    raise ValueError("Number of simulation datapoints per unit length must be an even integer")

run_simulation()
