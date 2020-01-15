var wse;
var $select2ChangeApprove;


function initModalSelect2(){
    // 初始化select2
    var current_state_name = $("#current_state_name").text();
    var project_id = $("#project_id").text();
    var _url = '/myworkflows/list_project_group_user/';

    if ( current_state_name == '后端负责人') {
        var project_group = '服务端技术组';
    } else if ( current_state_name == '前端负责人' ) {
        var project_group = '客户端技术组';
    } else if ( current_state_name == '策划负责人' ) {
        var project_group = '策划组';
    } else if ( current_state_name == '测试负责人' ) {
        var project_group = '测试组';
    } else if ( current_state_name == '运维负责人' ) {
        var project_group = '业务运维组';
    }

    $select2server_charge = $("#change_approve").select2({
        ajax: {
            url: _url,
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: project_id,
                    project_group: project_group,
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
};


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


$(document).ready(function() {

    wse = $("#wse_id").text();

    initModalSelect2();

    get_workflow_state_approve_process();

    $("#bt-commit").confirm({
        text:"确定更换审批人?",
        confirm: function(button){
            var inputs = {
                'wse': wse,
                'change_approve': $("#change_approve").val(),
            }

            var encoded=$.toJSON( inputs );
            var pdata = encoded;

            result = true;

            if ( result ){
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/change_approve/",
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
