import numpy as np
import matplotlib.pyplot as plt

# Generating mock data for the frequency domain plot
frequencies = np.linspace(0, 300, 300)  # Frequency index (0-300 Hz)
signal_amplitude = np.abs(
    np.random.normal(0, 0.2, len(frequencies))
)  # Base noise level
peaks = (
    np.random.choice([0, 1], size=len(frequencies), p=[0.95, 0.05]) * 
    np.random.uniform(0.8, 1.8, len(frequencies))
)  # Adding distinct peaks across the full range

# Normalizing the amplitude to lie between 0 and 1
zeros_50 = np.zeros((50, ), dtype=int)
random_choice = np.random.choice([0, 1], size=[50, ], p=[0.7, 0.3])
random_choice_filter = np.concatenate((zeros_50, zeros_50, random_choice, zeros_50, zeros_50, zeros_50))
peaks_with_noise = (peaks + np.where(peaks != 0, 1, 0) * signal_amplitude)
random_peaks = peaks_with_noise * random_choice_filter
peaks_normalised = random_peaks / np.max(random_peaks)
print(peaks_with_noise)
print(random_peaks)
print(random_choice)
signal_amplitude += peaks
signal_amplitude_normalized = signal_amplitude / np.max(signal_amplitude)

# Plotting the normalized frequency domain plot
# plt.figure(figsize=(8, 6))
plt.plot(frequencies, signal_amplitude_normalized, linewidth=1, label="Noisy signal")
plt.plot(frequencies, peaks_normalised, linewidth=1.5, label="Filtered signal")
plt.title("Noisy Signal From Sensor With SAWRR Filtering")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Normalized Amplitude")
plt.grid(True)
plt.xlim(0, 300)
plt.ylim(0, 1)  # Normalized amplitude range
plt.legend(loc="upper right")
plt.tight_layout()
# plt.show()
plt.savefig("random_data.png", format="png", dpi=300)
