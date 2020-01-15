var editFlag;
var table;

$(document).ready(function () {

    initModalSelect2();

    //获取流程审批链
    var workflow_id = $('#workflow_id').val();
    $.ajax({
        type: "POST",
        url: "/myworkflows/workflow_node_config/" + workflow_id + "/",
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            $(".ystep1").loadStep({
                size: "large",
                color: "green",
                steps: data.step,
            });
            $(".ystep1").setStep(data.max_index);
        }
    });

    //新增流程状态modal
    $("#bt-add-state").click(function () {
        $('#modal-add-state').hide();
        $('#myModalLabel-State').text('新增流程状态');
        initModalSelect2();
        initSelect2('state_name', '', '');
        var editFlag = false;
        $('#Modal-State').modal('show');
    });

    //保存新增流程状态信息
    $('#add_state').click(function () {
        var state_name = $('#state_name').select2('data')[0].id;
        let input = {
            'state_name': state_name,
            'workflow_id': workflow_id,
            'editFlag': editFlag,
        };

        let encoded = $.toJSON(input);
        let pdata = encoded;

        let url = '/myworkflows/add_workflow_state/';
        $.ajax({
            type: "POST",
            url: url,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.success) {
                    window.location.reload();
                }
                else {
                    $('#lb-msg-edit-state').text(data.msg);
                    $('#modal-edit-state').css('display', 'block');
                    $('#Modal-State').modal('hide')
                }
            },
            error: function (data) {
                alert('内部错误')
            }
        });
    });

    //使表格中，流程状态顺序列可编辑
    $('#bt-edit-state').click(function () {
        $('.state_order').removeAttr('readonly');
        $('.state_order').removeAttr('style');
    });

    //保存流程状态顺序
    $('#bt-save-state').click(function () {
        $('.state_order').attr('readonly', 'readonly');
        $('.state_order').attr('style', 'background-color:transparent;border:0;');
        let edit_state_data = getTableContent();
        let input = {
            'edit_state_data': edit_state_data,
            'workflow_id': workflow_id,
        };
        let encoded = $.toJSON(input);
        let pdata = encoded;
        let url = '/myworkflows/edit_workflow_state/';
        $.ajax({
            type: "POST",
            url: url,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            beforeSend: function () {
                jQuery('#loading').showLoading();
            },
            success: function (data) {
                if (data.success) {
                    window.location.reload();
                }
                else {
                    jQuery('#loading').hideLoading();
                    window.location.reload();
                    alert(data.msg);
                }
            },
            error: function (data) {
                jQuery('#loading').hideLoading();
                alert('内部错误')
            }
        });
    })

});


function initModalSelect2() {

    $select2StateByWorkflow = $('.select_state').select2({
        ajax: {
            url: '/myworkflows/list_state_by_workflow/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    workflow_id: $('#workflow_id').val(),
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
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: "请选择流程状态"
    });

    $select2AllState = $('#state_name').select2({
        ajax: {
            url: '/myworkflows/list_all_state/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
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
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: "请选择状态名称"
    });

}


function getTableContent() {
    var mytable = document.getElementById('mytable');
    var data = [];
    for (var i = 1, rows = mytable.rows.length; i < rows; i++) {
        for (var j = 0, cells = 2; j < cells; j++) {
            if (!data[i]) {
                data[i] = new Array();
            }
            if (j === 0) {
                data[i][j] = mytable.rows[i].cells[j].childNodes.item(1).value;
            }
            else {
                data[i][j] = mytable.rows[i].cells[j].innerHTML;
            }
        }
    }
    return data;
}

