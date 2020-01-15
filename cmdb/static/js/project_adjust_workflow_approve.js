var wse;

var $select2SvnProjects;
var $select2SerperProjects;

var $select2ToAnotherAdmin;
$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURIComponent(results[1]) || 0;
    }
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

    // get_workflow_state();

    // 提交
    $("#bt-commit").confirm({
        text:"确定提交?",
        confirm: function(button){

            var transition = $('input[name=transitions]:checked').attr('id');
            var opinion = $("#opinion").val();
            
            if ( !transition ){
                alert('请选择审批意见!');
                return false;
            }

            var inputs = {
                'wse': wse,
                'transition': transition,
                'opinion': opinion,
            }

            var encoded=$.toJSON( inputs );
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

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    $("#bt-load").click( function(){
        var inputs = {
            'wse': wse,
        }

        var encoded=$.toJSON( inputs );
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/myworkflows/test_load/",
            contentType: "application/json; charset=utf-8",
            async: true,
            data: pdata,
            beforeSend: function(){
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
            error: function(){
                $("#load").hide();
                $("#modal-footer").show();
                $("#load-msg").text(data.data);
                $("#show-msg").show();
            }
        });
    } );

    $("#bt-transfer").confirm({
        text:"确定转交另外的人员处理?",
        confirm: function(button){

            var to_anthoer_admin = $("#to_anthoer_admin").select2('data')[0].id;

            if ( to_anthoer_admin == '0' ){
                alert('请选择转交网管人员!');
                return false;
            }

            var inputs = {
                'wse': wse,
                'to_anthoer_admin': to_anthoer_admin,
            }

            var encoded=$.toJSON( inputs );
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

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });
    
} );
