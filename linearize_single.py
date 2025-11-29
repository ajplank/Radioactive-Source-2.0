import matplotlib.pyplot as plt
import csv
import numpy as np

# --- Configuration ---
FILENAME = 'single_channel_data_3.csv'

# --- Load Data ---
time_list = []
counts_list = []

try:
    with open(FILENAME, mode='r') as file:
        reader = csv.DictReader(file)
        
        # Automatically detect column names
        headers = reader.fieldnames
        time_col = headers[0]  # First column (Time)
        data_col = headers[1]  # Second column (The Channel)
        
        print(f"Plotting '{data_col}' vs '{time_col}'")

        for row in reader:
            time_list.append(float(row[time_col]))
            counts_list.append(float(row[data_col]))

except FileNotFoundError:
    print(f"Error: File '{FILENAME}' not found.")
    exit()

# Convert Time to Seconds (assuming input is ms)
# Remove the "/ 1000.0" if your CSV is already in seconds
t = np.array(time_list) / 1000.0 
y = np.array(counts_list)

# --- Plotting ---
plt.figure(figsize=(10, 6))

# The Magic Command: semilogy
# This plots X on a linear scale and Y on a Log scale
plt.semilogy(t, y, 'b.', markersize=5, label='Raw Data')

# Formatting
plt.title(f"Semi-Log Plot: {data_col}")
plt.xlabel("Time (s)")
plt.ylabel("Counts (Log Scale)")

# Add a grid (Essential for reading log plots)
plt.grid(True, which="both", ls="-", alpha=0.3)
plt.legend()

plt.tight_layout()
plt.show()