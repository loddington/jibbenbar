<?php
require_once 'db.php'; // Import database credentials


// Create a database connection
$mysqli = new mysqli($dbHost, $dbUser, $dbPass, $dbName);


// Check connection
if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
}

date_default_timezone_set($station_timezone);
$today =  date('Y-m-d', time());
list($year, $month, $day) = explode('-', $today);


// Calculate the SUM of rain_count by day_month since the beginning of the month
//$sumRainByDayMonthQuery = "SELECT day_of_month, month, SUM(rain_count) as daily_rain FROM weatherdata WHERE year = $year AND month = $month GROUP BY day_of_month, month";
$sumRainByDayMonthQuery = "SELECT day_of_month, month, sumrain as daily_rain FROM dailydata WHERE year = $year AND month = $month GROUP BY day_of_month, month";
$sumRainByDayMonth = $mysqli->query($sumRainByDayMonthQuery)->fetch_all(MYSQLI_ASSOC);


header('Content-Type: application/json');
echo json_encode($sumRainByDayMonth);
