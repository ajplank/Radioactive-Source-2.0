import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import csv

# --- load data ---
time, s1, s2, s3, s4 = [], [], [], [], []
with open('radioactive_sources_1s.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        time.append(float(row['Time [ms]']))
        s1.append(float(row['Source 1']))
        s2.append(float(row['Source 2']))
        s3.append(float(row['Source 3']))
        s4.append(float(row['Source 4']))

time    = np.asarray(time)
sources = [np.asarray(s1), np.asarray(s2), np.asarray(s3), np.asarray(s4)]

# convert ms -> s (optional but helps τ readability)
t = time / 1000.0

# model: N(t) = N0 * exp(-t/τ) + c
def model(x, N0, tau, c):
    return N0 * np.exp(-x / tau) + c

plt.close('all')
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

for i, y in enumerate(sources):
    # Initial guesses: amplitude, time constant, baseline
    N0_guess  = max(y) - min(y)
    tau_guess = (t.max() - t.min()) / 3  # rough scale
    c_guess   = min(y)
    p0 = [N0_guess, tau_guess, c_guess]

    # Poisson weighting (optional but good for counts)
    sigma = np.sqrt(np.clip(y, 1, None))

    popt, pcov = curve_fit(
        model, t, y,
        p0=p0,
        sigma=sigma,
        absolute_sigma=False,       # set True if sigma are absolute, else scales cov by χ²_red
        bounds=([0, 0, -np.inf],    # N0>=0, tau>=0, c free
                [np.inf, np.inf, np.inf])
    )
    perr = np.sqrt(np.diag(pcov))

    N0, tau, c = popt
    N0_err, tau_err, c_err = perr

    # Vectorized RMSE
    yfit = model(t, *popt)
    rmse = np.sqrt(np.mean((y - yfit)**2))

    print(
        f"Source {i+1}:\n"
        f"  N0  = {N0:.3f} ± {N0_err:.3f}\n"
        f"  τ   = {tau:.3f} s ± {tau_err:.3f} s\n"
        f"  c   = {c:.3f} ± {c_err:.3f}\n"
        f"  RMSE = {rmse:.3f}"
    )

    ax = axes[i//2, i%2]
    ax.plot(t, y, 'b.',ms=3, label='Data')
    ax.plot(t, yfit,'-', c='orange',label='Fit')
    ax.set_title(f"Source {i+1}")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Counts")
    ax.legend()

    # === Add τ and its uncertainty onto the plot ===
    tau_text = rf'$\tau = {tau:.3g} \pm {tau_err:.2g}\ \mathrm{{s}}$'
    ax.text(
        0.70, 0.8, tau_text,
        transform=ax.transAxes, ha='left', va='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.85, edgecolor='none'),
        fontsize=11
    )

plt.tight_layout()
plt.show()

