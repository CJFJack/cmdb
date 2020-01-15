var socket;


function init_ws() {
    var protocol = window.location.protocol;
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    var id = $('#id_log').val();
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/host_initialize_log/" + id + "/", null, {debug: true});

    socket.onmessage = function (e) {
        var data = $.parseJSON(e.data);
        if (data.message == "update_log") {
            $("#log").val(data.log);
            document.getElementById('log').scrollTop = document.getElementById('log').scrollHeight;
        }
    };

    socket.onopen = function () {
        socket.send("connect success");
    };

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}

$(document).ready(function () {

    init_ws();
    document.getElementById('log').scrollTop = document.getElementById('log').scrollHeight;

});
