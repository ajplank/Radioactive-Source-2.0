import matplotlib.pyplot as plt
import csv
import numpy as np
import os

# --- Configuration ---
# This will loop through single_channel_data_1.csv to _4.csv
FILE_INDICES = range(1, 5) 

# --- Plotting Setup ---
# Create a 2x2 grid of plots
plt.close('all') # Close previous windows
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle("Individual Semi-Log Decay Plots", fontsize=16)

# Flatten the 2x2 matrix of axes into a simple list [ax1, ax2, ax3, ax4]
ax_list = axes.flatten()

# --- Main Loop ---
for i in FILE_INDICES:
    filename = f'single_channel_data_{i}.csv'
    current_ax = ax_list[i-1] # Map file 1 to index 0, etc.
    
    # --- Load Data ---
    time_list = []
    counts_list = []
    
    if not os.path.exists(filename):
        # Handle missing files gracefully on the plot
        current_ax.text(0.5, 0.5, f"{filename}\nNot Found", 
                        ha='center', va='center', transform=current_ax.transAxes)
        print(f"Skipping {filename} (Not Found)")
    else:
        try:
            with open(filename, mode='r') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                
                # Auto-detect columns
                if headers and len(headers) >= 2:
                    time_col = headers[0]
                    data_col = headers[1] 

                    for row in reader:
                        try:
                            time_list.append(float(row[time_col]))
                            counts_list.append(float(row[data_col]))
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    # --- Plotting ---
    if time_list:
        # Convert Time to Seconds (assuming input is ms)
        t = np.array(time_list) / 1000.0 
        y = np.array(counts_list)

        # The Magic Command for Subplots: current_ax.semilogy
        current_ax.semilogy(t, y, '.', markersize=4, alpha=0.5, color='blue')
        
        # Add 'Grid' to make it easier to read the log scale
        current_ax.grid(True, which="both", ls="-", alpha=0.3)
    
    # --- Subplot Formatting ---
    current_ax.set_title(f"Channel {i}")
    current_ax.set_xlabel("Time (s)")
    current_ax.set_ylabel("Counts (Log Scale)")

# Adjust layout so titles and labels don't overlap
plt.tight_layout()
plt.subplots_adjust(top=0.92) # Leave space for the main super-title
plt.show()