import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import csv

# --- Configuration ---
CSV_FILENAME = 'serial_5_channels.csv' # Matches your Arduino logger script

# --- Load Data ---
time_list, s1, s2, s3, s4 = [], [], [], [], []

try:
    with open(CSV_FILENAME, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # We assume the Arduino logger saved columns as:
            # Time, Channel 1, Channel 2, Channel 3, Channel 4
            time_list.append(float(row['Time']))
            s1.append(float(row['Channel 1']))
            s2.append(float(row['Channel 2']))
            s3.append(float(row['Channel 3']))
            s4.append(float(row['Channel 4']))
except FileNotFoundError:
    print(f"Error: Could not find file '{CSV_FILENAME}'. Check directory.")
    exit()

# Convert to numpy arrays
raw_time = np.asarray(time_list)
sources  = [np.asarray(s1), np.asarray(s2), np.asarray(s3), np.asarray(s4)]

# --- Time Conversion ---
# Convert ms -> s (This makes Tau readable in seconds)
t = raw_time / 1000.0

# --- Model Definition ---
# N(t) = N0 * exp(-t/tau) + c
# tau = mean lifetime (seconds)
def model(x, N0, tau, c):
    return N0 * np.exp(-x / tau) + c

# --- Plotting Setup ---
plt.close('all')
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f"Radioactive Decay Fits (Data: {CSV_FILENAME})", fontsize=16)

for i, y in enumerate(sources):
    
    # 1. Intelligent Guesses
    # N0 = Range of data, c = minimum value, tau = 1/3 of total duration
    N0_guess  = max(y) - min(y)
    c_guess   = min(y)
    tau_guess = (t.max() - t.min()) / 3 if (t.max() - t.min()) > 0 else 1.0
    
    p0 = [N0_guess, tau_guess, c_guess]

    # 2. Weighting (Poisson Statistics)
    # Uncertainties in counts are sqrt(N). We use this to weight the fit.
    # We clip at 1 to avoid division by zero errors if counts are 0.
    sigma = np.sqrt(np.clip(y, 1, None))

    try:
        popt, pcov = curve_fit(
            model, t, y,
            p0=p0,
            sigma=sigma,
            absolute_sigma=True,          # True = treat sigma as absolute errors (counts)
            bounds=([0, 0, -np.inf],      # N0 >= 0, tau >= 0, c can be anything
                    [np.inf, np.inf, np.inf])
        )
        
        perr = np.sqrt(np.diag(pcov))
        N0, tau, c = popt
        N0_err, tau_err, c_err = perr

        # Calculate RMSE
        yfit = model(t, *popt)
        rmse = np.sqrt(np.mean((y - yfit)**2))

        print(f"--- Source {i+1} ---")
        print(f"  N0   = {N0:.3f} +/- {N0_err:.3f}")
        print(f"  Tau  = {tau:.3f} s +/- {tau_err:.3f} s")
        print(f"  c    = {c:.3f} +/- {c_err:.3f}")
        print(f"  RMSE = {rmse:.3f}\n")

        # 3. Plotting
        ax = axes[i//2, i%2]
        
        # Plot Data
        ax.plot(t, y, 'b.', ms=4, alpha=0.4, label='Data')
        
        # Plot Fit
        ax.plot(t, yfit, '-', color='orange', linewidth=2, label='Fit')

        # Add Annotation Box
        tau_text = rf'$\tau = {tau:.3f} \pm {tau_err:.3f}\ \mathrm{{s}}$'
        ax.text(
            0.95, 0.95, tau_text,
            transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'),
            fontsize=10
        )

    except Exception as e:
        print(f"Fit failed for Source {i+1}: {e}")
        ax = axes[i//2, i%2]
        ax.plot(t, y, 'b.', label='Data (Fit Failed)')

    ax.set_title(f"Channel {i+1}")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Counts")
    ax.legend(loc='upper right', bbox_to_anchor=(1, 0.85)) # Move legend slightly to avoid overlap

plt.tight_layout()
plt.show()