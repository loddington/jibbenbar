import os, mariadb, configparser
from datetime import datetime

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

# Run this script on your external web server (if you have one). If not just ignore this script.
# Set up a cron job on the Jibbenbar weather station that rsync's over the logs to the web server and removes them locally.
# You will need to set up SSH keys. I run this from a user called jibbenbar on both servers.
# ie. 1,16,31,46 * * * * rsync --remove-source-files -zh -e ssh /home/jibbenbar/weather_logs/* jibbenbar@ADDRESS_OF-EXTERNAL-SERVER:/home/jibbenbar/weather_logs/
# On the Web server side, this script will pick up the logs and process them into the DB.

# Create a database connection
try:
    conn = mariadb.connect(
       host=(config['databasecredentials']['host']),
       user=(config['databasecredentials']['user']),
       password=(config['databasecredentials']['password']),
       database=(config['databasecredentials']['database'])
    )
    print("Connected to MariaDB database")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    exit()

cursor = conn.cursor()


# Get the directory containing the data files
data_dir = "/home/jibbenbar/weather_logs/"

# Loop through all files in the directory
for filename in os.listdir(data_dir):
    filepath = os.path.join(data_dir, filename)

    # Open the file and read the line
    with open(filepath, "r") as f:
        data = f.readline().strip()

    # Convert the data to a list of values
    values = data.strip("()").split(",")

    # Create the SQL query to insert the data
    sql = """
        INSERT INTO weatherdata (epoch, iso_date, hour_min, day_of_month, month, year,
                                  backup_temp, barometric_pressure, humidity, probe_temp, dew_point,
                                  rain_count, wind_speed, wind_gusts, wind_direction, LUX, UV, sun_temp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Execute the SQL query
    cursor.execute(sql, values)

    # Delete the processed file
    os.remove(filepath)

# Commit and close connections
conn.commit()
cursor.close()
conn.close()
