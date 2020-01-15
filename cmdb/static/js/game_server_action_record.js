var table;

$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    }
    else {
        return decodeURIComponent(results[1]) || 0;
    }
};

function preFilter() {
    var filter_status = $.urlParam('status');

    if (filter_status !== null) {
        $("#filter_status").val(filter_status).trigger('change');
    }
}


$(document).ready(function () {
    $.fn.select2.defaults.set("theme", "bootstrap");

    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/myworkflows/data_game_server_action_record/",
            "type": "POST",
            "data": function (d) {
                d.filter_uuid = $('#filter_uuid').val();
                d.filter_project = $('#filter_project').select2('data')[0].id;
                d.filter_game_server = $('#filter_game_server').val();
                d.filter_status = $('#filter_status').select2('data')[0].id;
                d.filter_start_operation_time = $('#filter_start_operation_time').val();
                d.filter_end_operation_time = $('#filter_end_operation_time').val();
                d.filter_operation_user = $('#filter_operation_user').select2('data')[0].id;
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": 'area'},  // 1
            {"data": 'project'},  //2
            {"data": 'srv_id'},  //3
            {"data": "operation_type"},  // 4
            {"data": "uuid"},  // 5
            {"data": "operation_user"},  // 6
            {"data": "operation_time"},  // 7
            {"data": "source_ip"},  // 8
            {"data": "result"},  // 9
            {"data": "remark"}, //10
        ],
        columnDefs: [
            {
                'targets': 0,
                'visible': false,
                'searchable': false
            },
            {
                'targets': 4,
                render: function (data, type, row, meta) {
                    if (data == '开服') {
                        return '<label class="label label-success">' + data + '</label>'
                    }
                    else if (data == '关服') {
                        return '<label class="label label-info">' + data + '</label>'
                    }
                    else if (data == '重启') {
                        return '<label class="label label-warning">' + data + '</label>'
                    }
                    else if (data == '清档') {
                        return '<label class="label label-danger">' + data + '</label>'
                    }
                    else if (data == '新增') {
                        return '<label class="alert-success">' + data + '</label>'
                    }
                    else if (data == '修改') {
                        return '<label class="alert-info">' + data + '</label>'
                    }
                    else if (data == '删除') {
                        return '<label class="alert-danger">' + data + '</label>'
                    }
                    else {
                        return '<label class="label label-default">' + data + '</label>'
                    }
                }
            },
            {
                'targets': 9,
                render: function (data, type, row, meta) {
                    if (data == '执行失败') {
                        return '<label class="label label-danger">' + data + '</label>'
                    }
                    else if (data == '执行成功') {
                        return '<label class="label label-success">' + data + '</label>'
                    }
                    else if (data == '执行中') {
                        return '<label class="label label-primary">' + data + '</label>'
                    }
                    else {
                        return '<label class="label label-default">' + data + '</label>'
                    }
                }
            },
            {
                'targets': 10,
                width: '20%',
                render: function (data, type, row, meta) {
                    let num = 20;
                    if (data.length > num) {
                        return '<span class="tooltip-demo"><span data-toggle="tooltip" data-html="true" data-placement="left" title="' + data.split("\n").join("<br>") + '">' + data.substring(0, num) + '...' + '</span></span>'
                    }
                    else {
                        return data.split("\n").join("<br/>");
                    }
                }
            }
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
        initComplete: function () {
            // tooltip demo
            $('.tooltip-demo').tooltip({
                selector: "[data-toggle=tooltip]",
                container: "body",
            })
        }
    });

    preFilter();

    // 翻页后也要重新初始化提示插件
    $('#mytable').on('draw.dt', function () {
        // tooltip demo
        $('.tooltip-demo').tooltip({
            selector: "[data-toggle=tooltip]",
            container: "body"
        })
    });

    $('input.column_filter').on('keyup click', function () {
        table.ajax.reload();
    });

    $(".filter_select2").select2({}).on("select2:select", function (e) {
        table.ajax.reload();
    });

    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $('input.column_filter').on('keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    });

    $("#bt-reset").click(function () {
        // 重置高级搜索
        $("#filter_uuid").val('');
        $("#filter_game_server").val('');
        $(".filter_select2").val('全部').trigger('change');
        $(".flatpickr").val('');
        table.ajax.reload();

    });

    //初始化websocket链接
    init_ws();

    // 时间插件初始化
    $(".flatpickr").flatpickr({
        locale: "zh",
        enableTime: true,
        time_24hr: true,
        onChange: function () {
            table.ajax.reload();
        }
    });

});


//初始化websocket链接
function init_ws() {
    var protocol = window.location.protocol;
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/game_server_action_record/", null, {debug: true});

    socket.onmessage = function (e) {
        table.ajax.reload(null, false);
    };

    socket.onopen = function () {
        socket.send("start ws connection");
    };

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}
