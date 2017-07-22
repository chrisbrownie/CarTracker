<?php

        $logPath = 'log/logdata.csv';

        $data = json_decode($_POST["gpsData"], true);

        $logString = $data['time'] . "," . $data['lat'] . "," . $data['lon'] . "," . $data['alt'] . "," . $data['track'] . "," . $data['speed'] . "\n";

        file_put_contents($logPath,$logString, FILE_APPEND | LOCK_EX);
        
        print_r($logString);


?>
