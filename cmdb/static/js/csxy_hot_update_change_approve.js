var wse;
var $select2ChangeApprove;


function initModalSelect2(){
    // 初始化select2
    var current_state_name = $("#current_state_name").text();
    var project_id = $("#project_id").text();
    var workflow_name = $("#workflow_name").text();

    if ( workflow_name == '前端热更新' ) {
        project_group = '前端组'
    } else if ( workflow_name == '后端热更新' ) {
        project_group = '后端组'
    } else {
        project_group = '未知的组'
    }

    if ( current_state_name == '项目组长') {
        $select2server_charge = $("#change_approve").select2({
            ajax: {
                url: '/assets/list_backup_dev/',
                dataType: 'json',
                type: 'POST',
                delay: 250,
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
        });
    } else if ( current_state_name == '测试' ) {
        $select2server_charge = $("#change_approve").select2({
            ajax: {
                url: '/assets/list_test_user/',
                dataType: 'json',
                type: 'POST',
                delay: 250,
                data: function (params) {
                    return {
                        q: params.term, // search term
                        page: params.page,
                        name: '心源-测试中心',
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
        });
    } else if ( current_state_name == '运营' ) {
        $select2server_charge = $("#change_approve").select2({
            ajax: {
                url: '/assets/list_operation_user/',
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
        });
    } else if ( current_state_name == '运维' ) {
        $select2server_charge = $("#change_approve").select2({
            ajax: {
                url: '/assets/list_operation_user/',
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
        });
    }

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

            if ( $("#change_approve").val() == '0' ) {
                alert('请选择更改的审批人')
                return false;
            }

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
