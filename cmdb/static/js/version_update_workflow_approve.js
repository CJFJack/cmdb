var wse;

$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    }
    else {
        return decodeURIComponent(results[1]) || 0;
    }
}


function get_workflow_state_approve_process() {
    var inputs = {
        'wse': wse,
    }

    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/workflow_state_approve_process/",
        async: true,
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            // console.log(data.data, data.current_index);
            $(".ystep1").loadStep({
                size: "large",
                color: "green",
                steps: data.data,
            });

            $(".ystep1").setStep(data.current_index + 1);
        }
    });
}

$(document).ready(function () {

    wse = $("#wse_id").text();

    get_workflow_state_approve_process();

    // get_workflow_state();

    // 提交
    $("#bt-commit").confirm({
        text: "确定提交?",
        confirm: function (button) {

            var transition = $('input[name=transitions]:checked').attr('id');
            var opinion = $("#opinion").val();

            if (!transition) {
                alert('请选择审批意见!');
                return false;
            }

            if (typeof($("#server_version").attr('readonly')) == 'undefined') {
                // 如果没有readonly，说明需要填写版本号
                if ($("#server_version").val() == '') {
                    alert('请填写版本号!');
                    return false;
                }

                if ($("#server_attention").val() == '') {
                    alert('请填写后端注意事项!');
                    return false;
                }

            }

            if (typeof($("#client_version").attr('readonly')) == 'undefined') {
                // 如果没有readonly，说明需要填写版本号
                if ($("#client_version").val() == '') {
                    alert('请填写版本号!');
                    return false;
                }

                if ($("#client_attention").val() == '') {
                    alert('请填写前端注意事项!');
                    return false;
                }

            }

            var inputs = {
                'wse': wse,
                'transition': transition,
                'opinion': opinion,
                'server_version': $("#server_version").val(),
                'server_attention': $("#server_attention").val(),
                'client_version': $("#client_version").val(),
                'client_attention': $("#client_attention").val(),
            }

            var encoded = $.toJSON(inputs);
            var pdata = encoded;
            $.ajax({
                type: "POST",
                url: "/myworkflows/workflow_approve/",
                async: true,
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    if (data.success) {
                        var redirect_url = '/myworkflows/approve_list/';
                        window.location.href = redirect_url;
                    } else {
                        alert(data.data);
                        return false;
                    }
                }
            });
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    $("#bt-load").click(function () {
        var inputs = {
            'wse': wse,
        }

        var encoded = $.toJSON(inputs);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/myworkflows/test_load/",
            contentType: "application/json; charset=utf-8",
            async: true,
            data: pdata,
            beforeSend: function () {
                $("#myModal").modal("show");
                $("#modal-footer").hide();
                $("#show-msg").hide();
                $("#load").show();
            },
            success: function (data) {
                $("#load").hide();
                $("#modal-footer").show();
                $("#load-msg").text(data.data);
                $("#show-msg").show();

            },
            error: function () {
                $("#load").hide();
                $("#modal-footer").show();
                $("#load-msg").text(data.data);
                $("#show-msg").show();
            }
        });
    });

    $("#bt-transfer").confirm({
        text: "确定转交另外的人员处理?",
        confirm: function (button) {

            var to_anthoer_admin = $("#to_anthoer_admin").select2('data')[0].id;

            if (to_anthoer_admin == '0') {
                alert('请选择转交网管人员!');
                return false;
            }

            var inputs = {
                'wse': wse,
                'to_anthoer_admin': to_anthoer_admin,
            }

            var encoded = $.toJSON(inputs);
            var pdata = encoded;
            $.ajax({
                type: "POST",
                url: "/myworkflows/transfer_to_other_admin/",
                async: true,
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    if (data.success) {
                        var redirect_url = '/myworkflows/approve_list/';
                        window.location.href = redirect_url;
                    } else {
                        alert(data.data);
                        return false;
                    }
                }
            });
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });


    // 初始化区服列表
    $("#server_list_v2").treeMultiselect(
        {
            searchable: true, searchParams: ['section', 'text'],
            freeze: false, hideSidePanel: true, startCollapsed: true
        }
    );

});
