import argparse
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import time
import datetime

# Constants for paths
ANIMATIONS_PATH = "animations/output/"

def init_sim(args):
    """Initialise the simulation."""

    # Initial calculations
    delta_t = 1 / args.fps
    wg_total_length = args.wg_length + args.wg_edge_length
    num_wg_datapoints = int(round(wg_total_length * args.datapoint_density, 4))
    ring_datapoints = int(args.rr_length * args.datapoint_density)

    # Ensure velocities are correct
    ring_velocity = args.wg_vel * args.rr_vel
    ring_roll = int(delta_t * args.datapoint_density * ring_velocity)

    # Edge and coupling calculations
    coupling_datapoints = int(round(args.wg_length * args.datapoint_density, 4))
    edge_datapoints = int(args.wg_edge_length * args.datapoint_density)
    window_arr = np.concatenate((
        0.5 * (1 + np.sin(np.linspace(-np.pi/2, np.pi/2, edge_datapoints // 2))),
        np.ones(coupling_datapoints),
        0.5 * (1 - np.sin(np.linspace(-np.pi/2, np.pi/2, edge_datapoints // 2)))
    ))

    # Initialise x axes
    x_wg = np.linspace(0, wg_total_length - 1, num_wg_datapoints)
    # TODO: -1?
    x_rr = np.linspace(0, args.rr_length, ring_datapoints)

    # Initialise SAWs
    saw_wg = np.zeros(len(x_wg))
    saw_rr = np.zeros(ring_datapoints)

    cfg = {'delta_t': delta_t,
           'num_wg_datapoints': num_wg_datapoints,
           'ring_datapoints': ring_datapoints,
           'ring_roll': ring_roll,
           'window_arr': window_arr,
           'x_wg': x_wg,
           'x_rr': x_rr,
           }

    return cfg, saw_wg, saw_rr

def iter_sim(args, cfg, saw_wg, saw_rr, i):
    """Perform a single iteration of the simulation."""

    # Update waveguide SAW
    saw_wg = np.sin(2 * np.pi * (cfg['x_wg'] - cfg['delta_t'] * args.wg_vel * i)) * cfg['window_arr']

    # Update ring resonator SAW
    saw_rr *= (1 - 0.1 ** args.rr_decay_exp)  # Decay
    saw_rr[:cfg['num_wg_datapoints']] += args.wg2rr_coeff * saw_wg  # Coupling
    saw_rr = np.roll(saw_rr, cfg['ring_roll'])  # Traveling

    return saw_wg, saw_rr

def run_anim(args, cfg, saw_wg, saw_rr):
    """Run the animation mode."""

    # Plot setup
    fig, ax = plt.subplots()
    # Plot limits
    ax.set_xlim(0, args.rr_length)
    ax.set_ylim(-2, 2)
    # Plot line objects
    line_input, = ax.plot([], [], lw=3, label='Input')
    line_ring, = ax.plot([], [], lw=3, label='Ring')
    # Plot text and labels
    ax.set_title("Waveguide Coupling Simulation")
    ax.set_xlabel("Length (# of input $\\lambda$)")
    ax.set_ylabel("Amplitude (arb.)")
    iter_text = ax.text(0.02, 0.98, '', ha='left', va='top', transform=ax.transAxes)
    cfg_text = (f"Coupling coefficient: {args.wg2rr_coeff}\n"
                           f"Decay exponent: {args.rr_decay_exp}\n"
                           f"Edge length: {args.wg_edge_length}\n"
                           f"Coupling length: {args.wg_length}\n"
                           f"Datapoints: {args.datapoint_density}")
    ax.text(0.98, 0.02, cfg_text, ha='right', va='bottom', transform=ax.transAxes)
    # Plot legend
    ax.legend(loc="upper right")

    # Initialise animation
    def init_anim():
        line_input.set_data([], [])
        line_ring.set_data([], [])
        return line_input, line_ring

    # Iterate animation
    def iter_anim(i):
        nonlocal saw_wg, saw_rr
        iter_text.set_text(f'Iteration: {i}')
        saw_wg, saw_rr = iter_sim(args, cfg, saw_wg, saw_rr, i)
        line_input.set_data(cfg['x_wg'], saw_wg)
        line_ring.set_data(cfg['x_rr'], saw_rr)
        return line_input, line_ring

    # Run animation and save it with timestamp
    anim = FuncAnimation(fig, iter_anim, init_func=init_anim, frames=args.iterations, interval=cfg['delta_t'] * 1000)
    timestamp = datetime.datetime.now().strftime("-%m%d-%H%M%S")
    anim.save(f"{ANIMATIONS_PATH}animation{timestamp}.mp4", writer='ffmpeg', fps=args.fps)

### Main Script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulates coupling of SAWs between an input waveguide and a ring resonator.")
    # Simulation parameters
    parser.add_argument("mode", type=str, choices=["animation"], help="Mode to run the simulation.")
    parser.add_argument("--iterations", type=int, default=1000, help="Number of simulation iterations.")
    parser.add_argument("--datapoint-density", type=int, default=100, help="Number of datapoints per unit length.")
    parser.add_argument("--fps", type=int, default=25, help="Frames per second for animation.")
    # Waveguide geometry
    parser.add_argument("--wg-length", type=float, default=1, help="Waveguide length.")
    parser.add_argument("--wg-edge-length", type=float, default=1, help="Waveguide edge length.")
    parser.add_argument("--wg-vel", type=float, default=2, help="Waveguide SAW velocity.")
    # Ring resonator geometry
    parser.add_argument("--rr-length", type=float, default=15, help="Ring resonator length.")
    parser.add_argument("--rr-vel", type=float, default=1.5, help="Ring resonator velocity (ratio).")
    # Coupling and decay
    parser.add_argument("--wg2rr-coeff", type=float, default=0.05, help="Coupling coefficient from waveguide to resonator.")
    parser.add_argument("--rr-decay-exp", type=float, default=3, help="Resonator decay exponent.")

    args = parser.parse_args()

    # Validate arguments
    if args.datapoint_density % 2 != 0:
        raise ValueError("Datapoint density must be an even integer.")

    # Initialise simulation
    cfg, saw_wg, saw_rr = init_sim(args)

    if args.mode == "animation":
        run_anim(args, cfg, saw_wg, saw_rr)
