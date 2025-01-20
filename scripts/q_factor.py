import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-n", "--n-wavelengths", type=int, required=True)
parser.add_argument("-l", "--wavelength", type=float, required=True)
parser.add_argument("-w", "--ring-width", type=float, required=True)
parser.add_argument("-c", "--velocity", type=float, default=0)
args = parser.parse_args()

central_frequency_factor = 1 / (args.wavelength*1e-6)
upper_frequency_factor = args.n_wavelengths / (args.n_wavelengths*args.wavelength*1e-6 - np.pi*args.ring_width*1e-6)
lower_frequency_factor = args.n_wavelengths / (args.n_wavelengths*args.wavelength*1e-6 + np.pi*args.ring_width*1e-6)
delta_frequency_factor = upper_frequency_factor - lower_frequency_factor

# Scaled using 0.5(1+cos(2 pi x / delta_f)) at 3db (sqrt(2)) point
scaled_delta_frequency_factor = delta_frequency_factor * np.arccos(np.sqrt(2) - 1) / np.pi 

scaled_q_factor = central_frequency_factor / scaled_delta_frequency_factor
q_factor = central_frequency_factor / delta_frequency_factor

central_frequency = central_frequency_factor * args.velocity

upper_frequency = upper_frequency_factor * args.velocity
lower_frequency = lower_frequency_factor * args.velocity
delta_frequency = delta_frequency_factor * args.velocity

scaled_delta_frequency = scaled_delta_frequency_factor * args.velocity
scaled_upper_frequency = central_frequency + scaled_delta_frequency/2
scaled_lower_frequency = central_frequency - scaled_delta_frequency/2

print("Q factors:")
print(f"- Worst-case: {round(q_factor, 3)}")
print(f"- Scaled: {round(scaled_q_factor, 3)}")
if args.verbose:
    if args.velocity == 0:
        print("Provide an acoustic wave velocity!")
    else:
        print(f"\nCentral frequency: {round(central_frequency*1e-6, 3)} (MHz)")
        print("\nWorst-case frequencies:")
        print(f"- Upper frequency: {round(upper_frequency*1e-6, 3)} (MHz)")
        print(f"- Lower frequency: {round(lower_frequency*1e-6, 3)} (MHz)")
        print(f"- Delta frequency: {round(delta_frequency*1e-6, 3)} (MHz)")
        print("\nScaled frequencies:")
        print(f"- Upper frequency: {round(scaled_upper_frequency*1e-6, 3)} (MHz)")
        print(f"- Lower frequency: {round(scaled_lower_frequency*1e-6, 3)} (MHz)")
        print(f"- Delta frequency: {round(scaled_delta_frequency*1e-6, 3)} (MHz)")
