var table;
var str = "确定删除选中的数据?";
var count = 0;
var EditFlag;

$(document).ready(function () {
    $.fn.select2.defaults.set( "theme", "bootstrap" );

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        columns: [
            {},
            {"data": "id"},
            {"data": "cmdb_account"},
            {"data": "wechat_account"},
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
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请先勾选需要删除数据');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/delete_wechat_account_transfer/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['success']) {
                            window.location.reload();
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
        var cmdb_account = $('#id_cmdb_account').select2('data')[0].id;
        var wechat_account = $('#id_wechat_account').val();
        if (!cmdb_account) {
            $('#lb-msg').text('请选择cmdb用户');
            $('#modal-notify').show();
            return false;
        }
        if (wechat_account == null) {
            $('#lb-msg').text('请填写企业微信帐号');
            $('#modal-notify').show();
            return false;
        }
        var inputIds = {
            'cmdb_account': cmdb_account,
            'wechat_account': wechat_account,
            'EditFlag': EditFlag,
        };
        var urls = '/myworkflows/add_or_edit_wechat_account_transer/';
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.success) {
                    window.location.reload();
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
    $('#myModalLabel').text('新增');
    $('#id_wechat_account').val('');
    $("#id_cmdb_account").val('').trigger('change');
    $('#Modal').modal('show');
}


function initModalSelect2() {
    $select2CMDBAccount = $("#id_cmdb_account").select2({
        ajax: {
            url: '/it_assets/list_all_users/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },

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
            cache: false,
        },
        placeholder: '请选择流程',
    });

}

function edit(id) {
    EditFlag = true;
    inputs = {
        'id': id,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/get_wechat_account_transfer/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data.success) {
                data = data.data;
                $('#id_wechat_account').val(data.wechat_account);
                initSelect2('id_cmdb_account', data.cmdb_account_id, data.cmdb_account);
                $('#modal-notify').hide();
                $('#Modal').modal('show')
            }
            else {
                alert(data.msg)
            }
        },
    });

}