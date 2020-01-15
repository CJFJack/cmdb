var $select2Area;
var $select2Project;
var $select2Room;
var table;
var str = "确定对选中的主机执行任务?";
var count = 0;
var rows_selected = [];

// 开始执行salt任务
function start_execute() {
    var execute_task_id = $('#execute_task_id').val();
    var selected = getSelectedTable();
    inputs = {
        'execute_task_id': execute_task_id,
        'selected_host': selected,
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

// 清空执行结果输出
function clear_result() {
    $('#execute_result').val('')
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


function initModalSelect2() {
    $select2Area = $("#id_area").select2({
        ajax: {
            url: '/assets/list_area/',
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
                var result_data = $.map(data, function (item) {
                    return {
                        id: item.id,
                        text: item.text,
                    }
                });
                result_data.unshift({"id": "0", "text": "全部"});
                return {
                    results: result_data
                };
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '请选择地区',
    }).on("select2:select", function (e) {
        table.ajax.reload()
    });

    $select2Project = $("#id_project").select2({
        ajax: {
            url: '/myworkflows/list_game_project_by_area/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term,
                    page: params.page,
                    area_id: $('#id_area').val(),
                };
            },

            processResults: function (data, params) {
                params.page = params.page || 1;
                var result_data = $.map(data, function (item) {
                    return {
                        id: item.id,
                        text: item.text,
                    }
                });
                result_data.unshift({"id": "全部", "text": "全部"});
                return {
                    results: result_data
                }
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '请选择游戏项目',
    }).on("select2:select", function (e) {
        table.ajax.reload()
    });

    $select2Room = $("#id_room").select2({
        ajax: {
            url: '/myworkflows/list_room_name_by_project_and_area/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term,
                    page: params.page,
                    project: $('#id_project').val(),
                    area: $('#id_area').val(),
                };
            },

            processResults: function (data, params) {
                params.page = params.page || 1;
                var result_data = $.map(data, function (item) {
                    return {
                        id: item.id,
                        text: item.text,
                    }
                });
                result_data.unshift({"id": "全部", "text": "全部"});
                return {
                    results: result_data
                }
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '请选择机房',
    }).on("select2:select", function (e) {
        table.ajax.reload()
    });

}


$(document).ready(function () {

    // 初始化websocket连接
    init_ws();
    //初始化下拉框
    initModalSelect2();

    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        // "serverSide": true,
        "paging": false,
        "searching": true,
        "ajax": {
            "url": "/assets/saltstack_data_host/",
            "type": "POST",
            "data": function (d) {
                d.filter_area = $("#id_area").val();
                d.filter_project = $("#id_project").val();
                d.filter_room = $("#id_room").val();
            }
        },
        "columns": [
            {"data": null},  // 0
            {"data": "id"},  // 1
            {"data": "area"},  //2
            {"data": "belongs_to_game_project"},  // 3
            {"data": "belongs_to_room"},  // 4
            {"data": "status"},  // 5
            {"data": "belongs_to_business"}, // 6
            {"data": "platform"},  // 7
            {"data": "internal_ip"},  // 8
            {"data": "telecom_ip"},  // 9
            {"data": "unicom_ip"},  // 10
            {"data": "host_comment"},  // 11
        ],
        "order": [[1, 'asc']],
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
                'targets': 1,
                'visible': false,
                'searchable': false
            },
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });

    $(':checkbox.toggle-visiable').on('click', function (e) {
        //e.preventDefault();

        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        // table.ajax.reload();
        column.visible(is_checked);
    });

    $('#chb-all').on('click', function (e) {
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked) {
                $row.addClass('selected');
            } else {
                $row.removeClass('selected');
            }
        });
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
        } else {
            $row.removeClass('selected');
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    $('#bt-commit').click(function () {
        var selected = getSelectedTable();

        if (selected.length == 0) {
            alert('请选择主机');
        } else {
            var encoded = $.toJSON(selected);
            var pdata = encoded;
            $('#Modal-execute-host').modal('show');
        }
    })

});