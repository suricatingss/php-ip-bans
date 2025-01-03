<?php
function user_strike() {
    $Ip = $_SERVER["REMOTE_ADDR"];
    exec("python ban_actions.py strike $Ip");
}
function user_clean() {
    $Ip = $_SERVER["REMOTE_ADDR"];
    exec("python ban_actions.py clean $Ip");
}
?>