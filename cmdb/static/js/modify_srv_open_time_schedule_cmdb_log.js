var socket;

//初始化websocket
function init_ws() {
    var protocol = window.location.protocol;
    var id = $('#id_log').val();
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/modify_srv_open_time_schedule_log/" + id + "/", null, {debug: true});

    socket.onmessage = function (e) {
        var data = $.parseJSON(e.data);
        if (data.message == "update_log") {
            $("#log").val(data.log)
        }
    };

    socket.onopen = function () {
        socket.send("start ws connection");
    };

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}


$(document).ready(function () {

    init_ws();

});
