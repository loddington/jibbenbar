import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta

# Pin definitions
RELAY_PIN = 14
BUTTON_PIN = 24
WATER_LEVEL_SENSOR_PIN = 11
REFILL_HOUR = 10
REFILL_MIN = 0
MAX_RUN_TIME = 360  # Maximum run time in seconds just in case the water sensor fails

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(WATER_LEVEL_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initial states
relay_state = False
pump_start_time = None

def button_callback(channel):
    global relay_state, pump_start_time
    if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Button pressed
        # Check the water level before toggling the relay
        if GPIO.input(WATER_LEVEL_SENSOR_PIN) == GPIO.LOW:  # Water level is not high
            relay_state = not relay_state
            if relay_state:
                pump_start_time = datetime.now()
                GPIO.output(RELAY_PIN, GPIO.LOW)
                print("Relay ON")
            else:
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                pump_start_time = None
                print("Relay OFF")
        else:
            print("Water level high - Cannot turn on the relay")

def water_level_callback(channel):
    global relay_state, pump_start_time
    if GPIO.input(WATER_LEVEL_SENSOR_PIN) == GPIO.HIGH:  # Water level high
        relay_state = False
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        pump_start_time = None
        print("Water level high - Relay OFF")

def check_time_and_start_pump():
    global relay_state, pump_start_time
    now = datetime.now()
    if now.hour == REFILL_HOUR and now.minute == REFILL_MIN:
        # Attempt to start the pump if water level is not high
        if GPIO.input(WATER_LEVEL_SENSOR_PIN) == GPIO.LOW:  # Water level is not high
            relay_state = True
            pump_start_time = now
            GPIO.output(RELAY_PIN, GPIO.LOW)
            print("Attempting to start the pump relay at REFILL_HOUR REFILL_MIN")
        else:
            print("Water level high - Cannot start the pump relay")

def check_max_run_time():
    global relay_state, pump_start_time
    if relay_state and pump_start_time:
        if datetime.now() - pump_start_time > timedelta(seconds=MAX_RUN_TIME):
            relay_state = False
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            pump_start_time = None
            print("Maximum run time exceeded - Relay OFF")

# Set up event detection
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)
GPIO.add_event_detect(WATER_LEVEL_SENSOR_PIN, GPIO.RISING, callback=water_level_callback, bouncetime=300)

try:
    while True:
        check_time_and_start_pump()
        check_max_run_time()
        time.sleep(1)  # Check every second
except KeyboardInterrupt:
    print("Program terminated")
finally:
    GPIO.cleanup()
