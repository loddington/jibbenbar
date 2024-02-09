import mariadb, configparser
from datetime import datetime, timedelta

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

# I wanted to keep as little data as possible. So I decided to create a sumarized version of each day as a single line in a new tabel called dailydata.
# That way we can purge the detailed data in weatherdata after as little as 24 hours. At the moment I am keeping 32 days.



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

# Get current date components
today = datetime.now()
year = today.year
month = today.month
day = today.day
week = today.strftime("%W")

# Thresholds for calculations - lux_threshold and wind_threshold are a complete guess and will require some calibration. The idea was to record how many hours a day that we had of good solar and wind power generation. 
lux_threshold = 50000
wind_threshold = 5

# Min and Max temperatures today and the time they occurred.
min_max_temp_since_midnight_query = f"""
SELECT probe_temp AS min_temp,
       (SELECT MAX(probe_temp) FROM weatherdata WHERE year = {year} AND month = {month} AND day_of_month = {day}) AS max_temp,
       (SELECT hour_min FROM weatherdata WHERE probe_temp = min_temp AND year = {year} AND month = {month} AND day_of_month = {day} LIMIT 1) AS min_temp_time,
       (SELECT hour_min FROM weatherdata WHERE probe_temp = max_temp AND year = {year} AND month = {month} AND day_of_month = {day} LIMIT 1) AS max_temp_time
FROM weatherdata
WHERE year = {year} AND month = {month} AND day_of_month = {day}
GROUP BY probe_temp
LIMIT 1
"""
cursor.execute(min_max_temp_since_midnight_query)
min_max_temp_since_midnight_result = cursor.fetchone()
mintemp = min_max_temp_since_midnight_result[0]
maxtemp = min_max_temp_since_midnight_result[1]
maxtemptime = min_max_temp_since_midnight_result[2]
mintemptime = min_max_temp_since_midnight_result[3]

# End of Day Wind Query
end_of_day_wind_query = f"""
SELECT wind_direction, COUNT(wind_direction) AS value_occurrence
FROM weatherdata
WHERE year = {year} AND month = {month} AND day_of_month = {day}
GROUP BY wind_direction
ORDER BY value_occurrence DESC
LIMIT 1
"""
cursor.execute(end_of_day_wind_query)
wind_result = cursor.fetchone()
wind_direction_frequency = wind_result[0]

# End of Day Data Query
end_of_day_data_query = f"""
SELECT MAX(epoch) AS epoch, MAX(iso_date) AS iso_date, day_of_month, month, year, {week} AS week,
       ROUND(AVG(probe_temp), 2) AS avgtemp, {maxtemp} AS maxtemp, {mintemp} AS mintemp,
       ROUND(AVG(dew_point), 2) AS avgdew, SUM(rain_count) AS sumrain,
       ROUND(AVG(barometric_pressure), 2) AS avgbarometric, ROUND(AVG(humidity), 2) AS avghumidity,
       ROUND(AVG(wind_speed), 2) AS avgwind, ROUND(AVG(LUX), 2) AS avglux, ROUND(AVG(UV), 2) AS avguv,
       SUM(CASE WHEN LUX > {lux_threshold} THEN 0.166667 ELSE 0 END) AS luxhours, SUM(LUX) AS sumluxday,
       SUM(UV) AS sumuvday, SUM(CASE WHEN wind_speed > {wind_threshold} THEN 0.166667 ELSE 0 END) AS windhours,
       {maxtemptime} AS maxtemptime, {mintemptime} AS mintemptime, '{wind_direction_frequency}' AS wind_direction_frequency,
       ROUND(MAX(wind_gusts), 2) AS max_wind, ROUND(MAX(barometric_pressure), 2) AS max_barometer,
       ROUND(MIN(barometric_pressure), 2) AS min_barometer, MAX(sun_temp) AS max_sun_temp,
       AVG(sun_temp) AS avg_sun_temp, MIN(sun_temp) AS min_sun_temp
FROM weatherdata
WHERE year = {year} AND month = {month} AND day_of_month = {day}
"""
cursor.execute(end_of_day_data_query)
end_of_day_data = cursor.fetchone()

# Prepare insert query
insert_query = """
INSERT INTO dailydata (
    epoch, iso_date, day_of_month, month, year, week,
    avgtemp, maxtemp, mintemp, avgdew, sumrain, avgbarometric,
    avghumidity, avgwind, avglux, luxhours, avguv, sumluxday, sumuvday, windhours,
    maxtemptime, mintemptime, wind_direction_frequency, max_wind, max_barometer,
    min_barometer, max_sun_temp, avg_sun_temp, min_sun_temp
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

# Execute insert query
cursor.execute(insert_query, end_of_day_data)

# (1706819402, 202402020630, 5, 2, 2, 2024, Decimal('26.59'), Decimal('27.50'), Decimal('26.06'), Decimal('19.81'), Decimal('3.64'), Decimal('1091.47'), Decimal('66.08'), Decimal('0.00'), Decimal('309.00'), Decimal('0.01'), Decimal('0.000000'), Decimal('12360'), Decimal('0.2'), Decimal('0.000000'), Decimal('6.10'), Decimal('0.00'), '180.0', Decimal('0.48'), Decimal('1092.09'), Decimal('1090.93'), Decimal('26.80'), Decimal('26.088250'), Decimal('25.61'))



print (end_of_day_data)




# Commit and close connections
conn.commit()
cursor.close()
conn.close()






# This code will purge data older than X days from weatherdata. Since we sumarize the data fronm weatherdata each day, we shouldnt need more than a couple of days of data.


def delete_old_records(do_purge):
    if not do_purge:
        print("Purge operation not requested. Skipping deletion of old records.")
        return

    # Connect to the database
    try:
       connection = mariadb.connect(
       host=(config['databasecredentials']['host']),
       user=(config['databasecredentials']['user']),
       password=(config['databasecredentials']['password']),
       database=(config['databasecredentials']['database'])
    )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return

    try:
        with connection.cursor() as cursor:
            # Calculate the date X days ago - X is defined in config.ini
            days_ago = datetime.now() - timedelta(days=float((config['purge']['purge_days'])))

            # Convert X days ago to epoch time
            days_ago_epoch = int(days_ago.timestamp())

            # SQL query to delete records older than X days
            sql = "DELETE FROM weatherdata WHERE epoch < %s"

            # Execute the SQL query with the parameter
            cursor.execute(sql, (days_ago_epoch,))

            # Commit the changes to the database
            connection.commit()

            print("Old records deleted successfully.")

    except mariadb.Error as e:
        print(f"Error deleting old records: {e}")

    finally:
        # Close the database connection
        connection.close()

# Set do_purge to True or False based on your requirement - This is defined in config.ini
do_purge = (config['purge']['do_purge'])

# Call the function to delete old records if do_purge is True
delete_old_records(do_purge)



