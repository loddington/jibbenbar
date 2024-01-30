import os
import mysql.connector



# Run this script on your external web server (if you have one). If not just ignore this script.
# Set up a cron job on the Jibbenbar weather station that rsync's over the logs to the web server and removes them locally.
# You will need to set up SSH keys. I run this from a user called jibbenbar on both servers.
# ie. 1,16,31,46 * * * * rsync --remove-source-files -zh -e ssh /home/jibbenbar/weather_logs/* jibbenbar@ADDRESS_OF-EXTERNAL-SERVER:/home/jibbenbar/db_logs/
# On the Web server side, this script will pick up the logs and process them into the DB.


# Connect to your MySQL database using your read/write user
db = mysql.connector.connect(host="localhost", user="wuser", password="YourReadWritePasswordHere", database="weather")
cursor = db.cursor()

# Get the directory containing the data files
data_dir = "/home/jibbenbar/db_logs/"

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
                                  bme_temp, bme_barometric, bme_humidity, probe_temp, dew_point,
                                  rain_count, wind_speed, wind_gusts, wind_direction, light_meter, UV, sun_temp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Execute the SQL query
    cursor.execute(sql, values)

    # Commit the changes to the database
    db.commit()

    # Delete the processed file
    os.remove(filepath)

# Close the cursor and database connection
cursor.close()
db.close()
