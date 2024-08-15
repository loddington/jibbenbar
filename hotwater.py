import RPi.GPIO as GPIO
import time
import requests
import os

MAXTEMP = 90  # Max temperature before it cuts the power to the relay.
MINTEMP = 70  # Temperature at which the relay turns back on

# GPIO setup
BUTTON_PIN = 10 # GPIO 10 for the button
RELAY_PIN = 17  # Relay on GPIO 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button with pull-up resistor
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Initialize relay as off
relay_state = False
GPIO.output(RELAY_PIN, GPIO.HIGH)  # Relay off

# Track if the relay was turned off due to high temperature
relay_off_due_to_temp = False

# Sensor path setup DS18B20
sensor_address = "28-44c45d1f64ff"
sensor_path = f"/sys/bus/w1/devices/{sensor_address}/w1_slave"

# Slack webhook URL
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# File paths for remote control
REMOTE_CONTROL_DIR = "/home/jibbenbar/hotwater/"
ON_FILE_PATH = os.path.join(REMOTE_CONTROL_DIR, "on.txt")
OFF_FILE_PATH = os.path.join(REMOTE_CONTROL_DIR, "off.txt")

def send_slack_message(message):
    payload = {"text": message}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Failed to send Slack message: {e}")

def read_temperature(sensor_path):
    try:
        with open(sensor_path, 'r') as f:
            lines = f.readlines()
            if lines[0].strip()[-3:] == 'YES':
                temp_str = lines[1].split('t=')[-1]
                return float(temp_str) / 1000.0
            else:
                return None
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return None

def button_pressed_callback(channel):
    global relay_state, relay_off_due_to_temp
    relay_state = not relay_state
    relay_off_due_to_temp = False  # Reset the flag when the button is pressed
    GPIO.output(RELAY_PIN, GPIO.LOW if relay_state else GPIO.HIGH)  # Toggle relay state
    state = "on" if relay_state else "off"
    temperature = read_temperature(sensor_path)
    if temperature is not None:
        send_slack_message(f"Button pressed. Relay turned {state}. Current temperature: {temperature:.2f}°C.")
    else:
        send_slack_message(f"Button pressed. Relay turned {state}. Temperature reading failed.")

def check_remote_control():
    global relay_state, relay_off_due_to_temp
    if os.path.exists(ON_FILE_PATH):
        if not relay_state:  # Only turn on if it's currently off
            relay_state = True
            relay_off_due_to_temp = False  # Reset the flag if turned on remotely
            GPIO.output(RELAY_PIN, GPIO.LOW)
            send_slack_message("Relay turned on remotely via on.txt")
        os.remove(ON_FILE_PATH)  # Optionally remove the file after processing

    elif os.path.exists(OFF_FILE_PATH):
        if relay_state:  # Only turn off if it's currently on
            relay_state = False
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            send_slack_message("Relay turned off remotely via off.txt")
        os.remove(OFF_FILE_PATH)  # Optionally remove the file after processing

# Event detection for button press
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_pressed_callback, bouncetime=300)

try:
    while True:
        # Check for remote control commands
        check_remote_control()

        # Read temperature
        temperature = read_temperature(sensor_path)

        if temperature is not None:
            # Check if the temperature exceeds the threshold to turn off the relay
            if temperature >= MAXTEMP and relay_state:
                relay_state = False
                relay_off_due_to_temp = True  # Set the flag indicating the relay was turned off due to high temperature
                GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn off relay
                send_slack_message(f"Temperature reached {temperature:.2f}°C. Relay turned off.")

            # Check if the temperature drops below the minimum threshold to turn the relay back on
            elif temperature <= MINTEMP and relay_off_due_to_temp:
                relay_state = True
                relay_off_due_to_temp = False  # Reset the flag once the relay is turned back on
                GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn on relay
                send_slack_message(f"Temperature dropped to {temperature:.2f}°C. Relay turned on.")

        time.sleep(20)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
