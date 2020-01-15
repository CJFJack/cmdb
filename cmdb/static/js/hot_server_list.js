var table;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var socket;

var is_superuser;

function initModalSelect2() {
    $("#priority").select2();
    $("#status").select2();
    var $select2Status = $("#filter_status").select2();
    var $select2Priority = $("#filter_priority").select2();
    var $select2Project = $("#filter_project").select2();
    var $select2Type = $("#filter_hotupdate_type").select2({
        minimumResultsForSearch: Infinity
    });

    $select2Status.on("select2:select", function (e) {
        log("select2:select", e);
    });
    $select2Priority.on("select2:select", function (e) {
        log("select2:select", e);
    });
    $select2Project.on("select2:select", function (e) {
        log("select2:select", e);
    });
    $select2Type.on("select2:select", function (e) {
        log("select2:select", e);
    });
}

function log(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        table.ajax.reload();

    }
}

function filterColumn(i) {
    $('#mytable').DataTable().column(i).search(
        $('#col' + i + '_filter').val(),
        $('#col' + i + '_regex').prop('checked'),
        $('#col' + i + '_smart').prop('checked')
    ).draw();
}


$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    }
    else {
        return decodeURIComponent(results[1]) || 0;
    }
};


function init_ws() {
    var protocol = window.location.protocol;
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/hot_update/hot_server", null, {debug: true});

    socket.onmessage = function (e) {
        if (e.data == 'update_table') {
            // console.log('reload');
            table.ajax.reload(null, false);
        }
    }

    socket.onopen = function () {
        socket.send("start ws connection");
    }

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}


