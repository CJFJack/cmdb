var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

// 修改之前的数据
var origin_data;

var str = "确定删除选中的分组?";
var count = 0;

var $select2Leader;
var $select2_status;


function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/users/get_role_group_data/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data;
            $("#myModalLabel").text("修改人员分组");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide();

            // 重新填充select2
            $("#relate_user").val('').trigger('change');
            $("#relate_user").html('');
            var values = new Array();
            data.relate_user.forEach(function (e, i) {
                $("#relate_user").append('<option value="' + e.id + '">' + e.username + '</option>');
                values.push(e.id);
            });
            $("#relate_user").select2('val', values);
            $('#name').val(data.name);

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
};


function initModalSelect2() {

    $select2RelatedUsers = $("#relate_user").select2({
        ajax: {
            url: '/assets/list_ops_user/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
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
            cache: true,
        },
        placeholder: '对接运维',
        multiple: true,
        minimumResultsForSearch: Infinity,
    });
};


$(document).ready(function () {

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "serverSide": true,
        "ordering": false,
        "ajax": {
            "url": "/users/data_role_group/",
            "type": "POST",
        },
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "name"},
            {"data": "relate_user"},
            {
                "data": null,
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
                targets: 4,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                //{"name": "项目分组", "fn": "project_group(\'" + c.id + "\')", "type": "info"},
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


    initModalSelect2()

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
                    url: "/users/del_role_group/",
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
        $("#myModalLabel").text("新增人员分组");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $('#name').val('');
        $("#relate_user").val('').trigger('change');
        editFlag = false;
        $("#myModal").modal("show");
    });


    $('#bt-save').click(function () {

        var id = $("#id").val();
        var relate_user = $("#relate_user").val() == null ? new Array() : $("#relate_user").val();
        var name = $('#name').val();

        if (!name) {
            $('#lb-msg').text('请选择分组名字');
            $('#modal-notify').show();
            return false
        }

        var inputIds = {
            "id": id,
            "name": name,
            "relate_user": relate_user,
            "editFlag": editFlag,
        };

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        urls = '/users/add_or_edit_role_group/';

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
            }
        });
    });


    $('#bt-back').click(function () {
        window.location.href = document.referrer
    })

});
