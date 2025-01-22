import argparse

from modules.simulation import init_sim, iter_sim
from modules.animation import run_anim
from modules.maximum_amplitude import run_max_amps

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulates coupling of SAWs between an input waveguide and a ring resonator.")

    # Simulation modes
    parser.add_argument("mode", type=str, choices=["animation", "maximum-amplitudes"], help="Mode to run the simulation.")

    # Debugging
    parser.add_argument("--output-dir", type=str, default='outputs/saw_coupling_sim/', help="Path to output directory.")
    parser.add_argument('--dry-run', action='store_true', help='Initialise simulation but do not run it.')
    parser.add_argument('--no-rr2wg', action='store_true', help='Disable waveguide to RR SAW coupling.')
    parser.add_argument('--no-loss', action='store_true', help='Disable loss due to SAW coupling.')

    # Simulation configuration
    parser.add_argument("--iterations", type=int, default=1000, help="Number of simulation iterations.")
    parser.add_argument("--datapoint-density", type=int, default=100, help="Number of datapoints per unit length.")
    parser.add_argument("--fps", type=int, default=25, help="Frames per second for animation.")
    parser.add_argument("--print-freq", type=int, default=10, help="Number of iterations after which counter is updated.")

    # Input properties
    parser.add_argument("--wg-length", type=float, default=1, help="Waveguide length.")
    parser.add_argument("--wg-edge-length", type=float, default=1, help="Waveguide edge length.")
    parser.add_argument("--wg-vel", type=float, default=2, help="Waveguide SAW velocity.")
    parser.add_argument("--wg2rr-coupl", type=float, default=0.01, help="Coupling coefficient from waveguide to resonator.")
    parser.add_argument("--wg2rr-loss", type=float, default=0.02, help="Loss coefficient from waveguide to resonator.")
    parser.add_argument("--wg-decay-exp", type=float, default=3, help="Resonator decay exponent.")

    # Ring resonator properties
    parser.add_argument("--rr-length", type=float, default=15, help="Ring resonator length.")
    parser.add_argument("--rr-vel", type=float, default=2, help="Ring resonator velocity.")
    parser.add_argument("--rr2wg-coupl", type=float, default=0.01, help="Coupling coefficient from waveguide to resonator.")
    parser.add_argument("--rr2wg-loss", type=float, default=0.02, help="Loss coefficient from waveguide to resonator.")
    parser.add_argument("--rr-decay-exp", type=float, default=3, help="Resonator decay exponent.")

    # Maxmimum-amplitudes mode
    parser.add_argument("--min-wg-length", type=float, default=0, help="Minimum waveguide length.")
    parser.add_argument("--max-wg-length", type=float, default=7.5, help="Maximum waveguide length.")
    parser.add_argument("--step-wg-length", type=float, default=0.1, help="Waveguide length step.")

    args = parser.parse_args()

    # Check that datapoint-density is even as it is halved in simulation logic
    if args.datapoint_density % 2 != 0:
        raise ValueError("Datapoint density must be an even integer.")

    # Run simulation in appropriate mode
    if args.mode == "animation":
        run_anim(args)
    if args.mode == "maximum-amplitudes":
        # --datapoint-density 5000 --step-wg-length 0.2 gives nice figures here
        run_max_amps(args)
