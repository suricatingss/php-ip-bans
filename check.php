<?php
#if (!defined("ban_page") || !defined("js_ban")) die(); 
$output = null;
$ip = $_SERVER["REMOTE_ADDR"];

exec("python ban_actions.py check $ip",$output);


if (!empty($output)) { # the user is banned

        #header("Content-Disposition: attachment, filename:  banned.html");
        if (defined(constant_name: "ban_page")) {
            $html = file_get_contents(ban_page);

            if (defined("js_ban")) {
            $js = "<script>\nconst timeout = \"$output[0]\";";

            if (strpos($html, "</body>") != false) 
            {
                $calling = ($output[0] == "permanent") ? "banned();\n" : "temp_banned();\n";
                $html = str_replace("</body>", $js. file_get_contents(js_ban). $calling . "</script>\n</body>", $html);
            }
            
        }
        
        echo $html;
    
    }
    die(); // do NOT show the rest of the page (index.php)
    
}
?>

