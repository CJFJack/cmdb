var table;
var editFlag;
var str = "确定删除选中的云供应商?";
var count = 0;


function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_cmdb_tecent_cloud_account/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data;
            $("#myModalLabel").text("修改");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide();
            //console.log(roomid);
            $("#cloud_name").val('腾讯云');
            $("#secret_id").val(data.secret_id);
            $("#secret_key").val(data.secret_key);
            $("#remark").val(data.remark);
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


$(document).ready(function () {

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "ajax": {
            "url": "/assets/tecent_cloud_account/",
            "type": "POST",
        },
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "cloud"},
            {"data": "remark"},
            {"data": "secret_id"},
            {"data": "secret_key"},
            {
                "data": null,
                "orderable": false,
            }
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
                'targets': [1, 2],
                'visible': false,
                'searchable': false
            },
            {
                targets: 6,
                render: function (a, b, c, d) {
                    return '<button class="btn btn-sm btn-primary" onclick="edit(' + c.id + ')">修改</button>'
                }
            }
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },

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
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请选择');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_cmdb_tecent_cloud_account/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            table.ajax.reload(null, false);
                            makeTitle(str, 0);
                            count = 0;
                        } else {
                            alert(data['msg'])
                            table.ajax.reload(null, false);
                            makeTitle(str, 0);
                            count = 0;
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

    // 添加
    $('#bt-add').click(function () {
        $("#myModalLabel").text("新增云供应商");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#id").val('');
        $("#cloud_name").val('腾讯云');
        $("#remark").val('');
        $("#secret_id").val('');
        $("#secret_key").val('');
        editFlag = false;
        $("#myModal").modal("show");
    });

    $('#bt-save').click(function () {
        var id = $("#id").val();
        var secret_id = $('#secret_id').val();
        var secret_key = $('#secret_key').val();
        var remark = $('#remark').val();

        if (remark == '') {
            $('#lb-msg').text('请输入备注！');
            $('#modal-notify').show();
            return false;
        }
        if (secret_id == '') {
            $('#lb-msg').text('请输入secret_id!');
            $('#modal-notify').show();
            return false;
        }
        if (secret_key == '') {
            $('#lb-msg').text('请输入secret_key!');
            $('#modal-notify').show();
            return false;
        }

        var inputIds = {
            "id": id,
            'secret_id': secret_id,
            'secret_key': secret_key,
            'remark': remark,
            "editFlag": editFlag,
        };

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        var urls = '/assets/add_or_edit_tecent_cloud_account/';

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
});
