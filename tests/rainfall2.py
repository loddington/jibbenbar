import RPi.GPIO as GPIO
import time
from datetime import datetime

# Set GPIO pin mode to BCM
GPIO.setmode(GPIO.BCM)

# Define GPIO pin 6 as an input
pin = 19
# GPIO.setup(pin, GPIO.IN)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)



# Function to handle rain gauge tip events
def rain_gauge_tip(channel):
    # Get the current date and time in human-readable format
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Open the log file in append mode
    with open("/tmp/rain_gauge_log.txt", "a") as f:
        # Write the date and time to the log file
        f.write(f"{current_time} - Rain gauge tip detected\n")

# Attach an interrupt to GPIO pin 6 and call the rain_gauge_tip function
# on a rising edge
GPIO.add_event_detect(pin, GPIO.RISING, callback=rain_gauge_tip, bouncetime=1000)

# Keep the script running indefinitely
while True:
    time.sleep(0.5)
