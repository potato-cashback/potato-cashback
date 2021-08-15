//listen to shake event
var shakeEvent = new Shake({threshold: 15});
shakeEvent.start();
window.addEventListener('shake', function(){
    document.querySelector("#login").style.display = "block";
    setTimeout(()=>{
        document.querySelector("#login").style.display = "none";
    }, 5000)
}, false);

//stop listening
function stopShake(){
    shakeEvent.stop();
}

//check if shake is supported or not.
if(!("ondevicemotion" in window)){
    console.log("Not Supported");
}