var table;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);
var str = "确定发送选中的任务吗?";
var count = 0;
var rows_selected = [];


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
    var status = $.urlParam('status');

    if (status !== null) {
        $("#filter_status").val(status).trigger('change');
    }
}

$(document).ready(function () {
    $.fn.select2.defaults.set("theme", "bootstrap");

    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/ops/data_game_server_merge_list/",
            "type": "POST",
            "data": function (d) {
                d.filter_project = $('#filter_project').select2('data')[0].id;
                d.filter_room = $('#filter_room').select2('data')[0].id;
                d.filter_status = $('#filter_status').select2('data')[0].id;
                d.filter_main_srv = $('#filter_main_srv').val();
                d.filter_slave_srv = $('#filter_slave_srv').val();
                d.filter_group_id = $('#filter_group_id').val();
            }
        },
        "columns": [
            {"data": null},  // 0
            {"data": "id"},  // 1
            {"data": "uuid"},  // 2
            {"data": 'project'},  //3
            {"data": 'room'},  //4
            {"data": 'main_srv'}, //5
            {"data": 'slave_srv'},  //6
            {"data": 'group_id'},  //7
            {"data": 'merge_time'},  //8
            {"data": 'status'},  //9
            {
                "data": null,        //10
                "orderable": false,
            },
        ],
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
            {
                targets: 9,
                render: function (a, b, c, d) {
                    if (c.status == '未发送') {
                        return '<label class="label label-default">' + c.status + '</label>'
                    }
                    else if (c.status == '合服-发送成功' || c.status == '回滚-发送成功') {
                        return '<label class="label label-success">' + c.status + '</label>'
                    }
                    else if (c.status == '合服-发送失败' || c.status == '回滚-发送失败') {
                        return '<span class="tooltip-demo"><label class="label label-danger" data-toggle="tooltip" data-placement="left" title="' + c.remark + '">' + c.status + '</label></span>';
                    }
                    else {
                        return c.status
                    }
                }
            },
            {
                targets: 10,
                render: function (a, b, c, d) {
                    if (c.status == '未发送' || c.status == '合服-发送失败') {
                        var context =
                            {
                                func: [
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "info"},
                                    {"name": "合服", "fn": "send(\'" + c.id + "\')", "type": "success"},
                                ]
                            };
                        var html = template(context);
                    }
                    else if (c.status == '回滚-发送失败' || c.status == '合服-发送成功') {
                        var context =
                            {
                                func: [
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "info"},
                                    {"name": "回滚", "fn": "rollback(\'" + c.id + "\')", "type": "danger"},
                                ]
                            };
                        var html = template(context);
                    }
                    else {
                        var context =
                            {
                                func: [
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "info"},
                                ]
                            };
                        var html = template(context);
                    }
                    return html;
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
                container: "body"
            })
        }
    });


    // 翻页后也要重新初始化提示插件
    $('#mytable').on('draw.dt', function () {
        // tooltip demo
        $('.tooltip-demo').tooltip({
            selector: "[data-toggle=tooltip]",
            container: "body"
        })
    });


    $(':checkbox.toggle-visiable').on('click', function (e) {
        //e.preventDefault();

        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        // table.ajax.reload();
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
            makeMergeSrvTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            makeMergeSrvTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });


    $('#chb-all').on('click', function (e) {
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked) {
                $row.addClass('selected');
                count = getSelectedTable().length;
                makeMergeSrvTitle(str, count);
            } else {
                $row.removeClass('selected');
                count = 0;
                makeMergeSrvTitle(str, count);
            }
        });

    });


    // 设置权限
    is_superuser = $("#is_superuser").data('is-superuser');
    if (is_superuser == "False") {
        table.column(8).visible(false);
    }

    var $select2_project = $("#filter_project").select2({});
    var $select2_room = $("#filter_room").select2({});
    var $select2_status = $("#filter_status").select2({});
    $select2_project.on("select2:select", function (e) {
        table.ajax.reload();
    });
    $select2_room.on("select2:select", function (e) {
        table.ajax.reload();
    });
    $select2_status.on("select2:select", function (e) {
        table.ajax.reload();
    });

    $('input.column_filter').on('keyup click', function () {
        table.ajax.reload();
    });

    preFilter();

    $('#bt-save').click(function () {
        var id = $('#id_edit').val();
        var status = $('#edit_status').val();
        var inputIds = {
            'id': id,
            'status': status,
        };
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/ops/edit_game_server_merge_status/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                $('#myModal').modal('hide');
                if (data.success) {
                    table.ajax.reload(null, false);
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
    });


    //合服
    $("#bt-merge").confirm({
        confirm: function (button) {
            var selected = {
                'id': getSelectedTable()
            };

            if (selected.id.length == 0) {
                alert('请选择');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/ops/execute_game_server_merge_schedule/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            table.ajax.reload(null, false);
                            makeMergeSrvTitle(str, 0);
                            count = 0;
                        } else {
                            alert(data['msg']);
                            table.ajax.reload();
                            makeMergeSrvTitle(str, 0);
                            count = 0;
                        }
                    }
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });


    //回滚合服
    $("#bt-mergecallback").confirm({
        confirm: function (button) {
            var selected = {
                'id': getSelectedTable()
            };

            if (selected.id.length == 0) {
                alert('请选择');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/ops/rollback_game_server_merge_schedule/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            table.ajax.reload(null, false);
                            makeMergeSrvTitle(str, 0);
                            count = 0;
                        } else {
                            alert(data['msg']);
                            table.ajax.reload();
                            makeMergeSrvTitle(str, 0);
                            count = 0;
                        }
                    }
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

});


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
        url: "/ops/get_edit_data_game_server_merge/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            if (data.success) {
                $('#myModalLabel').text('修改状态');
                $('#id_edit').val(id);
                $('#edit_status').val(data.status_id);
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


// 发送运维管理机执行合服计划
function send(id) {
    var choice = confirm("确认发送合服计划？");
    if (choice == true) {
        var inputIds = {
            'id': id,
        };
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/ops/execute_game_server_merge_schedule/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.success) {
                    alert('发送合服计划成功')
                }
                else {
                    alert(data.msg)
                }
                table.ajax.reload(null, false);
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
}


// 发送运维管理机回滚合服计划
function rollback(id) {
    var choice = confirm("确认要回滚合服？");
    if (choice == true) {
        var inputIds = {
            'id': id,
        };
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/ops/rollback_game_server_merge_schedule/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.success) {
                    alert('发送回滚合服计划成功')
                }
                else {
                    alert(data.msg)
                }
                table.ajax.reload(null, false);
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
}
