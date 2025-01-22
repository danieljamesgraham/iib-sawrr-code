import numpy as np

def init_sim(args, wg_length):
    """Initialise the simulation."""

    delta_t = 1 / args.fps

    # Update iteration counter if in animation mode (as it is slow)
    print_iter_sim = False
    if args.mode == "animation":
        print_iter_sim = True

    # Calculate array velocity
    wg_roll = int(delta_t * args.datapoint_density * args.wg_vel)
    rr_roll = int(delta_t * args.datapoint_density * args.rr_vel)

    wg_total_length = wg_length + args.wg_edge_length

    # Calculate number of datapoints in different lengths
    num_wg_mid_datapoints = int(round(wg_length * args.datapoint_density))
    num_wg_edge_datapoints = int(round(args.wg_edge_length * args.datapoint_density))
    half_num_wg_edge_datapoints = num_wg_edge_datapoints // 2
    num_wg_datapoints = int(round(wg_total_length * args.datapoint_density))
    num_gen_datapoints = half_num_wg_edge_datapoints + wg_roll
    num_rr_datapoints = int(round(args.rr_length * args.datapoint_density))

    # Create window array to emulate the decrease in SAW coupling at edges of coupling region
    window = np.concatenate((
        0.5 * (1 + np.sin(np.linspace(-np.pi/2, np.pi/2, half_num_wg_edge_datapoints))),
        np.ones(num_wg_mid_datapoints),
        0.5 * (1 - np.sin(np.linspace(-np.pi/2, np.pi/2, half_num_wg_edge_datapoints)))
    ))

    # Create position arrays
    x_wg = np.linspace(0, wg_total_length , num_wg_datapoints, endpoint=False)
    x_gen = x_wg[0:num_gen_datapoints]
    x_rr = np.linspace(0, args.rr_length, num_rr_datapoints, endpoint=False)

    # Create config dictionary
    cfg = {'delta_t': delta_t,
           'print_iter_sim': print_iter_sim,
           'num_wg_datapoints': num_wg_datapoints,
           'half_num_wg_edge_datapoints': half_num_wg_edge_datapoints,
           'num_rr_datapoints': num_rr_datapoints,
           'wg_roll': wg_roll,
           'rr_roll': rr_roll,
           'window': window,
           'x_wg': x_wg,
           'x_gen': x_gen,
           'x_rr': x_rr}

    # Initialise SAWs
    saw_wg = np.zeros(num_wg_datapoints)
    saw_rr = np.zeros(num_rr_datapoints)

    return cfg, saw_wg, saw_rr

def iter_sim(args, cfg, saw_wg, saw_rr, i):
    """Perform a single iteration of the simulation."""

    # Update iteration counter if in animation mode (as it is slow)
    if cfg["print_iter_sim"]:
        print_iter(i, args.iterations, args.print_freq)

    # Gradually introduce SAW into input waveguide at same rate as SAW velocity
    if i * cfg['wg_roll'] < len(cfg['x_gen']):
        saw_wg[:i*cfg['wg_roll']] = np.sin(2 * np.pi * (cfg['x_gen'][:i*cfg['wg_roll']] - cfg['delta_t'] * args.wg_vel * i))  # SAW generation
    else:
        saw_wg[:len(cfg['x_gen'])] = np.sin(2 * np.pi * (cfg['x_gen'] - cfg['delta_t'] * args.wg_vel * i))  # SAW generation

    # Apply window array
    saw_wg *= cfg['window']

    # WG to RR SAW coupling and loss
    saw_rr[:cfg['num_wg_datapoints']] += args.wg2rr_coupl * saw_wg[:cfg['num_wg_datapoints']]  # Coupling
    if not args.no_loss:
        saw_wg[:cfg['num_wg_datapoints']] -= args.wg2rr_loss * saw_wg[:cfg['num_wg_datapoints']]  # Loss

    # RR to WG SAW coupling and loss
    if not args.no_rr2wg:
        saw_wg[:cfg['num_wg_datapoints']] += args.rr2wg_coupl * saw_rr[:cfg['num_wg_datapoints']]  # Coupling
        if not args.no_loss:
            saw_rr[:cfg['num_wg_datapoints']] -= args.rr2wg_loss * saw_rr[:cfg['num_wg_datapoints']]  # Coupling

    # Travelling SAW
    saw_wg = np.roll(saw_wg, cfg['wg_roll'])
    saw_rr = np.roll(saw_rr, cfg['rr_roll'])

    # SAW decay
    saw_wg *= (1 - 0.1 ** args.wg_decay_exp)
    saw_rr *= (1 - 0.1 ** args.rr_decay_exp)

    return saw_wg, saw_rr

def print_iter( i, total_i, print_freq):
    """Print the current iteration number"""

    if (i % print_freq == print_freq - 1) and ((i+1 == total_i) or (i+1 > total_i-print_freq)):
        print(f"\rProgress: {i+1}/{total_i}", end="\n")  # Final iteration; newline
    elif i % print_freq == print_freq - 1:
        print(f"\rProgress: {i+1}/{total_i}", end="")
