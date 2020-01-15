var wse;
var $selectGame2Project;


function checkBefore(title, content, applicant) {
    if (title == '') {
        alert('请输入标题');
        return false;
    }

    if (content == '') {
        alert('请输入内容');
        return false;
    }

    if (applicant == '0') {
        alert('请选择申请人');
        return false;
    }

    return true;

}


function initModalSelect2() {
    // 初始化select2

};


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

function show_div_server_content() {
    let server_range = $('#server_range').select2('data')[0].id;
    if (server_range === 'all') {
        $('#div_server_content').addClass('hidden');
    }
    else {
        $('#div_server_content').removeClass('hidden');
    }
    if (server_range === 'include') {
        $('#div_on_new_server').addClass('hidden');
    }
    else {
        $('#div_on_new_server').removeClass('hidden');
    }
}


function initSelect2Range() {
    var $select2Range = $('#server_range').select2();
    // 初始化区服范围的值
    show_div_server_content();
    // 监听区服范围下拉框变化
    $select2Range.on("select2:select", function (e) {
        show_div_server_content();
    });
}


function update_version_task(version_update_type) {
    var inputs = {
        'wse': wse,
        'version_update_type': version_update_type,
    };

    var encoded = $.toJSON(inputs);
    var pdata = encoded;

    $.ajax({
        type: "POST",
        url: "/myworkflows/do_version_update/",
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
            $("#load-msg").text(data.msg);
            $("#show-msg").show();

        },
        error: function (data) {
            $("#load").hide();
            $("#modal-footer").show();
            $("#load-msg").text(data.msg);
            $("#show-msg").show();
        }
    });
}


function change_version_update_status() {
    var inputs = {
        'wse': wse,
    };

    var encoded = $.toJSON(inputs);
    var pdata = encoded;

    $.ajax({
        type: "POST",
        url: "/myworkflows/failure_declare_finish/",
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
}


// 监听是否执行跨服重排
function check_is_ask_reset() {
    if ($('#ask_reset').prop('checked')) {
        $('#div_server_erlang').removeClass('hidden')
    }
    else {
        $('#div_server_erlang').addClass('hidden')
    }
    $("#ask_reset").change(function () {
        // console.log($('#ask_reset').prop('checked'))
        if ($('#ask_reset').prop('checked')) {
            $('#div_server_erlang').removeClass('hidden')
        }
        else {
            $('#div_server_erlang').addClass('hidden')
        }
    });
}


$(document).ready(function () {

    wse = $("#wse_id").text();

    initModalSelect2();
    initSelect2Range();

    get_workflow_state_approve_process();

    // 提交
    $("#bt-commit").confirm({
        text: "确定重新提交?",
        confirm: function (button) {

            var applicant = $("#applicant").select2('data')[0].id;
            var title = $("#title").val();
            var content = $("#content").val();
            var result = checkBefore(title, content, applicant);
            var inputs = {
                'applicant': applicant,
                'title': title,
                'content': content,
                'wse': wse,
            };

            var encoded = $.toJSON(inputs);
            var pdata = encoded;

            if (result) {
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/start_workflow/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        if (data.success) {
                            var redirect_url = '/myworkflows/apply_history/';
                            window.location.href = redirect_url;
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


    // 选择版本更新方式并执行
    $('#bt-load').confirm({
        columnClass: 'col-md-7 col-md-offset-3',
        icon: 'fa fa-warning',
        title: false,
        content: '确定要执行版本更新吗？',
        backgroundDismiss: true,
        buttons: {
            client: {
                text: '前端版本更新',
                btnClass: 'btn-success',
                action: function () {
                    let version_update_type = 'client';
                    update_version_task(version_update_type);
                }
            },
            server: {
                text: '后端版本更新',
                btnClass: 'btn-primary',
                action: function () {
                    let version_update_type = 'server';
                    update_version_task(version_update_type);
                }
            },
            all: {
                text: '前、后端版本更新',
                btnClass: 'btn-danger',
                action: function () {
                    let version_update_type = 'all';
                    update_version_task(version_update_type);
                }
            },
            handle: {
                text: '只修改处理状态',
                btnClass: 'btn-warning',
                action: function () {
                    change_version_update_status();
                }
            },
            cancel: {
                text: '取消',
            },
        }
    });


    // // 初始化区服列表
    // $("#server_list_v2").treeMultiselect(
    //     {
    //         searchable: true, searchParams: ['section', 'text'],
    //         freeze: false, hideSidePanel: true, startCollapsed: true
    //     }
    // );


    //监听是否执行跨服重排
    check_is_ask_reset();


    // 修改工单状态为已处理
    $('#bt-handle').confirm({
        columnClass: 'col-md-6 col-md-offset-3',
        icon: 'fa fa-warning',
        title: false,
        content: '确定将工单状态修改为已处理吗？',
        backgroundDismiss: true,
        buttons: {
            confirm: {
                text: '确定',
                btnClass: 'btn-success',
                action: function () {
                    change_version_update_status();
                }
            },
            cancel: {
                text: '取消',
            },
        }
    });


});
