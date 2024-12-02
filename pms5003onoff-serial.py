# Example turning pms5003 sensor on/off to extend its lifetime

# The PMS5003 sensor uses laser technology to measure the concentration of particulate matter in the air.
# This laser light has a life span of 30.000 hours, which is about 3.5 years.
# A solution to extend the life span of the PMS5003 is to turn it on and off between readings.

import logging
import time
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
pms5003 = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)  # Set the correct port if different

# Power on, off, reset and read functions for PMS5003
def power_on_pms5003():
    pms5003.write([0x42, 0x4D, 0xE4, 0x00, 0x01, 0x01, 0x74])  # Turn on sensor
    logging.info("PMS5003 sensor powered on.")
    
    time.sleep(3)  # Sensor needs some time to turn on
        
    pms5003.reset_input_buffer()  # Clear the buffer to remove any residual data
    logging.info("Clear UART buffer to remove any residual data.")
    
    #time.sleep(1)
    
    pms5003.write([0x42, 0x4D, 0xE2, 0x00, 0x00, 0x01, 0x71])  # Start read or start to continuously produce data by sensor
    logging.info("PMS5003 start sensor read.")

def power_off_pms5003():
    pms5003.write([0x42, 0x4D, 0xE4, 0x00, 0x00, 0x01, 0x73])  # Turn off sensor or switch to sleep mode
    logging.info("PMS5003 sensor powered off.")

def reset_pms5003():
    pms5003.write([0x42, 0x4D, 0xE4, 0x00, 0x00, 0x01, 0x74])  # Reset sensor
    logging.info("PMS5003 sensor reset.")

def read_pms5003():
    try:
        #pms5003.reset_input_buffer()  # Clears the buffer of any old or partial data before each read
        time.sleep(1) # Don't read the data too fast, wait to stabilize data (if needed)
        response = pms5003.read(32)  # Read 32 bytes (adjust as necessary based on your setup)
        logging.info("PMS5003 reading sensor.")

        # Check if the response is valid (length should be 32 bytes)
        if len(response) == 32:
            # Parse the particle readings (assuming the typical data format for PMS5003)
            pm1 = (response[4] << 8) + response[5]
            pm25 = (response[6] << 8) + response[7]
            pm10 = (response[8] << 8) + response[9]
            #temperature = ((response[16] << 8) + response[17]) / 10.0  # Celsius (reserved or unused but possibly internal temperature only for pms5003t not for pms5003)
            #humidity = ((response[18] << 8) + response[19]) / 10.0  # Percent (reserved or unused but possibly humidity only for pms5003t not for pms5003)
            
            print(f"PM1.0: {pm1} µg/m³")
            print(f"PM2.5: {pm25} µg/m³")
            print(f"PM10: {pm10} µg/m³")
            #print(f"Temperature: {temperature} °C") # Internal temperature of the sensor and not the ambient temperature
            #print(f"Humidity: {humidity} %")
        else:
            print("Error: Invalid response length or corrupted data")

    except ReadTimeoutError:
        logging.warning("Read timeout error. Attempting to reinitialize PMS5003.")
        power_on_pms5003()  # Reinitialize sensor in case of timeout
    except RuntimeError as e:
        print('Particle read failed:', e.__class__.__name__)
        reset_pms5003()  # Reset sensor
        time.sleep(30)  # Wait before trying again
    except Exception as e:
        logging.warning(f"Unexpected error: {e}")
        # Continue to the next reading without halting the program

# Function to wait with a countdown
def countdown_sleep(seconds):
    for i in range(seconds, 0, -1):
        logging.info(f"Waiting... {i} seconds remaining")
        time.sleep(1)

try:
    while True:
        # Turn on PMS5003 and take readings for x-seconds
        power_on_pms5003()
        
        # Initialize the reading counter
        readings_count = 0
        
        # Take x number of readings in a loop with 1-second interval between each reading
        for _ in range(100):  # Take x-readings, adjust this based on your needs
            readings_count += 1  # Increment the readings count
            logging.info(f"Reading {readings_count}")  # Log the number of readings taken
            read_pms5003()  # Read the sensor
            #time.sleep(1)
            
        # Turn off PMS5003 including its fan
        power_off_pms5003()       
        countdown_sleep(60)  # Wait x-seconds before taking readings again
        
except KeyboardInterrupt:
    logging.info("Script terminated by user.")
finally:
    # Ensure PMS5003 is turned off when exiting
    power_off_pms5003()
    logging.info("PMS5003 sensor turned off. Exiting.")
