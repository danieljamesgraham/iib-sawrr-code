import datetime
import numpy as np
import matplotlib.pyplot as plt

from .simulation import init_sim, iter_sim, print_iter

def iter_max_amps(args, cfg, saw_wg, saw_rr):
    """Iterate the maximum RR amplitude mode."""

    max_amp = 0
    for i in range(args.iterations):
        # Iterate the simulation and get maximum SAW amplitude in the iteration
        saw_wg, saw_rr = iter_sim(args, cfg, saw_wg, saw_rr, i)
        # Set maximum SAW value for entire simulation
        if max(saw_rr) > max_amp:
            max_amp = max(saw_rr)

    return max_amp

def run_max_amps(args):
    """Run the maximum RR amplitude mode."""

    # Check that all input waveguide lengths can actually be simulated
    if np.floor(np.log10(abs(1/args.step_wg_length))) > np.floor(np.log10(abs(args.datapoint_density))):
        raise ValueError("Datapoint density too small for specified waveguide length step size!")
    
    # Generate input waveguide lengths array
    wg_lengths = np.arange(args.min_wg_length, args.max_wg_length, args.step_wg_length)

    max_amps = []
    # Iterate coupling lengths
    for i in range(len(wg_lengths)):
        # Update the iteration counter after each complete simulation
        print_iter(i, len(wg_lengths), args.print_freq)

        # Initialise simulation and then run for specific coupling length
        cfg, saw_wg, saw_rr = init_sim(args, wg_lengths[i])
        max_amp = iter_max_amps(args, cfg, saw_wg, saw_rr)

        # Append maximum SAW amplitude in RR to array of values for all coupling lengths
        max_amps.append(max_amp)

    # Normalise maximum amplitudes
    max_amp_norm_factor = 1 / np.max(max_amps)
    norm_max_amps = np.array(max_amps) * max_amp_norm_factor

    # Generate plot
    plt.plot(wg_lengths, norm_max_amps)
    plt.xlim(0, args.max_wg_length-args.step_wg_length)
    plt.ylim(0, 1.05)
    plt.title("Variation in Maximum RR SAW Amplitude\nWith Coupling Length Between Input and RR")
    plt.xlabel("Coupling Length (Number of SAW Wavelengths)")
    plt.ylabel("Normalised Maximum SAW Amplitude")
    cfg_text = (f"SAW velocity in input: {args.wg_vel} (arb.)\n"
                f"SAW velocity in RR: {args.rr_vel} (arb.)\n"
                f"Input to RR coupling coefficient: {args.wg2rr_coupl}\n"
                f"RR to input coupling coefficient: {args.rr2wg_coupl}\n"
                f"Input to RR loss coefficient: {args.wg2rr_loss}\n"
                f"RR to input loss coefficient: {args.rr2wg_loss}\n"
                f"SAW decay coefficient: {args.rr_decay_exp}\n"
                )
    plt.text(0.98, 0, cfg_text, ha='right', va='bottom', transform=plt.gca().transAxes)
    plt.tight_layout()

    # Save plot with timestamp
    timestamp = datetime.datetime.now().strftime("%m%d-%H%M%S")
    filename = f"{args.output_dir}max-amps-{timestamp}.png"
    plt.savefig(filename, format='png', dpi=300)
    print(f"Saved: {filename}")
