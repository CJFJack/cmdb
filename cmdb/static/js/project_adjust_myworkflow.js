var wse;

var $select2SvnProjects;
var $select2SerperProjects;

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

function initSvnProjects(){
    $select2SvnProjects = $("#svn_projects").select2({
        minimumResultsForSearch: Infinity,
        multiple: true,
        placeholder: '',
    });
}


function initSerperProjects(){
    $select2SerperProjects = $("#serper_projects").select2({
        minimumResultsForSearch: Infinity,
        multiple: true,
        placeholder: '',
    });
}


$(document).ready(function() {

    wse = $("#wse_id").text();

    get_workflow_state_approve_process();

    initSvnProjects();
    initSerperProjects();

    // 提交
    $("#bt-commit").confirm({
        text:"确定重新提交?",
        confirm: function(button){

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
