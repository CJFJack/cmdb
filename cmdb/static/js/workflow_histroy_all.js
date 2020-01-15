var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的申请?";
var count = 0;

var $select2Workflow;
var $select2WorkflowStatus;
var $select2Admin;

var myObj;


function view(id) {
    var redirect_url = '/myworkflows/myworkflow_history?id=' + id;
    // window.location.href = redirect_url;
    var win = window.open(redirect_url, '_blank');
    if (win) {
        win.focus();
    } else {
        alert('Please allow popups for this website');
    }
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

function initModalSelect2() {

    $select2Workflow = $("#filter_workflow").select2({});
    $select2Workflow.on("change", function (e) {
        log("select2:select", e);
    });

    $select2Admin = $("#filter_admin").select2({});

    $select2Admin.on("select2:select", function (e) {
        log2("select2:select", e);
    });

    $select2WorkflowStatus = $("#filter_status").select2({});
    $select2WorkflowStatus.on("select2:select", function (e) {
        log2("select2:select", e);
    });

    $select2State_value = $("#filter_state_value").select2({});
    $select2State_value.on("change", function (e) {
        log2("select2:select", e);
    });

};


function reset_status(workflow_id) {
    var status_dict = {};
    if (workflow_id == null) {
        status_dict = {'100': '全部'}
    } else {
        for (var w of workflow_id) {
            for (var i in myObj[w]) {
                status_dict[myObj[w][i]] = myObj[w][i];
            }
        }
    }

    $("#filter_status").html('');

    Object.keys(status_dict).sort(function (a, b) {
        return a - b
    }).reverse().forEach(function (key) {
        // ordered[parseInt(key)] = status_dict[key]

        if (key == '100') {
            $("#filter_status").append('<option value=' + key + ' selected="selected">' + status_dict[key] + '</option>');
        } else {
            $("#filter_status").append('<option value=' + key + '>' + status_dict[key] + '</option>');
        }
    })

    $("#filter_status").val(100).trigger('change');
}

function log(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        // var workflow_id = $("#filter_workflow").val();
        // reset_status(workflow_id);
        table.ajax.reload();

    }
}

function log2(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        table.ajax.reload();

    }
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

function filter_workflow() {
    var workflow = $.urlParam('workflow');
    if (workflow !== null) {
        $('#filter_workflow').val(workflow);
    }
}


