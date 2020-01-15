var table;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);


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
            "url": "/ops/data_game_server_off_list/",
            "type": "POST",
            "data": function (d) {
                d.filter_web_callback_url = $('#filter_web_callback_url').val();
                d.filter_status = $('#filter_status').select2('data')[0].id;
                d.filter_project = $('#filter_project').select2('data')[0].id;
                d.filter_game_server = $('#filter_game_server').val();
                d.filter_start_create_time = $('#filter_start_create_time').val();
                d.filter_end_create_time = $('#filter_end_create_time').val();
                d.filter_start_off_time = $('#filter_start_off_time').val();
                d.filter_end_off_time = $('#filter_end_off_time').val();
                d.filter_uuid = $('#filter_uuid').val();
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": 'create_time'},  //1
            {"data": 'uuid'},  //2
            {"data": 'off_time'},  //3
            {"data": 'off_srv'}, //4
            {"data": 'status_text'},  //5
            {"data": 'web_callback_url'},  //6
            {
                "data": null,        //7
                "orderable": false,
            },
            // {
            //     "data": null,        //8
            //     "orderable": false,
            // },
            {"data": null},  //8
        ],
        columnDefs: [
            {
                'targets': 0,
                'visible': false,
                'searchable': false
            },
            {
                'targets': 4,
                render: function (data) {
                    return data.split(',').join('<br/>')
                }
            },
            {
                'targets': 5,
                render: function (a, b, c, d) {
                    if (c.status_text == '正在执行') {
                        var status_class = 'info';
                        return '<label class="label label-' + status_class + '">' + c.status_text + '</label>'
                    }
                    else if (c.status_text == '取消') {
                        var status_class = 'default';
                        return '<label class="label label-' + status_class + '">' + c.status_text + '</label>'
                    }
                    else if (c.status_text == '下线成功') {
                        var status_class = 'success';
                        return '<label class="label label-' + status_class + '">' + c.status_text + '</label>'
                    }
                    else {
                        let attr = '';
                        for (let i of c.off_srv_detail.split(',')) {
                            let Iresult = i.split('-')[0];
                            let Iremark = i.split('-')[1];
                            if (Iresult == '未执行') {
                                attr += '<label class="label label-warning">' + Iresult + '</label><br/>'
                            }
                            if (Iresult == '下线成功') {
                                attr += '<label class="label label-success">' + Iresult + '</label><br/>'
                            }
                            if (Iresult == '下线失败') {
                                attr += '<span class="tooltip-demo text-danger"><label class="label label-danger" data-toggle="popover" data-placement="right" disabled title="' + Iremark + '">' + Iresult + '</label><br/>'
                            }
                        }
                        return attr;
                    }
                }
            },
            {
                targets: 7,
                width: "10%",
                render: function (a, b, c, d) {
                    if (c.status_text == '未执行') {
                        var context =
                            {
                                func: [
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                    {"name": "执行", "fn": "execute_confirm(\'" + c.id + "\')", "type": "danger"},
                                ]
                            };
                        var html = template(context);
                        return html;
                    }
                    else {
                        var context =
                            {
                                func: [
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                ]
                            };
                        var html = template(context);
                        return html;
                    }
                }
            },
            // {
            //     targets: 8,
            //     render: function (a, b, c, d) {
            //         var context =
            //             {
            //                 func: [
            //                     {"name": "查看", "fn": "detail(\'" + c.id + "\')", "type": "info"},
            //                 ]
            //             };
            //         var html = template(context);
            //         return html;
            //     }
            // },
            {
                targets: 8,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "cmdb", "fn": "log(\'" + c.id + "\')", "type": "link"},
                            ]
                        };
                    var html = template(context);
                    return html;
                }
            }
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
        "initComplete": function (settings, json) {
            // popover demo
            $("[data-toggle=popover]")
                .popover()
        }
    });

    preFilter();

    // 翻页后也要重新初始化提示插件
    $('#mytable').on('draw.dt', function () {
        // popover demo
        $("[data-toggle=popover]")
            .popover()
    });

    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $('input.column_filter').on('keyup click', function () {
        table.ajax.reload();
    });

    $(".filter_select2").select2({}).on("select2:select", function (e) {
        table.ajax.reload();
    });

    $("#bt-reset").click(function () {
        // 重置高级搜索
        $("#filter_web_callback_url").val('');
        $("#filter_uuid").val('');
        $("#filter_game_server").val('');
        $(".filter_select2").val('全部').trigger('change');
        $(".flatpickr").val('');
        table.ajax.reload();
    });

    // 时间插件初始化
    $(".flatpickr").flatpickr({
        locale: "zh",
        enableTime: true,
        time_24hr: true,
        onChange: function () {
            table.ajax.reload();
        }
    });

    //初始化select2
    initModalSelect2();
    //初始化websocket
    init_ws()

});


function initModalSelect2() {
    $select2EditStatus = $("#edit_status").select2({
        ajax: {
            url: '/ops/list_game_server_off_status/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term,
                    page: params.page
                };
            },

            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                }
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '任务状态',
    });
}


// 查看主机回收/迁服申请详细页面
function detail(id) {
    window.location.href = '/ops/game_server_off_detail/' + id + '/';
}

//修改任务状态函数
function edit(id) {
    $('#modal-notify').hide();
    var inputIds = {
        'id': id,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/ops/get_data_game_server_off/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            if (data.success) {
                $('#myModalLabel').text('修改-' + data.uuid);
                initSelect2('edit_status', data.status_id, data.status_text);
                $('#edit_off_time').val(data.off_time);
                $('#id_edit').attr('value', id);
                $('#myModal').modal('show');
            }
            else {
                alert(data.msg)
            }
        },
        error: function (data) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
}


//保存修改任务状态
function save() {
    var id = $('#id_edit').val();
    var status = $('#edit_status').val();
    var off_time = $('#edit_off_time').val();
    var inputIds = {
        'id': id,
        'status': status,
        'off_time': off_time,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/ops/edit_game_server_off/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            if (data.success) {
                table.ajax.reload(null, false);
                $('#myModal').modal('hide');
            }
            else {
                alert(data.msg)
            }
        },
        error: function (data) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });

}


//执行任务确认弹窗
function execute_confirm(id) {
    $('#id_execute').attr('value', id);
    $('#id_confirm').text('确认要手动执行下线操作吗？');
    $('#myModal2').modal('show');
}


//执行任务
function execute() {
    var id = $('#id_execute').val();
    var inputIds = {
        'id': id,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/ops/execute_game_server_off/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        beforeSend: function () {
            $('#myModal2').modal('hide');
        },
        success: function (data) {
            if (data.success) {
                table.ajax.reload(null, false);
                $('#id_notice').text(data.msg);
                $('#myModal3').modal('show');
            }
            else {
                $('#id_notice').text(data.msg);
                $('#myModal3').modal('show');
            }
        },
        error: function (data) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
}

//初始化websocket
function init_ws() {
    var protocol = window.location.protocol;
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/game_server_off_list/", null, {debug: true});

    socket.onmessage = function (e) {
        var data = $.parseJSON(e.data);
        if (data.message == "update_table") {
            table.ajax.reload(null, false);
        }
    };

    socket.onopen = function () {
        socket.send("start ws connection");
    };

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}

// 跳转日志页面
function log(id) {
    var _url = '/ops/game_server_off_cmdb_log/' + id + '/';
    window.open(_url);
}