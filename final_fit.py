import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import csv
import os

# --- 1. USER CONFIGURATION ---
# Options: 'single' or 'double'
FIT_TYPES = {
    1: 'single',
    2: 'single',
    3: 'double',
    4: 'double'
}

# CSV settings
COL_TIME = 'Time'
COL_SIGNAL = 'Signal' 

# Constants
LN2 = np.log(2)

# --- 2. Model Definitions ---

# Single: N(t) = A * exp(-t/tau) + c
def model_single(t, A, tau, c):
    return A * np.exp(-t / tau) + c

# Double: N(t) = A1 * exp(-t/tau1) + A2 * exp(-t/tau2) + c
def model_double(t, A1, tau1, A2, tau2, c):
    return A1 * np.exp(-t / tau1) + A2 * np.exp(-t / tau2) + c

# --- 3. Plotting Setup ---
plt.close('all')
fig, axes = plt.subplots(2, 2, figsize=(14, 11)) # Slightly taller for extra text
fig.suptitle("Radioactive Decay Analysis (Half-Life & Abundance)", fontsize=16)
ax_list = axes.flatten()

# --- 4. Main Loop ---
for i in range(1, 5):
    
    filename = f'single_channel_data_{i}.csv'
    current_ax = ax_list[i-1]
    fit_type = FIT_TYPES[i]
    
    print(f"\n{'='*40}")
    print(f"Processing File {i}: {filename} ({fit_type} fit)")
    print(f"{'='*40}")

    # --- A. Load Data ---
    time_list, signal_list = [], []
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        current_ax.text(0.5, 0.5, "File Not Found", ha='center')
        continue

    try:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                time_list.append(float(row[COL_TIME]))
                # Fallback if specific column name is missing
                try:
                    signal_list.append(float(row[COL_SIGNAL]))
                except KeyError:
                    signal_list.append(float(row[list(row.keys())[1]]))
    except Exception as e:
        print(f"Error reading file: {e}")
        continue

    # Normalization
    t = np.array(time_list) / 1000.0 # ms to s
    y = np.array(signal_list)
    
    # Weights for fitting
    sigma = np.sqrt(np.clip(y, 1, None))

    # --- B. Fitting & Calculations ---
    try:
        amp_span = max(y) - min(y)
        c_guess = min(y)
        duration = t.max() - t.min()

        if fit_type == 'single':
            # --- Single Fit ---
            p0 = [amp_span, duration/3, c_guess]
            bounds = ([0, 0, -np.inf], [np.inf, np.inf, np.inf])
            
            popt, pcov = curve_fit(model_single, t, y, p0=p0, sigma=sigma, absolute_sigma=True, bounds=bounds)
            
            A, tau, c = popt
            perr = np.sqrt(np.diag(pcov))
            tau_err = perr[1]
            
            # Calculations
            t_half = tau * LN2
            t_half_err = tau_err * LN2
            
            yfit = model_single(t, *popt)
            
            # Print Info
            print(f"  > Tau       : {tau:.4f} +/- {tau_err:.4f} s")
            print(f"  > Half-Life : {t_half:.4f} +/- {t_half_err:.4f} s")
            print(f"  > Abundance : 100%")

            # Graph Label
            label_text = (rf'$T_{{1/2}} = {t_half:.3f} \pm {t_half_err:.3f}$ s' + '\n' +
                          r'(Abundance: 100%)')

        elif fit_type == 'double':
            # --- Double Fit ---
            p0 = [amp_span/2, duration/10, amp_span/2, duration/2, c_guess]
            bounds = ([0, 0, 0, 0, -np.inf], [np.inf, np.inf, np.inf, np.inf, np.inf])
            
            popt, pcov = curve_fit(model_double, t, y, p0=p0, sigma=sigma, absolute_sigma=True, bounds=bounds)
            
            A1, tau1, A2, tau2, c_val = popt
            perr = np.sqrt(np.diag(pcov))
            
            # Calculations (Half Lives)
            t1_half = tau1 * LN2
            t1_half_err = perr[1] * LN2
            
            t2_half = tau2 * LN2
            t2_half_err = perr[3] * LN2
            
            # Calculations (Abundance)
            total_amp = A1 + A2
            abund1 = (A1 / total_amp) * 100
            abund2 = (A2 / total_amp) * 100

            yfit = model_double(t, *popt)
            
            # Print Info
            print(f"  --- Component 1 (Fast?) ---")
            print(f"  > Tau       : {tau1:.4f} +/- {perr[1]:.4f} s")
            print(f"  > Half-Life : {t1_half:.4f} +/- {t1_half_err:.4f} s")
            print(f"  > Abundance : {abund1:.1f}%")
            print(f"  --- Component 2 (Slow?) ---")
            print(f"  > Tau       : {tau2:.4f} +/- {perr[3]:.4f} s")
            print(f"  > Half-Life : {t2_half:.4f} +/- {t2_half_err:.4f} s")
            print(f"  > Abundance : {abund2:.1f}%")

            # Graph Label (Compacted for space)
            label_text = (rf'$T_{{1/2,1}} = {t1_half:.2f} \pm {t1_half_err:.2f}$ s ({abund1:.0f}%)' + '\n' + 
                          rf'$T_{{1/2,2}} = {t2_half:.2f} \pm {t2_half_err:.2f}$ s ({abund2:.0f}%)')

        # --- C. Plotting ---
        rmse = np.sqrt(np.mean((y - yfit)**2))
        print(f"  > RMSE      : {rmse:.3f}")

        current_ax.plot(t, y, 'b.', alpha=0.3, markersize=3, label='Data')
        current_ax.plot(t, yfit, 'r-', linewidth=1.5, label='Fit')
        
        # Annotation Box
        current_ax.text(0.95, 0.95, label_text, transform=current_ax.transAxes, 
                        ha='right', va='top', fontsize=9,
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))
        
        current_ax.legend(loc='upper right', bbox_to_anchor=(1, 0.78))

    except Exception as e:
        print(f"  Fit Failed: {e}")
        current_ax.plot(t, y, 'k.', label='Data (Fit Failed)')

    # Aesthetics
    current_ax.set_title(f"File {i}: {fit_type.capitalize()} Fit")
    current_ax.set_xlabel("Time (s)")
    current_ax.set_ylabel("Counts")

plt.tight_layout()
plt.show()