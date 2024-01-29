# DS18B20 Probe 
#enable 1 Wire in rasp-conf 
# I do wonder why I use this probe when the ATH20 has 2 thermometers on it and would probably do. This one does look it will last a long time. 


import glob, time, requests

# API URL - probe_temp API interface to hit
probe_temp_url = "http://localhost:5000/sensors/probe_temp"

#How often to update the API
update_interval = 60  # 1 minutes in seconds

 
#serach for the probe.
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

current_time = time.time()

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
#check for valid output
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
#If you need to make a calibration adjustment to the probe you can change 1000 to a different value.
        temp_c = float(temp_string) / 1000.0
        return temp_c


last_update_time = time.time()


while True:
    start_time = time.time()
    while time.time() - start_time <= update_interval:
        time.sleep(30)
        temperature = read_temp()
#        print(temperature)

    current_time = time.time()

    if current_time - last_update_time >= update_interval:

        try:
            response = requests.put(probe_temp_url, json={'sensor_value': temperature})
            response.raise_for_status()
#            print("Data sent successfully")
            last_update_time = current_time  # Update last update time
        except requests.exceptions.RequestException as e:
            print("Error:", e)













