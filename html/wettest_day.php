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


// Calculate the SUM of rain_count by month for the previous 12 months
$prev12MonthsQuery = "SELECT day_of_month, SUM(rain_count) as sum_rain_year FROM weatherdata WHERE year >= YEAR(NOW())";
$sumRainPrev12Months = $mysqli->query($prev12MonthsQuery)->fetch_all(MYSQLI_ASSOC);



header('Content-Type: application/json');
echo json_encode($sumRainPrev12Months);
