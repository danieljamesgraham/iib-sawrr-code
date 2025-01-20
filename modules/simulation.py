import numpy as np

def init_sim(args):
    """Initialise the simulation."""
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

    x_wg = np.linspace(0, wg_total_length - 1, num_wg_datapoints)
    x_rr = np.linspace(0, args.rr_length, ring_datapoints)

    cfg = {'delta_t': delta_t,
           'num_wg_datapoints': num_wg_datapoints,
           'ring_datapoints': ring_datapoints,
           'ring_roll': ring_roll,
           'window_arr': window_arr,
           'x_wg': x_wg,
           'x_rr': x_rr}

    saw_wg = np.zeros(len(x_wg))
    saw_rr = np.zeros(ring_datapoints)

    return cfg, saw_wg, saw_rr

def iter_sim(args, cfg, saw_wg, saw_rr, i):
    """Perform a single iteration of the simulation."""
    saw_wg = np.sin(2 * np.pi * (cfg['x_wg'] - cfg['delta_t'] * args.wg_vel * i)) * cfg['window_arr']
    saw_rr *= (1 - 0.1 ** args.rr_decay_exp)  # Decay
    saw_rr[:cfg['num_wg_datapoints']] += args.wg2rr_coeff * saw_wg  # Coupling
    saw_rr = np.roll(saw_rr, cfg['ring_roll'])  # Traveling
    return saw_wg, saw_rr
