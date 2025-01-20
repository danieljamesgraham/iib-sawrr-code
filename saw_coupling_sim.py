import argparse
from modules.simulation import init_sim, iter_sim
from modules.animation import run_anim

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulates coupling of SAWs between an input waveguide and a ring resonator.")
    parser.add_argument("mode", type=str, choices=["animation"], help="Mode to run the simulation.")
    parser.add_argument("--iterations", type=int, default=1000, help="Number of simulation iterations.")
    parser.add_argument("--datapoint-density", type=int, default=100, help="Number of datapoints per unit length.")
    parser.add_argument("--fps", type=int, default=25, help="Frames per second for animation.")
    parser.add_argument("--wg-length", type=float, default=1, help="Waveguide length.")
    parser.add_argument("--wg-edge-length", type=float, default=1, help="Waveguide edge length.")
    parser.add_argument("--wg-vel", type=float, default=2, help="Waveguide SAW velocity.")
    parser.add_argument("--rr-length", type=float, default=15, help="Ring resonator length.")
    parser.add_argument("--rr-vel", type=float, default=1.5, help="Ring resonator velocity (ratio).")
    parser.add_argument("--wg2rr-coeff", type=float, default=0.05, help="Coupling coefficient from waveguide to resonator.")
    parser.add_argument("--rr-decay-exp", type=float, default=3, help="Resonator decay exponent.")

    args = parser.parse_args()

    if args.datapoint_density % 2 != 0:
        raise ValueError("Datapoint density must be an even integer.")

    cfg, saw_wg, saw_rr = init_sim(args)

    if args.mode == "animation":
        run_anim(args, cfg, saw_wg, saw_rr)
