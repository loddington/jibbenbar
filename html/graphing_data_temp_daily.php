<?php
require_once 'db.php'; // Import database credentials


// Create a database connection
$mysqli = new mysqli($dbHost, $dbUser, $dbPass, $dbName);


// Check connection
if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
}


$today =  date('Y-m-d', time());
list($year, $month, $day) = explode('-', $today);


// query for average, max, and min temperatures by day of month.
$TemperatureQuery = "
    SELECT
        day_of_month,
        month,
        avgtemp AS daily_avg_temp,
        maxtemp AS daily_max_temp,
        mintemp AS daily_min_temp,
        max_sun_temp AS daily_max_sun_temp
    FROM dailydata
    WHERE year = $year AND month = $month
    GROUP BY day_of_month, month
";

// Execute the combined query
$combinedTempQuery = $mysqli->query($TemperatureQuery);

// Fetch results in a single array
$combinedTempData = $combinedTempQuery->fetch_all(MYSQLI_ASSOC);

header('Content-Type: application/json');
echo json_encode($combinedTempData);
