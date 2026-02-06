#!/usr/bin/env python3
import serial
import time
import csv
import sys
import re # Import re for phone number cleaning

if len(sys.argv) < 4:
    print("Usage: write_sim.py /dev/ttyUSBx contacts.csv start_index")
    sys.exit(1)

dev = sys.argv[1]
csvf = sys.argv[2]
start_idx = int(sys.argv[3])  # usually 1

ser = serial.Serial(dev, baudrate=115200, timeout=2)
time.sleep(0.5)

def at(cmd, wait_ok=True):
    """Sends an AT command and returns the list of response lines."""
    ser.write((cmd + "\r").encode())
    resp = []
    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            resp.append(line)
            # Stop reading on final result codes
            if line in ("OK", "ERROR") or line.startswith("+CME") or line.startswith("+CMS"):
                break
        else:
            # Timeout occurred, break the loop
            break
    return resp

# basic sanity check
print("AT ->", at("AT"))

# verify that selecting the SIM phonebook was successful
print('Set phonebook to SIM ->', at('AT+CPBS="SM"'))
# A more robust check would be: enable if you need it.
# pbs_response = at('AT+CPBS="SM"')
# if "OK" not in pbs_response:
#     print("Error: Could not select SIM phonebook. Response:", pbs_response)
#     ser.close()
#     sys.exit(1)

# backup read
print("Reading existing SIM phonebook (1-200):")
print("\n".join(at("AT+CPBR=1,200")))

# iterate CSV and write
with open(csvf, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip header if present
    idx = start_idx
    for row in reader:
        if len(row) < 2:
            continue

        name = row[0].strip()[:14] or "NoName"
        
        # Clean the phone number
        num = row[1].strip()
        # Keep digits and a leading plus sign for international numbers
        cleaned_num = re.sub(r'[^\d+]', '', num)

        # Determine the number type based on the cleaned number
        if cleaned_num.startswith('+'):
            num_type = '129'  # International
        else:
            num_type = '161'  # National

        cmd = f'AT+CPBW={idx},"{cleaned_num}",{num_type},"{name}"'
        resp = at(cmd)
        print(f"{cmd} -> {resp}")
        
        # Check for errors
        joined = " ".join(resp)
        if "ERROR" in joined or "+CME" in joined:
            # More specific error message for a full SIM
            if "Memory full" in joined:
                print("Error: SIM card memory is full. Stopping.")
            else:
                print("Error detected, stopping. Response:", resp)
            break
        idx += 1
        time.sleep(0.25)

ser.close()
print("Done. Restart ModemManager when finished: sudo systemctl restart ModemManager")