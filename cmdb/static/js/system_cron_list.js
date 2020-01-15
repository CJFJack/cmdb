var table;
var str = "确定删除选中的salt任务?";
var count = 0;

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
        table.search(filter_status).draw();
    }
}

$(document).ready(function () {

    var rows_selected = [];
    table = $('#mytable').DataTable({
        columns: [
            {},
            {"data": "id"},
            {"data": "task_name"},
            {"data": "task_status"},
            {"data": "filename"},
            {"data": "push_path"},
            {},
            {"data": "modified_user"},
            {"data": "modified_time"},
            {},
            {"data": "release_user"},
            {"data": "release_time"},
            {},
            {"data": "execute_user"},
            {"data": "execute_time"},
            {"data": "execute_result"},
        ],
        columnDefs: [
            {
                'targets': [0, 3, 6, 7, 9, 10, 12, 13, 15],
                'orderable': false,
            },
            {
                'targets': [7, 10, 11, 13],
                'visible': false,
            }
        ],
        order: [[1, 'asc']],
        responsive: true,
        language: {
            "url": "/static/js/i18n/Chinese.json"
        },
        ordering: true,
        "initComplete": function (settings, json) {
            var specific_page = parseInt($('#specific_page').val());
            table.page(specific_page).draw(false);
        },
        "fnDrawCallback": function (oSettings) {
            var current_page = table.page.info().page;
            $('#current_page').val(current_page);
            $('#current_page2').val(current_page);
        }
    });

    preFilter();


    $(':checkbox.toggle-visiable').on('click', function (e) {
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        column.visible(is_checked);
    });

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
            makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            makeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    // 全选table checkbox
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

    //删除
    $("#bt-del").confirm({
        //text:"确定删除所选的saltstack任务?",
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请先勾选需要删除的任务');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/delete_salt_task/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            location.reload();
                        } else {
                            alert(data['msg']);
                        }
                    },
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    // 发送推送文件命令
    $('#push_confirm').click(function () {
        var config_id = $('#push_filename_id').val();
        var inputs = {
            'config_id': config_id,
        };
        var encoded = $.toJSON(inputs);
        var pdata = encoded;
        // 检验需要字段是否为空

        $('#Modal-push').modal('hide');
        $('#bt-push-' + config_id).text('正在推送...');
        $('#bt-push-' + config_id).attr('class', 'btn btn-sm btn-info');
        $('#bt-push-' + config_id).prop('disabled', true);
        $.ajax({
            type: "POST",
            url: "/assets/salt_config_push/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            async: true,
            success: function (data) {
                if (data['success']) {
                    $('#push-result').text(data['msg']);
                    $('#bt-push-' + config_id).text(data['msg']);
                    $('#bt-push-' + config_id).prop('disabled', true);
                    $('#bt-push-' + config_id).attr('class', 'btn btn-sm btn-success');
                    $('#ready_execute-' + config_id).attr("disabled", false);
                    $('#Modal-result').modal('show');
                }
                else {
                    $('#bt-push-' + config_id).text(data['msg']);
                    $('#bt-push-' + config_id).attr('class', 'btn btn-sm btn-danger');
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
    });

    // 同步pillar
    $("#sync_pillar").confirm({
        confirm: function (button) {
            $('#sync_pillar').text('刷新中，请勿刷新页面');
            $('#sync_pillar').attr('disabled', true);
            $.ajax({
                type: "POST",
                url: "/assets/sync_pillar/",
                contentType: "application/json; charset=utf-8",
                async: true,
                success: function (data) {
                    if (data['data']) {
                        alert(data['msg']);
                    } else {
                        alert(data['msg']);
                    }
                    $('#sync_pillar').text('刷新pillar配置');
                    $('#sync_pillar').attr('disabled', false);
                }
            });
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

});

// 编辑任务
function edit(config_id) {
    $.ajax({
        type: "POST",
        url: "/assets/salt_config/" + config_id + "/",
        data: '',
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            var org_data = data.data;
            $('#status_enable').removeAttr('checked');
            $('#status_disable').removeAttr('checked');
            if (org_data['status'] == 1) {
                $('#status_enable').prop("checked", "checked");
            }
            if (org_data['status'] == 0) {
                $('#status_disable').prop("checked", "checked");
            }
            $('#config_id').attr("value", org_data['config_id']);
            $('#task_name').attr("value", org_data['task_name']);
            $('#filename').attr("value", org_data['filename']);
            $('#content').attr("value", org_data['content']);
            $('#push_path').attr("value", org_data['push_path']);
            $('#task_name').text(org_data['task_name']);
            $('#filename').text(org_data['filename']);
            $('#content').val(org_data['content']);
            $('#push_path').val(org_data['push_path']);
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
    $('#Modal-edit').modal("show");
}


// 弹出推送配置文件确认框并初始化需要提交推送的字段
function push(config_id, filename) {
    $('#push_filename').text(filename);
    $('#push_filename_id').attr('value', config_id);
    $('#push_filename_path').attr('value', push_path);
    $('#push_content').attr('value', content);
    $('#Modal-push').modal('show');
}


function init_ws() {
    var protocol = window.location.protocol;
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/execute_salt_task/", null, {debug: true});

    socket.onmessage = function (e) {
        var data = $.parseJSON(e.data);
        //alert(data['message']);
        var execute_result = $('#execute_result').val();
        var execute_result = execute_result + data['message'] + '\n';
        $('#execute_result').val(execute_result);
    };

    socket.onopen = function () {
        socket.send("start ws connection");
    };

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}


// 开始执行salt任务
function start_execute() {
    var execute_task_id = $('#execute_task_id').attr('value');
    inputs = {
        'execute_task_id': execute_task_id,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/start_execute_salt_task/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        async: true,
        success: function (data) {
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


// 新增salt任务
function add_salt_task() {
    $('#Modal-Add').modal('show');
}
