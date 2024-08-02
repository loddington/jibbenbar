import RPi.GPIO as GPIO
import time
import requests

# API URL
api_url = "http://127.0.0.1:5000/sensors/bucket_tips/increment"

# Set the GPIO pin for the button
button_pin = 26

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Variables to track time
magnet_detected = False
start_time = 0
end_time = 0


def sensor_callback(channel):
    global magnet_detected, start_time, end_time

    if GPIO.input(button_pin) == GPIO.LOW:
        if not magnet_detected:
            magnet_detected = True
            start_time = time.time()
            print("Magnet not detected")

    else:
        if magnet_detected:
            magnet_detected = False
            end_time = time.time()
            duration = end_time - start_time
            print(f"Magnet detected, Duration: {duration:.2f} seconds")
            rain_gauge_tip()

# Add event detection on the hall or reed sensor pin
GPIO.add_event_detect(button_pin, GPIO.BOTH, callback=sensor_callback, bouncetime=10)


# Function to handle rain gauge tip events
def rain_gauge_tip():
    try:
        response = requests.put(api_url)

        if response.status_code == 200:
            sensor_data = response.json()
            print("Sensor value incremented successfully:", sensor_data['sensor'], time.ctime())
        else:
            print("Error:", response.text)
            sensor_data = response.json()  # a quick retry on error

    except requests.exceptions.RequestException as e:
        print("Error calling API:", e)


try:
    while True:
        time.sleep(0.1)  # Keep the script running

except KeyboardInterrupt:
    pass 
