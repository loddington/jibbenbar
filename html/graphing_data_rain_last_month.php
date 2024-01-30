<?php
require_once 'db.php'; // Import database credentials


// REWRITE THIS TO USE DAILYDATA table. Much faster


// Create a database connection
$mysqli = new mysqli($dbHost, $dbUser, $dbPass, $dbName);


// Check connection
if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
}


$today =  date('Y-m-d', time());
list($year, $month, $day) = explode('-', $today);


// Calculate the SUM of rain_count by day_month for the previous month
$prevMonth = date('Y-m-d 00:00:00', strtotime('first day of last month'));
$sumRainPrevMonthQuery = "SELECT day_of_month, month, SUM(rain_count) as sum_rain_previous FROM weatherdata WHERE year = YEAR('$prevMonth') AND month = MONTH('$prevMonth') GROUP BY day_of_month, month";
$sumRainPrevMonth = $mysqli->query($sumRainPrevMonthQuery)->fetch_all(MYSQLI_ASSOC);


header('Content-Type: application/json');
echo json_encode($sumRainPrevMonth);
