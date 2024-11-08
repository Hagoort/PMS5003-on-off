# Example turning pms5003 sensor on/off to extend its lifetime

# The PMS5003 sensor uses laser technology to measure the concentration of particulate matter in the air.
# This laser light has a life span of 30.000 hours, which is about 3.5 years.
# A solution to extend the life span of the PMS5003 is to turn it on and off between readings.
# See https://forum.airgradient.com/t/extending-the-life-span-of-the-pms5003-sensor/114

import logging
import time
from pms5003 import PMS5003, ReadTimeoutError
import serial

# Set up logging
logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info("""Turn the PMS5003 particulate sensor on/off before/after readings to extend its lifetime.

Press Ctrl+C to exit!

""")

# Initialize PMS5003 and UART for controlling power state
pms5003 = PMS5003()
pms5003_uart = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)  # Set the correct UART port if different

# Power on and off functions for PMS5003
def power_on_pms5003():
    pms5003_uart.write([0x42, 0x4D, 0xE4, 0x00, 0x01, 0x01, 0x74])  # Turn on sensor
    logging.info("PMS5003 sensor powered on.")

def power_off_pms5003():
    pms5003_uart.write([0x42, 0x4D, 0xE4, 0x00, 0x00, 0x01, 0x73])  # Turn off sensor
    logging.info("PMS5003 sensor powered off.")

# Function to take readings from the PMS5003
def take_readings():
    global pms5003  # Declare pms5003 as global to allow reassignment
    readings_count = 0
    while readings_count < 30: # Take 30 readings, 1 per second
        try:
            readings = pms5003.read()
            readings_count += 1
            logging.info(f"Reading {readings_count}: {readings}")
            time.sleep(1)  # Wait 1 second between readings
        except ReadTimeoutError:
            logging.warning("Read timeout error. Attempting to reinitialize PMS5003.")
            pms5003 = PMS5003()  # Reinitialize sensor in case of timeout
        except Exception as e:
            logging.warning(f"Unexpected error: {e}")
            # Continue to the next reading

# Function to wait with a countdown
def countdown_sleep(seconds):
    for i in range(seconds, 0, -1):
        logging.info(f"Waiting... {i} seconds remaining")
        time.sleep(1)

try:
    while True:
        # Turn on PMS5003 and take readings for 30 seconds to stabilize and warm-up
        # (Other option after turning on is sleep for 30 seconds to stabilize and warm-up. Hereafter still multiple readings are needed to stabilize)
        power_on_pms5003()
        take_readings()

        # Turn off PMS5003 including its fan
        power_off_pms5003()
        countdown_sleep(270)  # Wait for 270 seconds with countdown before taking next readings. Make this for instance 60 when testing on/off

except KeyboardInterrupt:
    logging.info("Script terminated by user.")
finally:
    # Ensure PMS5003 is turned off when exiting
    power_off_pms5003()
    logging.info("PMS5003 sensor turned off. Exiting.")
