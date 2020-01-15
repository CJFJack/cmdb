var workflow;

function initModalSelect2(){
    $select2Applicant = $("#applicant").select2({
        ajax: {
            url: '/assets/list_user/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                    };
            },
            
            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function(item){
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    $select2Applicant.on("select2:select", function (e){
        get_workflow_approve_user(workflow, $("#applicant").val())
    });
}

function get_workflow_state_approve_process(){
    var inputs = {
        'wse': wse,
    }

    var encoded=$.toJSON( inputs );
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

// 获取流程的各个节点的审批人员
function get_workflow_approve_user(workflow, applicant_id){
    if ( applicant_id == '0'){
        console.log('none')
    } else {
        var inputs = {
            'workflow': workflow,
            'applicant_id': applicant_id,
        }

        var encoded=$.toJSON( inputs );
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/myworkflows/get_workflow_approve_user/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                // console.log(data.data, data.current_index);
                if ( data.success ) {
                    $("#approve_user").html(data.data)
                    $("#approve_user").removeClass('alert-danger')
                    $("#approve_user").addClass('alert-success')
                    // $(".ystep1").setStep(data.current_index + 1);
                } else {
                    $("#approve_user").removeClass('alert-success')
                    $("#approve_user").addClass('alert-danger')
                    $("#approve_user").html(data.data)
                }
            },
            error: function() {
                /* Act on the event */
                $("#approve_user").removeClass('alert-success')
                $("#approve_user").addClass('alert-danger')
                $("#approve_user").html('获取审批人失败!')
            },
        });
    }
}

function checkBefore(applicant, title, reason){

    if (applicant == '0'){
        alert('请选择申请人');
        return false;
    }

    if (title == ''){
        alert('请输入标题');
        return false;
    }

    if (reason == ''){
        alert('请输入内容');
        return false;
    }

    return true;

}


$(document).ready(function() {

    workflow = $("#workflow_id").text();
    initModalSelect2();
    get_workflow_approve_user(workflow, $("#applicant").val())

    // 提交
    $("#bt-commit").confirm({
        text:"确定提交到下一步?",
        confirm: function(button){

            var applicant = $("#applicant").select2('data')[0].id;
            var title = $("#title").val();
            var reason = $("#reason").val();

            var result = checkBefore(applicant, title, reason);

            var inputs = {
                'applicant': applicant,
                'title': title,
                'reason': reason,
                'workflow': workflow,
            }

            var encoded=$.toJSON( inputs );
            var pdata = encoded;

            if ( result ){
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/start_workflow/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        if (data.success) {
                            var redirect_url = '/myworkflows/apply_history/';
                            window.location.href = redirect_url;
                        } else {
                            alert(data.data);
                        }
                    }
                });
            }
        },

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

} );
