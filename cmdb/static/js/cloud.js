var table;
var editFlag;
var str = "确定删除选中的云供应商?";
var count = 0;


$(document).ready(function () {

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "ajax": {
            "url": "/assets/cloud/",
            "type": "POST",
        },
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "name"},
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
                targets: 3,
                render: function (a, b, c, d) {
                    return '<a class="btn btn-sm btn-link" href="'+ c.href +'">编辑帐号信息</a>'
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
                    url: "/assets/del_data_cmdb_cloud/",
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
                        ;
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
        $("#cloud_name").val('');
        editFlag = false;
        $("#myModal").modal("show");
    });

    $('#bt-save').click(function () {

        var id = $("#id").val();
        var cloud_name = $('#cloud_name').val();

        if (cloud_name == '') {
            $('#lb-msg').text('请输入云供应商名称!');
            $('#modal-notify').show();
            return false;
        }

        var inputIds = {
            "id": id,
            "name": cloud_name,
            "editFlag": editFlag,
        };

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        var urls = '/assets/add_or_edit_cloud/';

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
