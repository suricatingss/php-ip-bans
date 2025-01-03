/*
 * This is a sample JS. You can modify it to serve your needs
 * By default, it gets linked with the sample html page.
 * 
 * This script's purpose is to serve as a live countdown
 * for how long the person has been banned
 * 
 * ex.: You are banned for 2d 3h 40m 30s
 * 
 * It works via the element's ID (to change the innerHTML),
 * you can change it for your html page.
 * 
 * You can't change the funcions's names, as it's PHP who calls them.
 * But you can change its content.
 * 
 * temp_ban is called at startup if youre tempbanned (which calls live timer)
 * banned is called once too if youre banned forever
 */

const temp_ban_id = "time";
const ban_id = "banned";

function live_countdown() {
    const label = document.getElementById(temp_ban_id);
    label.style.visibility = "visible";
    

    let now = new Date().getTime();
    let goal = new Date(timeout).getTime();
    
    let distance = goal - now;

    if (distance <= 0) 
        window.location.reload(); // reload the page
    else {
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        label.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
    }
}

function temp_banned() {
    // This function runs when there is a tempban
    // It only runs once, you can add more code as you please
    
    // update the countdown
    live_countdown();
    setInterval(live_countdown, 1000); // set the countdown to update every sec

}

function banned() {
    const perm_label = document.getElementById(ban_id);

    perm_label.style.visibility = "visible";

    // you can add more code as you please

}
