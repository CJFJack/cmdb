var table;
var str = "确定删除选中的web接口?";
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
            {"data": "workflow"},
            {"data": "state"},
            {"data": "speocified_user"},
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
                alert('请先勾选需要删除的审批人信息');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/delete_specified_user/",
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
        var workflow_id = $('#id_workflow').select2('data')[0].id;
        var state_id = $('#id_state').select2('data')[0].id;
        var specified_user = $('#id_specified_user').val();
        if (!workflow_id) {
            $('#lb-msg').text('请选择流程');
            $('#modal-notify').show();
            return false;
        }
        if (!state_id) {
            $('#lb-msg').text('请选择状态节点');
            $('#modal-notify').show();
            return false;
        }
        if (specified_user == null) {
            $('#lb-msg').text('请选择审批人');
            $('#modal-notify').show();
            return false;
        }
        var inputIds = {
            'workflow_id': workflow_id,
            'state_id': state_id,
            'specified_user': specified_user,
            'EditFlag': EditFlag,
        };
        var urls = '/myworkflows/add_or_edit_specified_user/';
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
    $('#myModalLabel').text('新增流程状态额外审批人');
    initSelect2('id_workflow', '', '');
    initSelect2('id_state', '', '');
    $('#id_workflow').removeAttr('disabled');
    $('#id_state').removeAttr('disabled');
    $("#id_specified_user").val('').trigger('change');
    $("#id_specified_user").html('');
    $('#Modal').modal('show');
}


function initModalSelect2() {
    $select2Workflow = $("#id_workflow").select2({
        ajax: {
            url: '/myworkflows/list_workflow/',
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

    $select2State = $("#id_state").select2({
        ajax: {
            url: '/myworkflows/list_workflow_state/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    workflow_id: $('#id_workflow').select2('data')[0].id,
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
        placeholder: '请选择状态节点',
    });

    $select2SpecifiedUser = $("#id_specified_user").select2({
        ajax: {
            url: '/it_assets/list_all_users/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
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
        placeholder: '请选择审批人',
        multiple: true,
        minimumResultsForSearch: Infinity,
    });
}

function edit_specified_user(state_id) {
    EditFlag = true;
    inputs = {
        'state_id': state_id,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/get_state_specified_user/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data.success) {
                data = data.data;
                initSelect2('id_workflow', data.workflow_id, data.workflow);
                initSelect2('id_state', data.state_id, data.state);
                $('#id_workflow').attr('disabled', 'true');
                $('#id_state').attr('disabled', 'true');
                // 重新填充select2
                $("#id_specified_user").val('').trigger('change');
                $("#id_specified_user").html('');
                var values = new Array();
                data.specified_user.forEach(function (e, i) {
                    $("#id_specified_user").append('<option value="' + e.id + '">' + e.username + '</option>');
                    values.push(e.id);
                });
                $("#id_specified_user").select2('val', values);
                $('#modal-notify').hide();
                $('#Modal').modal('show')
            }
            else {
                alert(data.msg)
            }
        },
    });

}