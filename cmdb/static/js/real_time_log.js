
var socket;

function init_ws(){
    var protocol = window.location.protocol;
    if ( protocol == 'http:' ) {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/real_time_log/", null, {debug: true});

    socket.onmessage = function(e) {
        $("#log").append(e.data);
    }

    socket.onopen = function() {
        // socket.send("start ws connection");
        // $("#log").val('');
        socket.send("hello world");
    }

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}

$(document).ready(function() {

    init_ws();


} );
