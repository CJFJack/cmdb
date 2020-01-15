var table;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);
var str = "确定批量操作选中的区服?";
var count = 0;

function initModalSelect2() {
    $(".filter_select2").select2().on("select2:select", function (e) {
        table.ajax.reload();
    });

    var $select2_project2 = $("#filter_project2").select2({});
    var $select2_room2 = $("#filter_room2").select2({});
    var $select2_srv_status2 = $("#filter_srv_status2").select2({});
    $select2_project2.on("select2:select", function (e) {
        table.ajax.reload();
    });
    $select2_room2.on("select2:select", function (e) {
        table.ajax.reload();
    });
    $select2_srv_status2.on("change", function (e) {
        table.ajax.reload();
    });
}


// 开服提示框
function start(id) {
    $('#modalBodyMessgae').text('开服');
    $('#modalSrvId_manager').attr('value', id);
    $('#modalSrvType_action').attr('value', 'start');
    $('#Modal-manager').modal("show");
}

// 关服提示框
function stop(id) {
    $('#modalBodyMessgae').text('关服');
    $('#modalSrvId_manager').attr('value', id);
    $('#modalSrvType_action').attr('value', 'stop');
    $('#Modal-manager').modal("show");
}

// 重启区服提示框
function restart(id) {
    $('#modalBodyMessgae').text('重启区服');
    $('#modalSrvId_manager').attr('value', id);
    $('#modalSrvType_action').attr('value', 'restart');
    $('#Modal-manager').modal("show");
}

// 清档提示框
function clean(id) {
    $('#modalBodyMessgae').text('清档');
    $('#modalSrvId_manager').attr('value', id);
    $('#modalSrvType_action').attr('value', 'clean');
    $('#Modal-manager').modal("show");
}

// 迁服提示框
function migrate(id, srv_id) {
    $('#migrate_srv_id').text(srv_id);
    $('#migrate_game_server_id').val(id);
    $('#Modal-migrate').modal("show");
}

// 单个区服管理操作
function game_server_action() {
    $('#Modal-manager').modal("hide");
    var game_server_id = $('#modalSrvId_manager').attr('value');
    var action_type = $('#modalSrvType_action').attr('value');
    var inputs = {
        'game_server_id': game_server_id,
        'action_type': action_type,
        'batch': false,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/game_server_action/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        async: true,
        success: function (data) {
            if (data['success']) {
                table.ajax.reload(null, false);
            }
            else {
                $('#action_notice_text').text(data['msg']);
                $('#Modal-notice').modal('show');
            }
        },
        error: function (data) {
            alert('内部错误')
        }
    });
}

// 多个区服管理操作提示框
function batch_action(action_type) {
    $('#modalBodyMessgaeBatch').text(str);
    $('#batch_action_type').attr('value', action_type);
    $('#Modal-manager-batch').modal("show");
}

// 多个区服管理操作
function batch_game_server_action() {
    $('#Modal-manager-batch').modal("hide");
    var action_type = $('#batch_action_type').attr('value');
    var selected = getSelectedTable();
    var inputs = {
        'action_type': action_type,
        'game_server_id': selected,
        'batch': true,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    if (selected.length == 0) {
        alert('请勾选需要操作的区服');
    }
    else {
        $.ajax({
            type: "POST",
            url: "/myworkflows/game_server_action/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            async: true,
            success: function (data) {
                if (data['success']) {
                    table.ajax.reload(null, false);
                }
                else {
                    $('#action_notice_text').text(data['msg']);
                    $('#Modal-notice').modal('show');
                }
            },
            error: function (data) {
                alert('内部错误')
            }
        });
    }
}


// 单个区服迁服操作
function game_server_migrate() {
    $('#Modal-migrate').modal("hide");
    var game_server_id = $('#migrate_game_server_id').val();
    var inputs = {
        'game_server_id': game_server_id,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/game_server_migrate/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        async: true,
        success: function (data) {
            if (data['success']) {
                table.ajax.reload(null, false);
            }
            else {
                $('#action_notice_text').text(data['msg']);
                $('#Modal-notice').modal('show');
            }
        },
        error: function (data) {
            alert('内部错误')
        }
    });
}

