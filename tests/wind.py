from gpiozero import Button
import time
import math
import statistics
import requests

store_speeds = []

wind_count = 0 # Counts how many half-rotations
radius_cm = 9.0 # Radius
wind_interval = 5 # Seconds between checks

CM_IN_A_KM = 100000
SECS_IN_AN_HOUR = 3600

ADJUSTMENT = 1.18

# Every half-rotation, add 1 to count
def spin():
	global wind_count
	wind_count = wind_count +1



# Calculate the wind speed

def calculate_speed(time_sec):
	global wind_count
	circumference_cm = (2 * math.pi) * radius_cm
	rotations = wind_count / 2.0

	dist_km = (circumference_cm * rotations) / CM_IN_A_KM

	km_per_sec = dist_km / time_sec
	km_per_hour = km_per_sec * SECS_IN_AN_HOUR

	return km_per_hour * ADJUSTMENT

wind_speed_sensor = Button(5)
wind_speed_sensor.when_pressed = spin


def reset_wind():
	global wind_count
	wind_count = 0


#update_interval = 600  # 10 minutes in seconds
update_interval = 30  # 30 seconds in seconds

last_update_time = time.time()



while True:
    start_time = time.time()
    while time.time() - start_time <= wind_interval:
        reset_wind()
        time.sleep(wind_interval)
        final_speed = calculate_speed(wind_interval)
        store_speeds.append(final_speed)
    wind_gust_value = max(store_speeds)
    wind_speed_value = statistics.mean(store_speeds)
    print(wind_speed_value, wind_gust_value)

    current_time = time.time()

    if current_time - last_update_time >= update_interval:
        windspeed_api_url = "http://localhost:5000/sensors/wind_speed"
        windgust_api_url = "http://localhost:5000/sensors/wind_gusts"

        try:
            response = requests.put(windspeed_api_url, json={'sensor_value': wind_speed_value})
            response.raise_for_status()
            response = requests.put(windgust_api_url, json={'sensor_value': wind_gust_value})
            response.raise_for_status()
            print("Data sent successfully")
            last_update_time = current_time  # Update last update time
#            Clear the list for next iteration once it has been sent to Flask.
            store_speeds.clear()
        except requests.exceptions.RequestException as e:
            print("Error:", e)




