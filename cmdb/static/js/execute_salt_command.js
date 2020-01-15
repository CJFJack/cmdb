var socket;

//初始化websocket
function init_ws() {
    var protocol = window.location.protocol;
    var uuid = $('#execute_command_uuid').val();
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/execute_salt_command/" + uuid + "/", null, {debug: true});

    socket.onmessage = function (e) {
        var data = $.parseJSON(e.data);
        var content = data['message'];
        var output = $('#output').html();
        var output = output + '<p>' + content + '</p>';
        $('#output').html(output);
    };

    socket.onopen = function () {
        socket.send("start ws connection");
    };

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}


$(document).ready(function () {

    init_ws();

    $('#submit_command').click(function () {
        var salt_command = $('#salt_command').val();
        var uuid = $('#execute_command_uuid').val();
        var data = {
            'salt_command': salt_command,
            'uuid': uuid
        };
        var encoded = $.toJSON(data);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/assets/execute_salt_command/",
            data: pdata,
            async: true,
            contentType: "application/json; charset=utf-8",
            beforeSend: function(data) {
                $('#output').html('<p style="color: #1e96d2;">提交成功，请勿刷新页面，耐心等待结果！</p>')
            },
            success: function (data) {
                if (!data['success']) {
                    var output = $('#output').html();
                    output = output + '<p class="text-danger">' + data['msg'] + '</p>';
                    $('#output').html(output);
                }
            },
            error: function (xhr, status, error) {
                if (xhr.status == '403') {
                    alert('权限拒绝');
                } else {
                    alert('内部错误');
                }
            }
        });
    })

});
