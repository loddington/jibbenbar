#MCP3002 is more than enough, you are only going to use 1 channel and it uses less space on the breadboard. Though often just as expensive.

#We are using the Python statistics module to find the most common value (mode) rather than an average. 

from gpiozero import MCP3008
import time, math, statistics, requests

check_interval = 1 

adc = MCP3008(channel=0) #Check which channel you are using. Most people will use 0
direction_count = 0 


#Recorded voltages
volts = [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 1.2, 1.4, 1.8, 2.0, 2.2, 2.3, 2.5, 2.7, 2.8, 2.9]

#Map voltages to compass points

dict = {}
dict[0.1] = 270 #West
dict[0.2] = 315.5 #NW
dict[0.3] = 292.5 #WNW
dict[0.4] = 0   #North
dict[0.6] = 337.5 #NNW
dict[0.7] = 225 #SW
dict[0.8] = 247.5 #WSW
dict[1.2] = 45  #NE
dict[1.4] = 22.5  #NNE
dict[1.8] = 180 #South
dict[2.0] = 202.5 #SSW
dict[2.2] = 135 #SE
dict[2.3] = 135 #SE
dict[2.5] = 157.5 #SSE
dict[2.7] = 90  #East
dict[2.8] = 67.5  #ENE
dict[2.9] = 112.5 #ESE

store_direction = []

def reset_direction():
        global direction_count
        direction_count = 0

update_interval = 600  # 10 minutes in seconds

last_update_time = time.time()


while True:
    start_time = time.time()
    while time.time() - start_time <= check_interval:
        reset_direction()
        time.sleep(check_interval)
        wind =round(adc.value*3.3,1)
        store_direction.append((dict[(wind)]))
    direction_mode_value = statistics.mode(store_direction)
    print('mode', direction_mode_value, 'voltage', wind, 'wind_direction', (dict[(wind)]))

    current_time = time.time()

    if current_time - last_update_time >= update_interval:
        wind_direction_api_url = "http://localhost:5000/sensors/wind_direction"

        try:
            response = requests.put(wind_direction_api_url, json={'sensor_value': direction_mode_value})
            response.raise_for_status()
#            print("Data sent successfully")
            last_update_time = current_time  # Update last update time
#            Clear the list for next iteration once it has been sent to Flask API Data Logger.
            store_direction.clear()
        except requests.exceptions.RequestException as e:
            print("Error:", e)



#Need to map voltages to compass degrees to send to the API.









