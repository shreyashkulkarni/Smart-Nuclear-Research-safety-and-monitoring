
function fetchdata(){

    $.ajax({

        url: '/data',
        type: 'GET',
        processData: false,
        dataType: 'json',
        success: function(response){
       	    console.log("Inside success");
       	    console.log("RadVal", response.RadVal);
       	    console.log("OccpCnt", response.OccpCnt);
       	    $("#RadVal").html(response.RadVal);
       	    $("#OccpCnt").html(response.OccpCnt);
            $("#light1").html(response.Light_1);
            $("#light2").html(response.Light_2);

            if (response.alarm == 'ON'){
              $("#alarm").html(response.alarm.fontcolor("red"));
            }
            else {
              $("#alarm").html(response.alarm);
            }

            if (response.door == 'OPEN'){
              $("#doors").html(response.door.fontcolor("red"));
            }
            else {
              $("#doors").html(response.door);
            }
            
            if (response.emergencyLights == 'ON'){
              $("#lights").html(response.emergencyLights.fontcolor("red")); 
            }
            else {
              $("#lights").html(response.emergencyLights);     
            }
               
       },
       	failure: function(response) {
			console.log("Inside Failure");
			console.log(response);
		},
		error: function(response) {
			console.log("Inside Error");
			console.log(response);
		}
   });
      
}


$(document).ready(function(){
	console.log("In the main function");
	setInterval(fetchdata,500);
	console.log("Executed the fetchdata");

});


function realTimeClock() {
    
    var rtClock = new Date();
    
    var hours = rtClock.getHours();
    var minutes = rtClock.getMinutes();
    var seconds = rtClock.getSeconds();
    
    
    var amPm = ( hours < 12 ) ? "AM" : "PM";
    
    
    hours = (hours > 12) ? hours - 12 : hours;
    
    hours = ("0" + hours).slice(-2);
    minutes = ("0" + minutes).slice(-2);
    seconds = ("0" + seconds).slice(-2);
    
    document.getElementById('clock').innerHTML = 
        hours + " : " + minutes + " : " + seconds + " " + amPm;
    var t = setTimeout(realTimeClock, 500);
     
}
