var table;
var bar;

$(document).ready(function () {

    table = $('#mytable').DataTable({
        "columns": [
            {
                "className": 'details-control',
                "orderable": false,
                "data": null,
                "defaultContent": '',
            },
            {"data": "project"},  // 1
            {"data": 'room'},  //2
            {"data": 'area'},  //3
            {"data": 'srv_id'},  // 4
            {"data": 'sid'},  // 5
            {"data": "ip"},  // 6
            {"data": "opsmanager"},  // 7
            {"data": "status"},  // 8
            {"data": "remark"},  // 9
        ],
        columnDefs: [
            {
                'targets': 8,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (data, type, full, meta) {
                    return data
                },
            },
            {
                'targets': 9,
                'visible': false,
            },

        ],
        responsive: true,
        language: {
            "url": "/static/js/i18n/Chinese.json"
        },
        ordering: false
    });

    $('#mytable tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child(format(row.data())).show();
            tr.addClass('shown');
        }
    });

    // 初始化进度条
    var settings = {
        strokeWidth: 4,
        easing: 'easeInOut',
        duration: 1400,
        color: '#FCB03C',
        trailColor: '#eee',
        trailWidth: 1,
        svgStyle: {width: '100%', height: '100%'},
        autoStyleContainer: false,
        from: {color: '#FFEA82'},
        to: {color: '#ED6A5A'},
        step: (state, bar) => {
            bar.setText(Math.round(bar.value() * 100) + ' %');
        }
    };
    var status = $('#status').val();
    var total = $('#total').val();
    var finish = $('#finish').val();
    bar = new ProgressBar.Line('#container', settings);
    if (status == 1 || status == 4) {
        bar.animate(0);
    }
    if (status == 3) {
        bar.animate(1);
    }
    if (status == 2) {
        bar.animate(finish / total);
    }

    //手动过滤table中成功或失败的结果
    $("#bt-failed").click(function (event) {
        /* Act on the event */
        table.search('失败').draw();
    });
    $("#bt-success").click(function (event) {
        /* Act on the event */
        table.search('成功').draw();
    });
    $("#bt-clear").click(function (event) {
        /* Act on the event */
        table.search('').draw();
    });

    //初始化websocket
    init_ws();

});


//初始化websocket
function init_ws() {
    var protocol = window.location.protocol;
    var id = $('#obj_id').val();
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/modify_srv_open_time_schedule_detail/" + id + "/", null, {debug: true});

    socket.onmessage = function (e) {
        var data = $.parseJSON(e.data);
        var message = data.message;
        if (message == 'update_detail') {
            window.location.reload(true);
        }
    };

    socket.onopen = function () {
        socket.send("start ws connection");
    };

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}


// datatable children row
function format(d) {
    // `d` is the original data object for the row
    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">' +
        '<tr>' +
        '<td>修改详情:</td>' +
        '<td>' + d.remark + '</td>' +
        '</tr>' +
        '</table>';
}
