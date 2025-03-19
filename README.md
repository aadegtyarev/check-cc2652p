# check_cc2652p

A Python script for communicating with Texas Instruments Zigbee modules (CC2652, CC2530, CC2538) over UART. It can parse the module's version information and identify its compatibility with Z-Stack.

## Features
- Detects and parses version responses for Zigbee modules.
- Checks if the serial port is occupied and provides recommendations.
- Supports sending custom commands in hexadecimal format.
- Debugging mode for detailed logs.

## Requirements
- Python 3.6 or newer.
- A compatible Zigbee module connected via UART.
- Dependencies specified in `requirements.txt`.

## Installation  
### For Wiren Board Controllers 
1. Download the script directly to your controller: 
    ```bash
    wget https://raw.githubusercontent.com/aadegtyarev/check-cc2652p/refs/heads/main/src/check_cc2652p.py
    ```

2. Run the script without additional setup, as all dependencies are pre-installed on Wiren Board:     
    ```
    python3 ./check_cc2652p.py /dev/ttyMOD4
    ```   

### For Other Systems

1. Ensure you have Git and Python 3 installed on your system. Install Git if needed:   
   
    ```
    sudo apt update && sudo apt install -y git
    ```
    
2. Clone the repository:        
    ```
    git clone https://github.com/aadegtyarev/check-cc2652p.git cd check-cc2652p
    ```
    
3. Install the required dependencies:        
    ```
    pip install -r requirements.txt    
    ```
    
4. Run the script:        
    ```
    python3 ./src/check_cc2652p.py /dev/your-port
    ```

## Usage

### Help

Check the version of a connected Zigbee module:

```
python3 src/check_cc2652p.py --help
```

Help:
```
usage: check_cc2652p.py [-h] [--baudrate BAUDRATE] [--reset] [--version] [--timeout TIMEOUT] [--custom-command CUSTOM_COMMAND] [--debug] port

Check the version, reset or send custom command to the CC2652P, CC2530, or CC2538 Zigbee module over UART.

positional arguments:
  port                  Serial port where the Zigbee module is connected (e.g., /dev/ttyMOD4).

optional arguments:
  -h, --help            show this help message and exit
  --baudrate BAUDRATE   Baud rate for serial communication (default: 115200).
  --reset               Send reset command to the module.
  --version             Send version request to the module.
  --timeout TIMEOUT     Timeout for waiting for a response (in seconds, default: 1).
  --custom-command CUSTOM_COMMAND
                        Send a custom command to the module in hex format (e.g., 'fe01210100').
  --debug               Enable debug output.
```

### Basic Usage

Check the version of a connected Zigbee module:

```
python3 src/check_cc2652p.py /dev/ttyMOD4
```

### Reset the module

Send a reset command to the module:

```
python3 src/check_cc2652p.py /dev/ttyMOD4 --reset
```

### Send a custom command

Send a custom hexadecimal command:

```
python3 src/check_cc2652p.py /dev/ttyMOD4 --custom-command fe01210100
```

### Enable debugging

Use `--debug` to see detailed logs:

```
python3 src/check_cc2652p.py /dev/ttyMOD4 --debug
```

### Timeout Configuration

Specify a custom timeout (in seconds):

```
python3 src/check_cc2652p.py /dev/ttyMOD4 --timeout 2
```
