var table;
var str = "确定删除选中的web接口?";
var count = 0;
var EditFlag;

$(document).ready(function () {

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        columns: [
            {},
            {"data": "id"},
            {"data": "param"},
            {"data": "user"},
            {"data": "remark"},
            {},
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
                alert('请先勾选需要删除的配置信息');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/delete_workflow_special_user/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['success']) {
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

    // 初始化select2下拉框
    initModalSelect2();

    // 保存审批人配置信息
    $('#bt-save').click(function () {
        var config_id = $('#id_config').val();
        var param = $('#id_param').val();
        var remark = $('#id_remark').val();
        var special_user = $('#id_special_user').val();
        if (!param) {
            $('#lb-msg').text('请填写参数名称');
            $('#modal-notify').show();
            return false;
        }
        if (!remark) {
            $('#lb-msg').text('请填写参数备注');
            $('#modal-notify').show();
            return false;
        }
        if (special_user == null) {
            $('#lb-msg').text('请选择特殊人员');
            $('#modal-notify').show();
            return false;
        }
        var inputIds = {
            'config_id': config_id,
            'param': param,
            'remark': remark,
            'special_user': special_user,
            'EditFlag': EditFlag,
        };
        var urls = '/myworkflows/add_or_edit_special_user/';
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.success) {
                    location.reload();
                    $("#Modal").modal("hide");
                } else {
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
            }
        });
    })

});


//新增审批人信息
function bt_add() {
    EditFlag = false;
    $('#modal-notify').hide();
    $('#myModalLabel').text('新增特殊人员配置信息');
    $('#id_param').val('');
    $('#id_remark').val('');
    $("#id_special_user").val('').trigger('change');
    $("#id_special_user").html('');
    $('#Modal').modal('show');
}


function initModalSelect2() {
    $select2SpecialUser = $("#id_special_user").select2({
        ajax: {
            url: '/it_assets/list_all_users/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
        placeholder: '选择关联人员',
        multiple: true,
        minimumResultsForSearch: Infinity,
    });
}

function edit(config_id) {
    EditFlag = true;
    inputs = {
        'config_id': config_id,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/get_workflow_special_user/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data.success) {
                data = data.data;
                $('#id_config').val(data.id);
                $('#id_param').val(data.param);
                $('#id_remark').val(data.remark);
                // 重新填充select2
                $("#id_special_user").val('').trigger('change');
                $("#id_special_user").html('');
                var values = new Array();
                data.special_user.forEach(function (e, i) {
                    $("#id_special_user").append('<option value="' + e.id + '">' + e.username + '</option>');
                    values.push(e.id);
                });
                $("#id_special_user").select2('val', values);
                $('#modal-notify').hide();
                $('#Modal').modal('show')
            }
            else {
                alert(data.msg)
            }
        },
    });

}