$(document).ready(function () {

    initModalSelect2();
    filter_workflow();

    myObj = $("#test").data('my-object');
    // console.log(myObj);

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "searching": false,
        "ajax": {
            "url": "/myworkflows/data_apply_history_all/",
            "type": "POST",
            "data": function (d) {
                d.workflow = $("#filter_workflow").val();
                d.filter_state_value = $("#filter_state_value").val();
                d.workflow_status = $("#filter_status").val();
                d.admin = $("#filter_admin").select2('data')[0].id;
                d.time = $("#filter_time").val();
                d.creator = $("#filter_creator").val();
                d.applicant = $("#filter_applicant").val();
                d.title = $("#filter_title").val();
                d.state = $("#filter_state").val();
                d.svn_processed = $("#svn_processed").is(':checked');
                d.serper_processed = $("#serper_processed").is(':checked');
            },
        },
        "columns": [
            {"data": "id"},
            {"data": "workflow"},
            {"data": "create_time"},
            {"data": "creator"},
            {"data": "applicant"},
            {"data": "title"},
            {"data": "current_state"},
            {"data": "state_value"},
            {"data": "status"},
            {"data": "is_valid"},
            {
                "data": null,
                "orderable": false,
            }
        ],
        "order": [[2, 'asc']],
        columnDefs: [
            {
                'targets': 0,
                'visible': false,
                'searchable': false
            },
            {
                'targets': 7,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (data, type, full, meta) {
                    if (data == '审核中') {
                        return '<span class="label label-primary">' + data + '</span>';
                    } else if (data == '完成') {
                        return '<span class="label label-success">' + data + '</span>';
                    } else if (data == '拒绝') {
                        return '<span class="label label-danger">' + data + '</span>';
                    } else if (data == '取消') {
                        return '<span class="label label-default">' + data + '</span>';
                    } else {
                        return '<p class="text-muted">' + data + '</p>';
                    }
                },
            },
            {
                'targets': 8,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (data, type, full, meta) {
                    if (data == '更新成功' | data == '已处理' | data == '查看企业邮件通知') {
                        return '<span class="label label-success">' + data + '</span>';
                    } else if (data == '未处理') {
                        return '<span class="label label-primary">' + data + '</span>';
                    } else if (data == '待更新') {
                        return '<span class="label label-info">' + data + '</span>';
                    } else if (data == '故障中' | data == '更新失败') {
                        return '<span class="label label-danger">' + data + '</span>';
                    } else {
                        return '<p class="text-muted">' + data + '</p>';
                    }
                },
            },
            {
                'targets': 9,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (data, type, full, meta) {
                    if (data == '有效') {
                        return '<span class="label label-success">' + data + '</span>';
                    } else if (data == '无效') {
                        return '<span class="label label-danger">' + data + '</span>';
                    } else {
                        return '<p class="text-muted">' + data + '</p>';
                    }
                },
            },
            {
                targets: 10,
                render: function (a, b, c, d) {
                    let is_superuser = $('#is_superuser').val();
                    if (is_superuser) {
                        if (c.is_valid == '有效') {
                            var context =
                                {
                                    func: [
                                        {"name": "查看", "fn": "view(\'" + c.id + "\')", "type": "info"},
                                        {"name": "设置无效", "fn": "invalid(\'" + c.id + "\')", "type": "warning"},
                                    ]
                                };
                            var html = template(context);
                        }
                        else {
                            var context =
                                {
                                    func: [
                                        {"name": "查看", "fn": "view(\'" + c.id + "\')", "type": "info"},
                                        {"name": "设置有效", "fn": "valid(\'" + c.id + "\')", "type": "success"},
                                    ]
                                };
                            var html = template(context);
                        }
                    }
                    else {
                        var context =
                            {
                                func: [
                                    {"name": "查看", "fn": "view(\'" + c.id + "\')", "type": "info"},
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
                ;
            }
        });
    });

    $("#svn_processed").click(function () {
        table.ajax.reload();
    });

    $("#serper_processed").click(function () {
        table.ajax.reload();
    });

    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $('input.column_filter').on('keyup click || change', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    });

    $("#bt-reset").click(function () {
        $("#filter_workflow").val('0').trigger('change');
        $("#filter_admin").val('0').trigger('change');
        $("#filter_time").val('');
        $("#filter_creator").val('');
        $("#filter_applicant").val('');
        $("#filter_title").val('');
        $("#filter_state").val('');
        $("#svn_processed").attr('checked', false);
        $("#serper_processed").attr('checked', false);

        $("#filter_status").html('');
        $("#filter_status").append('<option value="100" selected="selected">全部</option>');
        $("#filter_status").val('100').trigger('change');
        $("#filter_state_value").val('全部').trigger('change');
        table.ajax.reload();
    });

    $(".flatpickr").flatpickr({
        locale: "zh",
        enableTime: false,
        // time_24hr: true,
    });

});

// 设置工单有效状态为无效
function invalid(id) {
    let r = confirm("确定要设置为无效吗?");
    if (r == true) {
        let inputIds = {
            "id": id,
            "is_valid": 0,
        };
        let encoded = $.toJSON(inputIds);
        let pdata = encoded;
        let urls = '/myworkflows/change_workflow_apply_valid_status/';

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.data) {
                    table.ajax.reload();
                } else {
                    alert(data.msg)
                }
            }
        });
    }
}

// 设置工单有效状态为有效
function valid(id) {
    let r = confirm("确定要设置为有效吗?");
    if (r == true) {
        let inputIds = {
            "id": id,
            "is_valid": 1,
        };
        let encoded = $.toJSON(inputIds);
        let pdata = encoded;
        let urls = '/myworkflows/change_workflow_apply_valid_status/';

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.data) {
                    table.ajax.reload();
                } else {
                    alert(data.msg)
                }
            }
        });
    }
}