//初始化websocket链接
function init_ws() {
    var protocol = window.location.protocol;
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/game_server_action/", null, {debug: true});

    socket.onmessage = function (e) {
        var data = $.parseJSON(e.data);
        table.ajax.reload(null, false);
        $('#action_notice_text').html(data['message']);
        $('#Modal-notice').modal('show');
    };

    socket.onopen = function () {
        socket.send("start ws connection");
    };

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}


// 获取区服操作历史记录
function get_history(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/get_game_server_action_history/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data.data;
            console.log(origin_data)
            let record = '';
            for (let i = 0; i < origin_data.length; i++) {
                let log = origin_data[i];
                let operation_time = '<p><span class="text-danger"><strong>' + log['operation_time'] + '</strong></span>';
                let operation_user = '<span class="text-primary"><strong>' + log['operation_user'] + '</strong></span>';
                let operation_type = '<span class="text-default"><strong>' + log['operation_type'] + '</strong></span>';
                let result = '<span class="text-success"><strong>' + log['result'] + '</strong></span></p>';
                let re = new RegExp("\n","g");
                let remark = '<span class="text-muted"><strong>' + log['remark'].replace(re, '<br/>') + '</strong></span></p>';
                record += operation_time + '&nbsp;&nbsp;&nbsp;' + operation_user + '&nbsp;&nbsp;&nbsp;' + operation_type + '&nbsp;&nbsp;&nbsp;' + result + remark
            }
            $('#action_history_content').html(record);
            $("#Modal-history").modal("show");
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


$(document).ready(function () {
    $.fn.select2.defaults.set("theme", "bootstrap");

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "serverSide": true,
        "ordering": false,
        "ajax": {
            "url": "/myworkflows/data_game_server_list/",
            "type": "POST",
            "data": function (d) {
                d.filter_project_type = $("#filter_project_type").select2('data')[0].id;
                d.filter_project = $("#filter_project").select2('data')[0].id;
                d.filter_srv_status = $("#filter_srv_status").select2('data')[0].id;
                d.filter_game_type = $("#filter_game_type").select2('data')[0].id;
                d.filter_pf_name = $("#filter_pf_name").val();
                d.filter_internal_ip = $("#filter_internal_ip").val();
                d.filter_telecom_ip = $("#filter_telecom_ip").val();
                d.filter_unicom_ip = $("#filter_unicom_ip").val();
                d.filter_srv_id = $("#filter_srv_id").val();
                d.filter_srv_name = $("#filter_srv_name").val();
                d.filter_room = $("#filter_room").select2('data')[0].id;
                d.filter_ip = $("#filter_ip").val();
                d.filter_merge_id = $("#filter_merge_id").val();
                d.filter_merge_time = $("#filter_merge_time").val();
                d.filter_client_version = $("#filter_client_version").val();
                d.filter_server_version = $("#filter_server_version").val();
                d.filter_cdn_root_url = $("#filter_cdn_root_url").val();
                d.filter_cdn_dir = $("#filter_cdn_dir").val();
                d.filter_open_time = $("#filter_open_time").val();
                d.filter_area_name = $("#filter_area_name").select2('data')[0].id;
                d.filter_master_server = $("#master_server").is(':checked');
                d.filter_sid = $("#filter_sid").val();
                d.filter_project2 = $("#filter_project2").select2('data')[0].id;
                d.filter_srv_status2 = $("#filter_srv_status2").val();
                d.filter_room2 = $("#filter_room2").select2('data')[0].id;
            }
        },
        "columns": [
            {"data": null}, //0
            {"data": "id"},  // 1
            {"data": "project_type"},  // 2
            {"data": "project"},  // 3
            {"data": "srv_status"},  // 4
            {"data": "game_type"},  // 5
            {"data": "pf_name"},  // 6
            {"data": "srv_id"},  // 7
            {"data": "srv_name"},  // 8
            {"data": "room"},  // 9
            {"data": "ip"},  // 10
            {"data": "merge_id"},  // 11
            {"data": "merge_time"},  // 12
            {"data": "client_version"},  // 13
            {"data": "server_version"},  // 14
            {"data": "cdn_root_url"},  // 15
            {"data": "cdn_dir"},  // 16
            {"data": "open_time"},  // 17
            {"data": "area_name"},  // 18
            {"data": "sid"},  // 19
            {                         //20
                "data": null,
                "orderable": false,
            }
        ],
        "order": [[3, 'asc']],
        columnDefs: [
            {
                'targets': 0,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-center',
                'render': function (data, type, full, meta) {
                    return '<input type="checkbox">';
                },
            },
            {
                'targets': 3,
                width: "6%",
            },
            {
                'targets': 10,
                "width": "13%",
                "render": function (data, type, row) {
                    return data.split(",").join("<br/>");
                },
            },
            {
                'targets': [1, 2, 8, 12, 17, 19],
                'visible': false,
                'searchable': false
            },
            {
                targets: 20,
                width: "14%",
                render: function (a, b, c, d) {
                    if (c.srv_status == '正在开服') {
                        return '<div id="starting_' + c.id + '">' +
                            '<button id="bt_starting_' + c.id + '" class="btn btn-sm btn-success" disabled="true">正在开服</button>' +
                            '<button class="btn btn-sm btn-primary" onclick="get_history(' + c.id + ')">历史记录</button>' +
                            '</div>'
                    }
                    else if (c.srv_status == '正在关服') {
                        return '<div id="stopping_' + c.id + '">' +
                            '<button id="bt_stopping_' + c.id + '" class="btn btn-sm btn-info" disabled="true">正在关服</button>' +
                            '<button class="btn btn-sm btn-primary" onclick="get_history(' + c.id + ')">历史记录</button>' +
                            '</div>'
                    }
                    else if (c.srv_status == '正在重启') {
                        return '<div id="restarting_' + c.id + '">' +
                            '<button id="bt_restarting_' + c.id + '" class="btn btn-sm btn-warning" disabled="true">正在重启</button>' +
                            '<button class="btn btn-sm btn-primary" onclick="get_history(' + c.id + ')">历史记录</button>' +
                            '</div>'
                    }
                    else if (c.srv_status == '正在清档') {
                        return '<div id="cleaning_' + c.id + '">' +
                            '<button id="bt_cleaning_' + c.id + '" class="btn btn-sm btn-danger" disabled="true">正在清档</button>' +
                            '<button class="btn btn-sm btn-primary" onclick="get_history(' + c.id + ')">历史记录</button>' +
                            '</div>'
                    }
                    else if (c.srv_status == '正在刷新') {
                        return '<div id="refreshing_' + c.id + '">' +
                            '<button id="bt_refreshing_' + c.id + '" class="btn btn-sm btn-info" disabled="true">正在清档</button>' +
                            '<button class="btn btn-sm btn-primary" onclick="get_history(' + c.id + ')">历史记录</button>' +
                            '</div>'
                    }
                    else if (c.srv_status == '正在迁服') {
                        return '<div id="migrate_' + c.id + '">' +
                            '<button id="bt_migrate_' + c.id + '" class="btn btn-sm btn-default" disabled="true">正在迁服</button>' +
                            '<button class="btn btn-sm btn-primary" onclick="get_history(' + c.id + ')">历史记录</button>' +
                            '</div>'
                    }
                    else if (c.srv_status in {'注销': '', '关闭平台': ''}) {
                        return '<button type="button" class="btn btn-sm btn-primary" onclick="get_history(' + c.id + ')">历史记录</button>'
                    }
                    else if (c.srv_status == '正常'){
                        return '<div class="btn-group" id="bt_group_' + c.id + '">' +
                            '<button type="button" class="btn btn-success btn-sm dropdown-toggle" data-toggle="dropdown">' +
                            '操作' +
                            '<span class="caret"></span>' +
                            '</button>' +
                            '<ul class="dropdown-menu pull-right" role="menu">' +
                            '<li><a id="start_' + c.id + '" onclick="start(' + c.id + ')">开服</a>' +
                            '</li>' +
                            '<li><a id="stop_' + c.id + '" onclick="stop(' + c.id + ')">关服</a>' +
                            '</li>' +
                            '<li><a id="restart_' + c.id + '" onclick="restart(' + c.id + ')">重启</a>' +
                            '</li>' +
                            '<li><a id="clean_' + c.id + '" onclick="clean(' + c.id + ')">清档</a>' +
                            '</li>' +
                            '<li><a id="migrate_' + c.id + '" onclick="migrate(\'' + c.id + '\',\'' + c.srv_id + '\')">迁服</a>' +
                            '</li>' +
                            '</ul>' +
                            '</div>&nbsp;' +
                            '<button type="button" class="btn btn-sm btn-primary" onclick="get_history(' + c.id + ')">历史记录</button>'
                    }
                    else {
                        return '<div id="refreshing_' + c.id + '">' +
                            '<button id="bt_refreshing_' + c.id + '" class="btn btn-sm btn-default" disabled="true">' + c.srv_status + '</button>' +
                            '<button class="btn btn-sm btn-primary" onclick="get_history(' + c.id + ')">历史记录</button>' +
                            '</div>'
                    }
                }
            }
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });

    // 设置权限
    is_superuser = $("#is_superuser").data('is-superuser');

    if (!is_superuser) {
        table.column(19).visible(false);
        table.column(20).visible(false);
    }

    initModalSelect2();

    // Handle click on checkbox
    $('#mytable tbody').on('click', 'input[type="checkbox"]', function (e) {
        var $row = $(this).closest('tr');

        var data = table.row($row).data();
        var index = $.inArray(data[0], rows_selected);

        if (this.checked && index === -1) {
            rows_selected.push(data[0]);
        } else if (!this.checked && index !== -1) {
            rows_selected.splice(index, 1);
        }

        if (this.checked) {
            $row.addClass('selected');
            //makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            //makeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    $('input.column_filter').on('keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    });

    $("#master_server").click(function () {
        table.ajax.reload();
    });

    $('#chb-all').on('click', function (e) {
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked) {
                $row.addClass('selected');
                count = getSelectedTable().length;
                //makeTitle(str, count);
            } else {
                $row.removeClass('selected');
                count = 0;
                //makeTitle(str, count);
            }
        });

    });

    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $("#bt-reset").click(function () {
        // 重置高级搜索
        $("#filter_project").val('0').trigger('change');
        $("#filter_project_type").val('100').trigger('change');
        $("#filter_srv_status").val('100').trigger('change');
        $("#filter_game_type").val('0').trigger('change');
        $(".column_filter").val('');
        $("#filter_area_name").val('0').trigger('change');
        $("#filter_room").val('0').trigger('change');
        table.ajax.reload();

    });


    $('#bt-save').click(function () {

        var id = $("#id").val();
        var project_name = $("#project_name").val();
        var project_name_en = $("#project_name_en").val();
        var svn_repo = $("#svn_repo").val();
        var group = $("#group").val();
        var leader = $("#leader").select2('data')[0].id;
        var status = $("#status").select2('data')[0].id;

        var inputIds = {
            "id": id,
            "project_name": project_name,
            "project_name_en": project_name_en,
            "svn_repo": svn_repo,
            "leader": leader,
            "group": group,
            "status": status,
            "editFlag": editFlag,
        };

        var encoded = $.toJSON(inputIds)
        var pdata = encoded

        urls = '/assets/add_or_edit_game_project/';

        if (!checkBeforeAdd(project_name, project_name_en)) {
            return false;
        }

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
            }
        });
    });

    $(':checkbox.toggle-visiable').on('click', function (e) {
        //e.preventDefault();

        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        // table.ajax.reload();
        column.visible(is_checked);
    });

    init_ws();

});
