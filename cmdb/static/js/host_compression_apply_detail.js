var table;
var bar;

$(document).ready(function () {

    table = $('#mytable').DataTable({
        columns: [
            {
                "className": 'details-control',
                "orderable": false,
                "data": null,
                "defaultContent": '',
            },
            {"data": "project"},
            {"data": "room"},
            {"data": "business"},
            {"data": "type"},
            {"data": "ip"},
            {"data": "migration_status"},
            {"data": "migration_remark"},
            {"data": "recover_status"},
            {"data": "recover_remark"},
        ],
        columnDefs: [
            {
                'targets': [7, 9],
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

    // 根据类型设置可视列
    var type = $("#id_type").val();
    if (type != 2) {
        table.column(6).visible(false);
    }

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
    var action_status = $('#action_status').val();
    var total = $('#total').val();
    var migration_finish = $('#migration_finish').val();
    var recover_status = $('#recover_status').val();
    var recover_finish = $('#recover_finish').val();
    if (type == 2) {
        bar = new ProgressBar.Line('#action_container', settings);
        if (action_status == 1 || action_status == 4) {
            bar.animate(0);
        }
        if (action_status == 3) {
            bar.animate(1);
        }
        if (action_status == 2) {
            bar.animate(migration_finish / total);
        }
    }

    recover_bar = new ProgressBar.Line('#recover_container', settings);
    if (recover_status == 1 || recover_status == 4) {
        recover_bar.animate(0);
    }
    if (recover_status == 3) {
        recover_bar.animate(1);
    }
    if (recover_status == 2) {
        recover_bar.animate(recover_finish / total);
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

    //提示工具初始化
    $('.tooltip-msg').tooltip({
        selector: "[data-toggle=tooltip]",
        container: "body"
    });

    init_ws();

});


//初始化websocket
function init_ws() {
    var protocol = window.location.protocol;
    var id = $('#apply_id').val();
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/host_compression_detail/" + id + "/", null, {debug: true});

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
        '<td>迁服详情:</td>' +
        '<td>' + d.migration_remark + '</td>' +
        '<td>回收详情:</td>' +
        '<td>' + d.recover_remark + '</td>' +
        '</tr>' +
        '</table>';
}