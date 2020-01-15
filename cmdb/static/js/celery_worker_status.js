var table;
var str = "确定取消监控选中的worker?";
var count = 0;

function initModalSelect2() {

    $select2ReceiveUser = $("#receive_user").select2({
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
        placeholder: '接收告警人',
        multiple: true,
        minimumResultsForSearch: Infinity,
    });

}

$(document).ready(function () {

    var rows_selected = [];
    table = $('#mytable').DataTable({
        columns: [
            {},
            {"data": "id"},
            {"data": "name"},
            {"data": "total"},
            {"data": "status"},
        ],
        responsive: true,
        language: {
            "url": "/static/js/i18n/Chinese.json"
        },
        ordering: false
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
        //text:"确定删除所选的cdn接口?",
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请先勾选需要取消监控的worker');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/delete_worker_monitor/",
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


    // 编辑接收告警信息的人员
    $('#bt-receive-user').click(function () {
        initModalSelect2();
        $.ajax({
            type: "get",
            url: "/myworkflows/get_celery_notice_receive_user/",
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                if (data.success) {
                    // 重新填充select2
                    $("#receive_user").val('').trigger('change');
                    $("#receive_user").html('');
                    var values = new Array();
                    data.receive_user.forEach(function (e, i) {
                        $("#receive_user").append('<option value="' + e.id + '">' + e.username + '</option>');
                        values.push(e.id);
                    });
                    $("#receive_user").select2('val', values);
                    $('#myModalReceiveNotice').modal('show');
                }
                else {
                    alert(data.msg)
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


    // 保存接收告警信息人员名单
    $('#bt-save').click(function () {
        var receive_user = $('#receive_user').val();
        var inputIds = {
            'receive_user': receive_user
        };
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: '/myworkflows/save_celery_notice_receive_user/',
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                $('#myModalReceiveNotice').modal('hide');
                if (data.success) {
                    alert('保存成功')
                }
                else {
                    alert(data.msg)
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
    })


});


// 同步运行中的worker到数据库
function sync_running_worker() {
    $('#loading').showLoading();
    $.ajax({
        type: "POST",
        url: "/myworkflows/sync_running_worker/",
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            $('#loading').hideLoading();
            if (data['success']) {
                location.reload();
            }
            else {
                alert(data['msg'])
            }
        },
        error: function (xhr, status, error) {
            $('#loading').hideLoading();
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
}

