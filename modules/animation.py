import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime

from .simulation import iter_sim

def run_anim(args, cfg, saw_wg, saw_rr):
    """Run the animation mode."""
    fig, ax = plt.subplots()
    ax.set_xlim(0, args.rr_length)
    ax.set_ylim(-2, 2)

    line_input, = ax.plot([], [], lw=3, label='Input')
    line_ring, = ax.plot([], [], lw=3, label='Ring')

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
    ax.legend(loc="upper right")

    def init_anim():
        line_input.set_data([], [])
        line_ring.set_data([], [])
        return line_input, line_ring

    def iter_anim(i):
        nonlocal saw_wg, saw_rr
        iter_text.set_text(f'Iteration: {i}')
        saw_wg, saw_rr = iter_sim(args, cfg, saw_wg, saw_rr, i)
        line_input.set_data(cfg['x_wg'], saw_wg)
        line_ring.set_data(cfg['x_rr'], saw_rr)
        return line_input, line_ring

    anim = FuncAnimation(fig, iter_anim, init_func=init_anim, frames=args.iterations, interval=cfg['delta_t'] * 1000)
    timestamp = datetime.datetime.now().strftime("-%m%d-%H%M%S")
    anim.save(f"animations/output/animation{timestamp}.mp4", writer='ffmpeg', fps=args.fps)
