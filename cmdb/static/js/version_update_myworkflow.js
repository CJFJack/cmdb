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


$(document).ready(function () {

    wse = $("#wse_id").text();

    initModalSelect2();

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
            }

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

    $("#bt-load").click(function () {
        var inputs = {
            'wse': wse,
        }

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
    });


    // 初始化区服列表
    $("#server_list_v2").treeMultiselect(
        {
            searchable: true, searchParams: ['section', 'text'],
            freeze: false, hideSidePanel: true, startCollapsed: true
        }
    );

});
