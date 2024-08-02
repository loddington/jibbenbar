import RPi.GPIO as GPIO
import time, math, statistics, requests

# Configuration and constants
radius_cm = 9.5  # Radius of the anemometer
rotations_per_reading = 1 #Some Anemometer's record 2 button presses per rotation
wind_interval = 5  # Interval to check wind speed in seconds
update_interval = 10  # Interval to update the server in seconds
CM_IN_A_KM = 100000
SECS_IN_AN_HOUR = 3600
ADJUSTMENT = 1.2  # Calibration adjustment factor
wind_speed_sensor_pin = 16  # GPIO pin for wind speed sensor



# Credit where credit is due, much of this code was taken
# straight from https://projects.raspberrypi.org/en/projects/build-your-own-weather-station/


# Global variables
wind_count = 0
store_speeds = []  # List to store speed measurements
last_update_time = time.time()  # Time of the last update to the server

# Set up the GPIO mode and pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(wind_speed_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Every half-rotation, increment the wind count
def spin(channel):
    global wind_count
    wind_count += 1

# Calculate the wind speed in km/h
def calculate_speed(time_sec):
    global wind_count
    circumference_cm = (2 * math.pi) * radius_cm
    rotations = wind_count / rotations_per_reading
    dist_km = (circumference_cm * rotations) / CM_IN_A_KM
    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * SECS_IN_AN_HOUR
    return km_per_hour * ADJUSTMENT

# Reset the wind count to 0
def reset_wind():
    global wind_count
    wind_count = 0

# Set up event detection on the wind speed sensor pin
GPIO.add_event_detect(wind_speed_sensor_pin, GPIO.FALLING, callback=spin, bouncetime=200)

print("Monitoring Wind Speed Sensor...")

try:
    while True:
        start_time = time.time()
        while time.time() - start_time <= wind_interval:
            reset_wind()
            time.sleep(wind_interval)
            final_speed = calculate_speed(wind_interval)
            store_speeds.append(final_speed)

        wind_gust_value = round(max(store_speeds), 2)
        wind_speed_value = round(statistics.mean(store_speeds), 2)

        current_time = time.time()

        if current_time - last_update_time >= update_interval:
            windspeed_api_url = "http://localhost:5000/sensors/wind_speed"
            windgust_api_url = "http://localhost:5000/sensors/wind_gusts"

            try:
                response = requests.put(windspeed_api_url, json={'sensor_value': wind_speed_value})
                response.raise_for_status()
                time.sleep(0.1)
                response = requests.put(windgust_api_url, json={'sensor_value': wind_gust_value})
                response.raise_for_status()
                print(f"Data sent successfully: Wind Speed = {wind_speed_value} km/h, Wind Gust = {wind_gust_value} km/h")
                last_update_time = current_time  # Update last update time
                store_speeds.clear()  # Clear the list for the next iteration
            except requests.exceptions.RequestException as e:
                print("Error:", e)

except KeyboardInterrupt:
    print("Exiting program")

finally:
    GPIO.cleanup()
