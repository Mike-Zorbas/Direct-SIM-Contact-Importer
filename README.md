# Utility scripts for direct .vcf -> SIM
## Overview
This project was a presonal project to resolve a very niche problem
but it could be of use in other instances since the utilities as general. 
*Note this project was created and tested on linux **only***

### Operetion
The `vfc_to_csv.py` utiltiy is used to make a plain listing of the contacts (could be usefull in other instances also)
The `sim_writer.py` uses the /dev/ttyXXXX serial port to send AT commands so to write the contacts on the card (also verifies general integrity as to make operation as safe as possible)

## Dependencies
```toml
requires-python = ">=3.11"
dependencies = [
    "pyserial>=3.5",
    "vobject>=0.9.9",
]
```

## Usage

### Step 1
First covert the .vcf file to csv using:
```bash
python vfc_to_csv.py input.vcf output.csv
```

Then identify the correct serial interface. This step depends on how you are accessing the SIM card.
If your device is connected and running as a modem device you should use mmcli to find your device and then the the serial port.

**Example**
Run to list modem devices `mmcli -L`
Run to get modem info `mmcli -m MODEM_INDEX` *Replace MODEM_INDEX ofcorse*

Look for ttyXXXX interfaces for AT commands *Should have (at) next to the name*

<br>

**🔴 IMPORTANT ! Make sure to stop the ModemManager deamon before executing main script**
```bash
sudo systemctl stop ModemManager
```

**If you are using a SIM to USB adapter**
Things are easier since most adapters just open a serial connection.  
I didn't have one so you have to find it your self how to get the interface
Also check out this project: https://github.com/georgenicolaou/simfor

### Step 2

Run the main script:
```bash
python sim-writer.py /dev/ttyXXXX output.csv 1 # Last argument is the starting index (From the contacts)
```

Make sure to look out for errors because some SIM cards are PIN2 / PUK2 locked this will cause the script to fail.
Also SIM could be Full or Factory Locked so watch out.