function edit(id, update_type) {
    editFlag = true;
    var data = {
        'id': id,
        'update_type': update_type,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;

    $.ajax({
        type: "POST",
        url: "/myworkflows/get_hot_server_task/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data;
            $("#myModalLabel").text("修改后端热更新任务");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide();
            $("#project").val(data.project);
            $("#area_name").val(data.area_name);
            $("#update_type").val(data.update_type);
            $("#title").val(data.title);
            $("#priority").val(data.priority_code).trigger('change');
            $("#status").val(data.status_code).trigger('change');
            $("#myModal").modal("show");
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
}


function hotupdate_cmdb_log(uuid) {
    var _url = '/myworkflows/hotupdate_cmdb_log?uuid=' + uuid;
    window.location.href = _url;
}


function show_detail(id) {
    redirect_url = "/myworkflows/host_server_detail?id=" + id;
    window.location.href = redirect_url;
}


function view(id, update_type) {
    redirect_url = "/myworkflows/myworkflow_hotupdate/?id=" + id + '&update_type=' + update_type;
    window.location.href = redirect_url;
}

function execute(id, update_type) {
    var data = {
        'id': id,
        'update_type': update_type,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;


    $.ajax({
        type: "POST",
        url: "/myworkflows/execute_hot_server_task/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data.success) {
                table.ajax.reload(null, false);
            } else {
                alert(data.msg);
                table.ajax.reload(null, false);
            }
        },
        error: function (xhr, status, error) {
            alert('执行失败');
            table.ajax.reload(null, false);
        }
    });
}

function formatRepo(repo) {

    var markup = '<div class="clearfix"><div class="col-sm-7">' + repo.text + '</div></div>';

    return markup;
}


function formatRepoSelection(repo) {
    return repo.text || repo.id;
}


function preFilter() {
    var status = $.urlParam('status');

    if (status !== null) {
        $("#filter_status").val(status).trigger('change');
    }
}


$(document).ready(function () {

    initModalSelect2();

    init_ws();

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/myworkflows/data_hot_server_list/",
            "type": "POST",
            "data": function (d) {
                d.filter_hotupdate_type = $("#filter_hotupdate_type").val();
                d.filter_project = $("#filter_project").val();
                d.filter_area_name = $("#filter_area_name").val();
                d.filter_title = $("#filter_title").val();
                d.filter_priority = $("#filter_priority").val();
                d.filter_status = $("#filter_status").val();
                d.filter_start_time = $("#filter_start_time").val();
                d.filter_end_time = $("#filter_end_time").val();
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": "create_time"},  // 1
            {"data": 'project'},  //2
            {"data": 'area_name'},  //3
            {"data": 'update_type'},  //4
            {"data": 'title'},  // 5
            {"data": 'uuid'},  // 6
            {"data": 'pair_code'},  // 7
            {"data": 'order'},  // 8
            {"data": "priority"},  // 9
            {"data": "status"},  // 10
            {
                "data": null,
                "orderable": false,
            },
            {
                "data": null,
                "orderable": false,
            },
            {
                "data": null,
                "orderable": false,
            },
            {"data": "no_auto_execute_reason"},  // 14
        ],
        "order": [[1, 'asc']],
        columnDefs: [
            {
                'targets': 0,
                'visible': false,
                'searchable': false
            },
            {
                'targets': 14,
                'visible': false,
                'searchable': false
            },
            {
                'targets': 5,
                'width': "10%",
            },
            {
                'targets': 10,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (data, b, c, d) {
                    if (data == '更新成功') {
                        return '<span class="label label-success">' + data + '</span>';
                    } else if (data == '更新中') {
                        return '<span class="label label-info">' + data + '</span>';
                    } else if (data == '更新失败') {
                        return '<span class="label label-danger">' + data + '</span>';
                    } else if (data == '待更新') {
                        return '<div class="tooltip-msg"><span class="label label-warning" data-toggle="tooltip" data-placement="left" title=\"' + c.no_auto_execute_reason + '\">' + data + '</span></div>';
                    } else {
                        return '<span class="label label-default">' + data + '</span>';
                    }
                },
            },
            {
                targets: 11,
                render: function (a, b, c, d) {
                    if (c.update_type == '前端') {
                        if (c.status.indexOf('待更新') !== -1) {
                            var context =
                                {
                                    func: [
                                        {
                                            "name": "修改",
                                            "fn": "edit(\'" + c.id + "\', \'" + c.update_type + "\')",
                                            "type": "primary"
                                        },
                                        {
                                            "name": "执行",
                                            "fn": "execute(\'" + c.id + "\', \'" + c.update_type + "\')",
                                            "type": "success",
                                            "is_disabled": "enabled"
                                        },
                                    ]
                                };
                        } else {
                            var context =
                                {
                                    func: [
                                        {
                                            "name": "修改",
                                            "fn": "edit(\'" + c.id + "\', \'" + c.update_type + "\')",
                                            "type": "primary"
                                        },
                                        {
                                            "name": "执行",
                                            "fn": "execute(\'" + c.id + "\', \'" + c.update_type + "\')",
                                            "type": "success",
                                            "is_disabled": "disabled"
                                        },
                                    ]
                                };
                        }

                    } else {
                        if (c.status.indexOf('待更新') !== -1) {
                            var context =
                                {
                                    func: [
                                        {
                                            "name": "修改",
                                            "fn": "edit(\'" + c.id + "\', \'" + c.update_type + "\')",
                                            "type": "primary"
                                        },
                                        {
                                            "name": "执行",
                                            "fn": "execute(\'" + c.id + "\', \'" + c.update_type + "\')",
                                            "type": "success",
                                            "is_disabled": "enabled"
                                        },
                                        {"name": "更新详细", "fn": "show_detail(\'" + c.id + "\')", "type": "info"},
                                    ]
                                };
                        } else {
                            var context =
                                {
                                    func: [
                                        {
                                            "name": "修改",
                                            "fn": "edit(\'" + c.id + "\', \'" + c.update_type + "\')",
                                            "type": "primary"
                                        },
                                        {
                                            "name": "执行",
                                            "fn": "execute(\'" + c.id + "\', \'" + c.update_type + "\')",
                                            "type": "success",
                                            "is_disabled": "disabled"
                                        },
                                        {"name": "更新详细", "fn": "show_detail(\'" + c.id + "\')", "type": "info"},
                                    ]
                                };
                        }
                    }

                    var html = template(context);
                    return html;
                }
            },
            {
                targets: 12,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {
                                    "name": "查看",
                                    "fn": "view(\'" + c.id + "\', \'" + c.update_type + "\')",
                                    "type": "primary"
                                },
                            ]
                        };
                    var html = template(context);
                    return html;
                }
            },
            {
                targets: 13,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "cmdb", "fn": "hotupdate_cmdb_log(\'" + c.uuid + "\')", "type": "link"},
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
            // tooltip demo
            $('.tooltip-msg').tooltip({
                selector: "[data-toggle=tooltip]",
                container: "body"
            });
        }
    });

    // 翻页后也要重新初始化提示插件
    $('#mytable').on('draw.dt', function () {
        // tooltip demo
        $('.tooltip-msg').tooltip({
            selector: "[data-toggle=tooltip]",
            container: "body"
        });
    });


    preFilter();

    // 设置权限
    is_superuser = $("#is_superuser").data('is-superuser');

    if (!is_superuser) {
        table.column(11).visible(false);
        table.column(13).visible(false);
    }

    $(".flatpickr").flatpickr({
        enableTime: true,
        time_24hr: true,
        locale: "zh",
        /*onChange: function(selectedDates, dateStr, instance){
            table.ajax.reload();
        },*/
        onClose: function (selectedDates, dateStr, instance) {
            table.ajax.reload();
        }
    });


    $(':checkbox.toggle-visiable').on('click', function (e) {
        //e.preventDefault();

        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        // table.ajax.reload();
        column.visible(is_checked);
    });

    $('#bt-modal-notify').click(function () {
        $("#modal-notify").hide();
    });

    $('#chb-all').on('click', function (e) {
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked) {
                $row.addClass('selected');
                count = getSelectedTable().length;
                makeTitle(str, count);
            } else {
                $row.removeClass('selected');
                count = 0;
                makeTitle(str, count);
            }
        });
    });

    $('#mytable tbody').on('click', 'tr', function () {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        }
        else {
            table.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
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
        $("#filter_hotupdate_type").val('全部').trigger('change');
        $("#filter_project").val('全部').trigger('change');
        $("#filter_area_name").val('');
        $("#filter_title").val('');
        $("#filter_priority").val('全部').trigger('change');
        $("#filter_status").val('全部').trigger('change');
        $("#filter_start_time").val('');
        $("#filter_end_time").val('');
        table.ajax.reload();

    });

    $("#bt-refresh").click(function (event) {
        /* Act on the event */

        table.ajax.reload();
    });

    $('#bt-save').click(function () {

        var id = $("#id").val();
        var status = $("#status").select2('data')[0].id;
        var priority = $("#priority").select2('data')[0].id;
        var update_type = $("#update_type").val();

        var inputIds = {
            "id": id,
            "status": status,
            "priority": priority,
            "update_type": update_type,
        };

        var encoded = $.toJSON(inputIds)
        var pdata = encoded

        var urls = '/myworkflows/edit_hot_server_task/'

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {

                if (data['data']) {
                    table.ajax.reload(null, false);
                    $("#myModal").modal("hide");
                } else {
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
                ;
            },
            error: function (data) {
                if (editFlag) {
                    $('#lb-msg').text('你没有修改基础资源权限');
                    $('#modal-notify').show();
                } else {
                    $('#lb-msg').text('你没有增加基础资源权限');
                    $('#modal-notify').show();
                }
            }
        });
    });

    $("#bt-download").click(function (event) {
        /* Act on the event */
        var filter_project = $("#filter_project").val()

        if (filter_project == '全部') {
            alert('请选择游戏项目!')
            return false
        }

        var filter_hotupdate_type = $("#filter_hotupdate_type").val()
        var filter_area_name = $("#filter_area_name").val()
        var filter_title = $("#filter_title").val()
        var filter_priority = $("#filter_priority").val()
        var filter_status = $("#filter_status").val()
        var filter_start_time = $("#filter_start_time").val()
        var filter_end_time = $("#filter_end_time").val()

        var inputIds = {
            'filter_project': filter_project,
            'filter_hotupdate_type': filter_hotupdate_type,
            'filter_area_name': filter_area_name,
            'filter_title': filter_title,
            'filter_priority': filter_priority,
            'filter_status': filter_status,
            'filter_start_time': filter_start_time,
            'filter_end_time': filter_end_time,
        }

        var encoded = $.toJSON(inputIds)
        var pdata = encoded

        _url = '/myworkflows/download_hotupdate/'

        $.ajax({
            type: "POST",
            url: _url,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            beforeSend: function () {
                $("#myModal2").modal("show");
                $("#modal-footer2").hide();
                $("#show-msg2").hide();
                $("#load2").show();
            },
            success: function (data) {
                if (data.success) {
                    $("#load2").hide();
                    $("#modal-footer2").show();
                    $("#load-msg2").text(data.data);
                    $("#show-msg2").show();
                    $("#myModal2").modal("hide");
                    var file_name = data.data;
                    var download_url = '/hotupdate_download/' + file_name;
                    window.location = download_url;
                } else {
                    $("#load2").hide();
                    $("#modal-footer2").show();
                    $("#load-msg2").text(data.data);
                    $("#show-msg2").show();
                }
            },
            error: function () {
                $("#load2").hide();
                $("#modal-footer2").show();
                $("#load-msg2").text('下载失败');
                $("#show-msg2").show();
            }
        });
    });

    $('input.column_filter').on('keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    });


});


function wt_update_notice(id) {
    $("#myModal-update").modal("show");
}