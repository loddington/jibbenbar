<?php

//
// Based on SunCalc a PHP library for calculating sun/moon position and light phases.
// https://github.com/gregseth/suncalc-php
//
// Based on Vladimir Agafonkin's JavaScript library.
// https://github.com/mourner/suncalc
//
//Apologies for butchering it.

namespace jibbenbar;

use DateInterval;

require_once 'db.php'; // Import some site-specific stuff like timezone and long/lat


// shortcuts for easier to read formulas
define('PI', M_PI);
define('rad', PI / 180);
define('daySec', 60 * 60 * 24);
define('J1970', 2440588);
define('J2000', 2451545);
define('e', rad * 23.4397); // obliquity of the Earth

function toJulian($date) {
    return $date->getTimestamp() / daySec - 0.5 + J1970;
}

function fromJulian($j) {
    $dt = new \DateTime("@".round(($j + 0.5 - J1970) * daySec));
    return $dt;
}

function toDays($date) {
    return toJulian($date) - J2000;
}

function rightAscension($l, $b) {
    return atan2(sin($l) * cos(e) - tan($b) * sin(e), cos($l));
}

function declination($l, $b) {
    return asin(sin($b) * cos(e) + cos($b) * sin(e) * sin($l));
}

function siderealTime($d, $lw) {
    return rad * (280.16 + 360.9856235 * $d) - $lw;
}

function moonCoords($d) {
    $L = rad * (218.316 + 13.176396 * $d); // ecliptic longitude
    $M = rad * (134.963 + 13.064993 * $d); // mean anomaly
    $F = rad * (93.272 + 13.229350 * $d);  // mean distance

    $l  = $L + rad * 6.289 * sin($M); // longitude
    $b  = rad * 5.128 * sin($F);      // latitude
    $dt = 385001 - 20905 * cos($M);   // distance to the moon in km

    return (object) [
        'dec' => declination($l, $b),
        'ra'  => rightAscension($l, $b),
        'dist' => $dt
    ];
}

function hoursLater($date, $h) {
    $newDate = clone $date;
    return $newDate->add(new DateInterval('PT' . round($h * 60) . 'M'));
}

class SunCalc {

    var $date;
    var $lat;
    var $lng;

    function __construct($date, $lat, $lng) {
        $this->date = $date;
        $this->lat  = $lat;
        $this->lng  = $lng;
    }

    function getMoonIllumination() {
        $d = toDays($this->date);
        $m = moonCoords($d);

        return [
            'fraction' => (1 + cos($m->ra)) / 2,
            'phase'    => $m->ra,
            'angle'    => $m->dec
        ];
    }

    function getMoonTimes() {
        $t = clone $this->date;
        $t->setTime(0, 0, 0);

        $hc = 0.133 * rad;
        $h0 = $this->getMoonPosition($t)->altitude - $hc;
        $rise = 0;
        $set = 0;

        for ($i = 1; $i <= 24; $i += 2) {
            $h1 = $this->getMoonPosition(hoursLater($t, $i))->altitude - $hc;
            $h2 = $this->getMoonPosition(hoursLater($t, $i + 1))->altitude - $hc;

            $a = ($h0 + $h2) / 2 - $h1;
            $b = ($h2 - $h0) / 2;
            $xe = -$b / (2 * $a);
            $ye = ($a * $xe + $b) * $xe + $h1;
            $d = $b * $b - 4 * $a * $h1;

            if ($d >= 0) {
                $dx = sqrt($d) / (abs($a) * 2);
                $x1 = $xe - $dx;
                $x2 = $xe + $dx;

                if (abs($x1) <= 1) {
                    $time = $i + $x1;

                    if ($h0 < 0 && $h1 >= 0) {
                        $rise = $time;
                    } elseif ($h0 >= 0 && $h1 < 0) {
                        $set = $time;
                    }
                }

                if (abs($x2) <= 1) {
                    $time = $i + $x2;

                    if ($h0 < 0 && $h1 >= 0) {
                        $rise = $time;
                    } elseif ($h0 >= 0 && $h1 < 0) {
                        $set = $time;
                    }
                }
            }

            $h0 = $h2;
        }

        $result = [];
        if ($rise != 0) {
//            $result['moonrise'] = hoursLater($t, $rise)->format('Y-m-d H:i:s');
            $result['moonrise'] = hoursLater($t, $rise)->format('H:i:s');
        }

        if ($set != 0) {
            $moonset = hoursLater($t, $set);

            // If the moonset time is earlier than the current time, add one day
            if ($moonset < $this->date) {
                $moonset->add(new DateInterval('P1D'));
            }

//            $result['moonset'] = $moonset->format('Y-m-d H:i:s');
            $result['moonset'] = $moonset->format('H:i:s');
        }

        return $result;
    }

    function getMoonPosition($date) {
        $d = toDays($date);
        $coords = moonCoords($d);
        $H = siderealTime($d, -rad * $this->lng) - $coords->ra;
        $h = altitude($H, $this->lat, $coords->dec);

        return (object) [
            'altitude' => $h
        ];
    }
}

function altitude($H, $phi, $dec) {
    return asin(sin($phi * rad) * sin($dec) + cos($phi * rad) * cos($dec) * cos($H));
}

// Convert the numeric moon phase to a descriptive label
function getMoonPhaseName($phase) {
    if ($phase === 0 || $phase === 1) {
        return "New Moon";
    } elseif ($phase > 0 && $phase < 0.25) {
        return "Waxing Crescent";
    } elseif ($phase === 0.25) {
        return "First Quarter";
    } elseif ($phase > 0.25 && $phase < 0.5) {
        return "Waxing Gibbous";
    } elseif ($phase === 0.5) {
        return "Full Moon";
    } elseif ($phase > 0.5 && $phase < 0.75) {
        return "Waning Gibbous";
    } elseif ($phase === 0.75) {
        return "Last Quarter";
    } elseif ($phase > 0.75 && $phase < 1) {
        return "Waning Crescent";
    }
}

// Function to format the fraction as a simple fraction over 100
function formatFraction($fraction) {
    return round($fraction * 100) . "/100";
}

//$test = new SunCalc(new \DateTime('now', new \DateTimeZone('Australia/Brisbane')), -28.79, 151.64);
$test = new SunCalc(new \DateTime('now', new \DateTimeZone($station_timezone)), $latitude, $longitude);
$moonIllumination = $test->getMoonIllumination();
$moonTimes = $test->getMoonTimes();

// Replace the numeric 'phase' value with the descriptive moon phase name
$moonIllumination['phase'] = getMoonPhaseName($moonIllumination['phase']);

// Convert the fraction to the "x/100" format
$moonIllumination['fraction'] = formatFraction($moonIllumination['fraction']);

// Combine all values into one array
$combinedResult = array_merge($moonIllumination, $moonTimes);

// Output the result as a JSON string
header('Content-Type: application/json');
echo json_encode($combinedResult);

?>
