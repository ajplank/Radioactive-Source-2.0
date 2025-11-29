# -*- coding: utf-8 -*-
"""
Serial Logger (5 Columns: Time + 4 Channels)
"""

import serial
import csv
import time

# --- Configuration ---
SERIAL_PORT = 'COM11'       # Change to your board's port
BAUD_RATE = 9600            # Match your device's baud rate
CSV_FILENAME = 'serial_5_channels.csv'
# NOTE: If your Arduino sends data faster than this interval, 
# decrease this number (e.g., 0.1) or set to 0 to prevent lag.
LOG_INTERVAL_SECONDS = 1  

def log_serial_data_to_csv(port, baud_rate, filename):
    try:
        # Open Serial Connection
        ser = serial.Serial(port, baud_rate, timeout=1)
        # Clear any old data sitting in the buffer
        ser.reset_input_buffer() 
        print(f" Connected to {port} @ {baud_rate} baud.")

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # --- CHANGE 1: Updated Headers ---
            # Labels for the 5 columns coming from Arduino
            writer.writerow(['Time', 'Channel 1', 'Channel 2', 'Channel 3', 'Channel 4'])

            print(f"Logging to {filename}. Press Ctrl+C to stop.")

            while True:
                # Read a line from the serial port
                raw_line = ser.readline().decode(errors='ignore').strip()

                if raw_line:
                    # Split the line by whitespace (tabs or spaces)
                    cols = raw_line.split()

                    # --- CHANGE 2: Capture 5 Columns ---
                    # Ensure we have at least 5 columns of data
                    if len(cols) >= 5:
                        # Slice 0:5 gets the first 5 items (Time + 4 Channels)
                        data_row = cols[0:5]
                        
                        writer.writerow(data_row)
                        csvfile.flush() # Ensure data is written immediately
                        print(f"Logged: {data_row}")
                    else:
                        print(f"Ignored incomplete line: {cols}")

                # Optional delay (be careful: too long causes buffer overflow)
                if LOG_INTERVAL_SECONDS > 0:
                    time.sleep(LOG_INTERVAL_SECONDS)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        print("Tip: Check that the COM port is correct and no other program (like Arduino IDE) is using it.")
    except KeyboardInterrupt:
        print("\nLogging stopped by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print(" Serial port closed.")

if __name__ == "__main__":
    # Ensure pyserial is installed before running:
    # pip install pyserial
    log_serial_data_to_csv(SERIAL_PORT, BAUD_RATE, CSV_FILENAME)