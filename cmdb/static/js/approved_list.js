var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);


function view(id) {
    var redirect_url = '/myworkflows/workflow_approve?id=' + id;
    window.location.href = redirect_url;
};


function initModalSelect2() {
    $select2_status = $("#status").select2({
        minimumResultsForSearch: Infinity,
    });
};

$(document).ready(function () {

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/myworkflows/data_approved_list/",
            "type": "POST",
        },
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "workflow"},
            {"data": "create_time"},
            {"data": "creator"},
            {"data": "title"},
            {"data": "approve_time"},
            {"data": "state_value"},
            {"data": "current_state"},
            {
                "data": null,
                "orderable": false,
            }
        ],
        "order": [[2, "desc"]],
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
                targets: 2,
                render: function (data) {
                    if (data == 'wifi申请') {
                        return 'wifi申请和网络问题申报';
                    }
                    else {
                        return data;
                    }
                }
            },
            {
                'targets': 7,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (data, type, full, meta) {
                    if (data == '待审批') {
                        return '<span class="label label-primary">' + data + '</span>';
                    } else if (data == '同意') {
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
                'targets': 1,
                'visible': false,
                'searchable': false
            },
            {
                targets: 9,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "查看", "fn": "view(\'" + c.id + "\')", "type": "info"},
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
                    url: "/assets/del_data_cmdb_game_project_list/",
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
});
