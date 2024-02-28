import json, requests, mariadb, time, datetime, pytz, configparser

# I installed a second tipping bucket Martek to prove things were working. 
# It writes to a separate Flask API logger on port 5001 and to a separate table in the DB.

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

# Dates and Times.
# I know you are thinking, why so many time and date formats when it should all just work off epoch?
# Well it should, but I wanted some flexibility because I really wasn't sure what I wanted.
# I will revisit that later.

#TimeZone
timezone = pytz.timezone((config['timezone']['timezone']))
now = datetime.datetime.now(timezone)
iso_date = int(now.strftime("%Y%m%d%H%M"))
hour_min = float(now.strftime("%H.%M"))
day_of_month = int(now.strftime("%d"))
month = int(now.strftime("%m"))
year =  int(now.strftime("%Y"))
epoch = int(time.time())

# Retrieve the sensor data from the API
# You can do this by hand by using:
# curl  -H "Content-Type: application/json"  -X GET http://localhost:5000/sensors

response = requests.get("http://localhost:5001/sensors")
response.raise_for_status()  # Error message

sensor_data = response.json()

# Create variables for each sensor ID and assign their values
for sensor in sensor_data["sensors"]:
   id = sensor["id"]
   value = sensor["sensor_value"]
   globals()[id] = value

bucket_size = 0.2794
rain_count_2 = round((bucket_tips_2 * bucket_size), 2) # Number of times the rain bucket tipped multiplied by the size of the bucket.


# Check if any sensor reading equals -50 as this means we have not started populating the Data Logger API yet (or your sensor is broken) 
if rain_count_2 == -50:
    print("Exiting: One of the sensor readings equals -50.")
    exit()


# Connect to MariaDB database
try:
    conn = mariadb.connect(

        host=(config['databasecredentials']['host']),
        user=(config['databasecredentials']['user']),
        password=(config['databasecredentials']['password']),
        database=(config['databasecredentials']['database'])
    )
    cursor = conn.cursor()

    sql = "INSERT INTO weatherdata_2 (epoch, iso_date, hour_min, day_of_month, month, year, rain_count_2) VALUES (%(epoch)s, %(iso_date)s, %(hour_min)s, %(day_of_month)s, %(month)s, %(year)s, %(rain_count_2)s)"

        # Create a dictionary of parameters
    params = {
            "epoch": epoch, "iso_date": iso_date, "hour_min": hour_min,
            "day_of_month": day_of_month, "month": month, "year": year,
            "rain_count_2": rain_count_2,
        }

        # Execute the query with the dictionary of parameters
    cursor.execute(sql, params)

    conn.commit()
    print(cursor.rowcount, "record inserted.")

except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")

finally:
    if conn:
        #Once we have the data in the database we need to reset the rain guage to 0. 
        rain_api_url = "http://localhost:5001/sensors/bucket_tips_2"
        rain_reset = requests.put(rain_api_url, json={'sensor_value': 0})
        conn.close()



#Logging 1 is true 0 is false. Handy for debugging or log shipping to an external DB/WebServer.
#logging = 1
#log_directory = /home/jibbenbar/weather_logs
logging = int((config['logging']['logging']))
log_directory = (config['logging']['log_directory'])



AllSensorData = epoch, iso_date, hour_min, day_of_month, month, year, rain_count_2;


#write output to file for debugging.

if logging == 1:
     print (AllSensorData)

