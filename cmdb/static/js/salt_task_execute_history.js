var tpl = $("#tpl").html();
var template = Handlebars.compile(tpl);


$(document).ready(function () {

    $('#mytable').DataTable({
        responsive: true,
        language: {
            "url": "/static/js/i18n/Chinese.json"
        },
        ordering: false
    });

});

function view_detail(history_id) {
    $.ajax({
        type: "POST",
        url: "/assets/execute_history_detail/" + history_id + "/",
        data: '',
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            var org_data = data.data;
            $('#task_name').text(org_data['task_name']);
            $('#execute_result').val(org_data['execute_result']);
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
    $('#Modal-execute').modal("show");
}

function view_run_targets(history_id) {

    table = $('#mytable_host').DataTable({
        "destroy": true,
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "searching": true,
        "ajax": {
            "url": "/assets/saltstack_history_host_detail/",
            "type": "POST",
            "data": function (d) {
                d.history_id = history_id;
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": "area"},  //1
            {"data": "belongs_to_game_project"},  // 2
            {"data": "belongs_to_room"},  // 3
            {"data": "belongs_to_business"}, // 4
            {"data": "platform"},  // 5
            {"data": "internal_ip"},  // 6
            {"data": "telecom_ip"},  // 7
            {"data": "unicom_ip"},  // 8
            {"data": "host_comment"},  // 9
            {"data": "execute_status"},  // 10
            {"data": null},  // 11
        ],
        "order": [[0, 'asc']],
        columnDefs: [
            {
                'targets': 0,
                'visible': false,
                'searchable': false
            },
            {
                'targets': 10,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (data, type, full, meta) {
                    if (data == '执行成功') {
                        return '<label class="label label-success">' + data + '</label>'
                    }
                    else {
                        return '<label class="label label-danger">' + data + '</label>'
                    }
                },
            },
            {
                targets: 11,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "查看", "fn": "host_detail(\'" + c.id + "\')", "type": "info"},
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
    });
    $('#Modal-host').modal('show');
}


function host_detail(id) {
    $.ajax({
        type: "POST",
        url: "/assets/execute_history_host_detail/" + id + "/",
        data: '',
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            var org_data = data.data;
            $('#task_name').text(org_data['task_name']);
            $('#execute_result').val(org_data['execute_result']);
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
    $('#Modal-execute').modal("show");
}

