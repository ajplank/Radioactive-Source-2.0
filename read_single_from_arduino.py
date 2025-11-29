# -*- coding: utf-8 -*-
"""
Serial Logger (Time + Single Selectable Channel)
"""

import serial
import csv
import time
import sys

# --- Configuration ---
SERIAL_PORT = 'COM11'       # Change to your board's port
BAUD_RATE = 9600            # Match your device's baud rate
CSV_FILENAME = 'single_channel_data_3.csv'

# WHICH CHANNEL DO YOU WANT? (Range: 1 - 4)
SELECTED_CHANNEL = 3      

# Logging Interval
LOG_INTERVAL_SECONDS = 1

def log_serial_data_to_csv(port, baud_rate, filename, channel_num):
    # Basic validation to ensure channel is valid
    if channel_num < 1 or channel_num > 4:
        print("Error: SELECTED_CHANNEL must be an integer between 1 and 4.")
        sys.exit()

    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        ser.reset_input_buffer()
        print(f" Connected to {port} @ {baud_rate} baud.")

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # --- Dynamic Header ---
            # Creates headers like: ['Time', 'Channel 2']
            writer.writerow(['Time', f'Channel {channel_num}'])

            print(f"Logging Time and Channel {channel_num} to {filename}. Press Ctrl+C to stop.")

            while True:
                raw_line = ser.readline().decode(errors='ignore').strip()

                if raw_line:
                    cols = raw_line.split()

                    # We need at least 5 columns to be safe 
                    # (Time, Ch1, Ch2, Ch3, Ch4)
                    if len(cols) >= 5:
                        
                        # Column 0 is always Time
                        time_val = cols[0]
                        
                        # Since cols[1] is Ch1, cols[2] is Ch2...
                        # The index matches your channel_num exactly.
                        channel_val = cols[channel_num]
                        
                        data_row = [time_val, channel_val]
                        
                        writer.writerow(data_row)
                        csvfile.flush()
                        print(f"Logged: {data_row}")
                    else:
                        print(f"Ignored incomplete line: {cols}")

                if LOG_INTERVAL_SECONDS > 0:
                    time.sleep(LOG_INTERVAL_SECONDS)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        print("Tip: Check COM port and close Arduino Serial Monitor.")
    except KeyboardInterrupt:
        print("\nLogging stopped by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print(" Serial port closed.")

if __name__ == "__main__":
    log_serial_data_to_csv(SERIAL_PORT, BAUD_RATE, CSV_FILENAME, SELECTED_CHANNEL)