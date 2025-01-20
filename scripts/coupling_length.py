import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("--theta", type=float, required=True)
parser.add_argument("--wavelength", type=float, default=32)
parser.add_argument("--ring-wavelengths", type=int, required=True)
parser.add_argument("--radius-of-curvature", type=float, required=True)
parser.add_argument("--x-shift", type=float, default=0)
args = parser.parse_args()

theta_1 = np.deg2rad(args.theta)
theta_2 = (np.pi - theta_1) / 2

curved_corner_1 = (np.pi - theta_1) * args.radius_of_curvature
curved_corner_2 = (np.pi - theta_2) * args.radius_of_curvature
curved_corners = curved_corner_1 + 2*curved_corner_2
# curved_corners = 2 * np.pi * args.radius_of_curvature
ring_circumference = args.wavelength * args.ring_wavelengths

triangle_corner_1 = 2 * args.radius_of_curvature/np.tan(theta_1/2)
triangle_corner_2 = 2 * args.radius_of_curvature/np.tan(theta_2/2)

triangle_circumference = ring_circumference - curved_corners + triangle_corner_1 + 2*triangle_corner_2
triangle_side_length = triangle_circumference / (2 * (1 + np.sin(theta_1/2)))

central_length = 2 * args.x_shift * np.tan(theta_1/2)

coupling_length = triangle_side_length - triangle_corner_1/2 - triangle_corner_2/2 - central_length / (1 + np.sin(theta_1/2))
coupling_wavelengths = coupling_length / args.wavelength

# check = triangle_opposite_side_length + 2 * triangle_side_length + 2 * np.pi * args.radius_of_curvature
# print(check)

print(f"Coupling wavelengths: {round(coupling_wavelengths,3)}")

if args.verbose:
    print(f"Coupling length: {round(coupling_length,3)} (arb.)")
    print(f"Curved corner 1: {round(curved_corner_1,3)} (arb.)")
    print(f"Curved corner 2: {round(curved_corner_2,3)} (arb.)")
    print(f"Curved corners: {round(curved_corners,3)} (arb.)")
    print(f"Ring circumference: {round(ring_circumference,3)} (arb.)")
    print(f"Triangle corner 1: {round(triangle_corner_1,3)} (arb.)")
    print(f"Triangle corner 2: {round(triangle_corner_2,3)} (arb.)")
    print(f"Triangle circumference: {round(triangle_circumference,3)} (arb.)")
    print(f"Triangle side length: {round(triangle_side_length,3)} (arb.)")
    print(f"Central length: {round(central_length,3)} (arb.)")
