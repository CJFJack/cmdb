
var socket;

$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURIComponent(results[1]) || 0;
    }
}

function init_ws(){
    var protocol = window.location.protocol;
    if ( protocol == 'http:' ) {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    var uuid = $.urlParam('uuid');
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/hotupdate_cmdb_log/" + uuid, null, {debug: true});

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
