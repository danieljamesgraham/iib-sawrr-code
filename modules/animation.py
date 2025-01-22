import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime

from .simulation import init_sim, iter_sim

def run_anim(args):
    """Run the animation mode."""

    # Initialise simulation
    cfg, saw_wg, saw_rr = init_sim(args, args.wg_length)

    # Initialise plot
    fig, ax = plt.subplots()
    ax.set_xlim(0, args.rr_length)
    ax.set_ylim(-2, 2)
    line_input, = ax.plot([], [], lw=3, label='Input')
    line_ring, = ax.plot([], [], lw=3, label='Ring')
    ax.set_title("Simulation of SAW Coupling")
    ax.set_xlabel("Waveguide Position (SAW Wavelengths)")
    ax.set_ylabel("Amplitude (arb.)")
    iter_text = ax.text(0.02, 0.98, '', ha='left', va='top', transform=ax.transAxes)
    cfg_text = (f"SAW velocity in input: {args.wg_vel} (arb.)\n"
                f"SAW velocity in RR: {args.rr_vel} (arb.)\n"
                f"Input to RR coupling coefficient: {args.wg2rr_coupl}\n"
                f"RR to input coupling coefficient: {args.rr2wg_coupl}\n"
                f"Input to RR loss coefficient: {args.wg2rr_loss}\n"
                f"RR to input loss coefficient: {args.rr2wg_loss}\n"
                f"SAW decay coefficient: {args.rr_decay_exp}\n"
                )
    ax.text(0.98, 0, cfg_text, ha='right', va='bottom', transform=ax.transAxes)
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

    # Generate and save animation
    if not args.dry_run:
        anim = FuncAnimation(fig, iter_anim, init_func=init_anim, frames=args.iterations, interval=cfg['delta_t'] * 1000)
        timestamp = datetime.datetime.now().strftime("%m%d-%H%M%S")
        filename = f"{args.output_dir}animation-{timestamp}.mp4"
        anim.save(filename, writer='ffmpeg', fps=args.fps)
        print(f"Saved: {filename}")
