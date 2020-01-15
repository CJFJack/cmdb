var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的申请?";
var count = 0;


function view(id) {
    var redirect_url = '/myworkflows/myworkflow_history?id=' + id;
    window.location.href = redirect_url;
};


function mail(id) {
    var wse = id
    var encoded = $.toJSON(wse);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/send_mail_for_wse/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            if (data['success']) {
                table.ajax.reload();
            } else {
                alert(data['data'])
                table.ajax.reload();
            }
            ;
        }
    });
};

// 更换审批人
function change_approve(id, workflow) {
    var _url = '/myworkflows/change_approve/?id=' + id;
    window.location.href = _url;
}

// 我的热更新
function myhotupdate(id, workflow) {
    var _url = '/myworkflows/myhotupdate/?id=' + id;
    var win = window.open(_url, '_blank');
    if (win) {
        win.focus();
    } else {
        alert('Please allow popups for this website');
    }

    ;
}

function initModalSelect2() {
    $select2_status = $("#status").select2({
        minimumResultsForSearch: Infinity,
    });
}


function cancel_confirm(wse_id) {
    $('#wse_id').val(wse_id);
    $('#Modal-cancel').modal('show')
}


function cancel() {
    var wse_id = $('#wse_id').val();
    var inputs = {
        'wse_id': wse_id,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/get_reject_transition_id/",
        contentType: "application/json; charset=utf-8",
        cache: false,
        async: false,
        data: pdata,
        success: function (data) {
            if (data.success) {
                var transition_id = data.transition_id;
                var inputs = {
                    'wse': wse_id,
                    'transition': transition_id,
                    'is_cancel': '1',
                };
                var encoded = $.toJSON(inputs);
                var pdata = encoded;
                console.log(pdata);
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/workflow_approve/",
                    async: true,
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        if (data.success) {
                            var redirect_url = '/myworkflows/apply_history/';
                            window.location.href = redirect_url;
                        } else {
                            alert(data.data);
                            return false;
                        }
                    }
                });
            } else {
                alert(data.msg);
                return false;
            }
        }
    });
}

$(document).ready(function () {

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/myworkflows/data_apply_history/",
            "type": "POST",
        },
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "workflow"},
            {"data": "create_time"},
            {"data": "title"},
            {"data": "current_state"},
            {"data": "state_value"},
            {"data": "send_mail"},
            {
                "data": null,
                "orderable": false,
            },
            {
                "data": "can_cancel",
                "orderable": false,
            }
        ],
        "order": [[2, 'asc']],
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
                'targets': 6,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (data, type, full, meta) {
                    if (data == '审核中') {
                        return '<span class="label label-primary">' + data + '</span>';
                    } else if (data == '完成' | data == '完成-已处理' | data == '完成-查看企业邮件通知' | data == '完成-更新成功') {
                        return '<span class="label label-success">' + data + '</span>';
                    } else if (data == '拒绝') {
                        return '<span class="label label-danger">' + data + '</span>';
                    } else if (data == '完成-未处理' | data == '完成-待更新') {
                        return '<span class="label label-info">' + data + '</span>';
                    } else if (data == '完成-故障中' | data == '完成-更新失败') {
                        return '<span class="label label-danger">' + data + '</span>';
                    } else if (data == '完成-更新中') {
                        return '<span class="label label-default">' + data + '</span>';
                    } else if (data == '取消') {
                        return '<span class="label label-default">' + data + '</span>';
                    } else {
                        return '<p class="text-muted">' + data + '</p>';
                    }
                },
            },
            {
                'targets': 7,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (data, type, full, meta) {
                    if (data == '未发送') {
                        return '<span class="label label-warning">' + data + '</span>';
                    } else if (data == '已发送') {
                        return '<span class="label label-default">' + data + '</span>';
                    } else if (data == '拒绝') {
                        return '<span class="label label-danger">' + data + '</span>';
                    } else {
                        return '<p class="text-muted">' + data + '</p>';
                    }
                },
            },
            {
                targets: 8,
                render: function (a, b, c, d) {
                    if (c.workflow == '后端热更新' | c.workflow == '前端热更新') {
                        var context =
                            {
                                func: [
                                    {"name": "查看", "fn": "view(\'" + c.id + "\')", "type": "info"},
                                    {"name": "邮件通知", "fn": "mail(\'" + c.id + "\')", "type": "success"},
                                    {
                                        "name": "更新详情",
                                        "fn": "myhotupdate(\'" + c.id + "\', \'" + c.workflow + "\')",
                                        "type": "warning"
                                    },
                                    {
                                        "name": "更换审批人",
                                        "fn": "change_approve(\'" + c.id + "\', \'" + c.workflow + "\')",
                                        "type": "primary"
                                    },
                                ]
                            };
                    } else if (c.workflow == '版本更新单申请') {
                        var context =
                            {
                                func: [
                                    {"name": "查看", "fn": "view(\'" + c.id + "\')", "type": "info"},
                                    {"name": "邮件通知", "fn": "mail(\'" + c.id + "\')", "type": "success"},
                                    {
                                        "name": "更换审批人",
                                        "fn": "change_approve(\'" + c.id + "\', \'" + c.workflow + "\')",
                                        "type": "primary"
                                    },
                                ]
                            };
                    }
                    else {
                        var context =
                            {
                                func: [
                                    {"name": "查看", "fn": "view(\'" + c.id + "\')", "type": "info"},
                                    {"name": "邮件通知", "fn": "mail(\'" + c.id + "\')", "type": "success"},
                                ]
                            };
                    }
                    var html = template(context);
                    return html;
                }
            },
            {
                targets: 9,
                render: function (data, b, c, d) {
                    if (data == '1') {
                        var context =
                            {
                                func: [
                                    {"name": "取消", "fn": "cancel_confirm(\'" + c.id + "\')", "type": "danger"},
                                ]
                            };
                    }
                    var html = template(context);
                    return html;
                }
            }
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });

    // initModalSelect2();


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

    // Handle click on table cells
    // $('#mytable tbody').on('click', 'td', function(e){
    //     $(this).parent().find('input[type="checkbox"]').trigger('click');
    // });

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
        //text:"确定删除所选的机房?",
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请选择');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/del_myworkflow_svn/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        } else {
                            alert(data['msg'])
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        }
                        ;
                    }
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    // 添加
    $('#bt-add').click(function () {
        $("#myModalLabel").text("新增机房信息");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#project_name").val('');
        $("#project_name_en").val('');
        $("#status").val('1').trigger('change');
        editFlag = false;
        $("#myModal").modal("show");
    });

    $('#bt-save').click(function () {

        var id = $("#id").val();
        var project_name = $("#project_name").val();
        var project_name_en = $("#project_name_en").val();
        var status = $("#status").select2('data')[0].id;

        var inputIds = {
            "id": id,
            "project_name": project_name,
            "project_name_en": project_name_en,
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
                    table.ajax.reload();
                    $("#myModal").modal("hide");
                } else {
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
            }
        });
    });
});
