var workflow;
var $select2Applicant;

var $select2ProjectGroup;
var $select2SvnProjects;
var $select2SerperProjects;

function initProjectGroup(){
}


function initModalSelect2(){
    // 初始化select2

    $select2Applicant = $("#applicant").select2({
        ajax: {
            url: '/assets/list_user/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    user_project_group: 1,
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
                            user_project_group: item.user_project_group,
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

    $select2ProjectGroup = $('#new_group_section').select2( {
        ajax: {
            url: '/users/list_group_section_all/',
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
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2ProjectGroup = $('#new_department_group').select2( {
        ajax: {
            url: '/users/list_department_group_all/',
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
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2Applicant;
    $select2Applicant.on("select2:select", function (e){ show_current_project_group("select2:select", e); });


    $.fn.modal.Constructor.prototype.enforceFocus = function() {};
};

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

// 初始化提示
function initToolTip(){
    var title = '1 人员项目调整，比如同事K从A调去项目B，同事K可能有多个项目的SVN和服务器权限，CMDB会将同事K的SVN和服务器权限关联的项目列出来<br />' + 
                '2 如果勾选了删除svn或者服务器权限，需要选择清除哪些项目对应的SVN和服务器权限，如果没有勾选，则会保留之前项目的SVN和服务器权限。'
    $("[data-toggle='tooltip']").attr('title', title)
    $("[data-toggle='tooltip']").tooltip({html: true});
}


function show_current_project_group(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){

        var user = $("#applicant").val()

        var data = {
            'user': user
        }

        var encoded = $.toJSON(data);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/users/user_svn_serper_projects/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function(data){
                if ( data.success ) {
                    // 填充服务器项目
                    $('#serper_projects').val(null).trigger('change');
                    $('#serper_projects').html('');
                    var serper_projects = data.serper_projects;
                    serper_projects.forEach(function(e, i) {
                        var newOption = new Option(e.text, e.id, true, true);
                        $('#serper_projects').append(newOption).trigger('change');
                    } );

                    // 填充svn项目
                    $('#svn_projects').val(null).trigger('change');
                    $('#svn_projects').html('');
                    var svn_projects = data.svn_projects;
                    svn_projects.forEach(function(e, i) {
                        var newOption = new Option(e.text, e.id, true, true);
                        $('#svn_projects').append(newOption).trigger('change');
                    } );
                } else {
                    alert('获取用户的项目数据失败! 请联系运维部')
                }
            },
            error: function(e) {
                /* Act on the event */
                alert('获取用户的项目数据失败! 请联系运维部')
            },
        });

        get_workflow_approve_user(workflow, $("#applicant").val())
    }
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

function checkBefore(applicant, title, new_department_group){
    if (title == ''){
        alert('请输入标题');
        return false;
    }

    if (applicant == '0'){
        alert('请选择申请人!');
        return false;
    }

    if (new_department_group == '0'){
        alert('请选择新的项目分组!');
        return false;
    }

    return true;

}


$(document).ready(function() {

    workflow = $("#workflow_id").text();

    initModalSelect2();
    initToolTip();

    initSvnProjects();
    initSerperProjects();

    // 提交
    $("#bt-commit").confirm({
        text:"确定提交到下一步?",
        confirm: function(button){
            var applicant = $("#applicant").select2('data')[0].id;
            var title = $("#title").val();

            var delete_svn = $("#delete_svn").prop('checked');
            var delete_serper = $("#delete_serper").prop('checked');

            var svn_projects = $("#svn_projects").val();
            var serper_projects = $("#serper_projects").val();

            var new_department_group = $("#new_department_group").val();
            
            var result = checkBefore(applicant, title, new_department_group);

            var inputs = {
                'applicant': applicant,
                'title': title,
                'delete_svn': delete_svn,
                'svn_projects': svn_projects,
                'delete_serper': delete_serper,
                'serper_projects': serper_projects,
                'new_department_group': new_department_group,
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

    $("#delete_svn").click(function(event) {
        /* Act on the event */
        if ( $("#delete_svn").prop('checked') ) {
            var delete_svn_warning = '<div id="delete_svn_warning" class="alert alert-danger">' +
                                        '被调整人员的<strong>已选择的项目上的SVN权限</strong>将被清除!' +
                                    '</div>'
            $("#append_warning").append(delete_svn_warning);
            $("#svn_projects").attr({disabled: false,});
        } else {
            $("#delete_svn_warning").remove();
            $("#svn_projects").attr({disabled: true,});
        }
    });

    $("#delete_serper").click(function(event) {
        /* Act on the event */
        if ( $("#delete_serper").prop('checked') ) {
            var delete_serper_warning = '<div id="delete_serper_warning" class="alert alert-danger">' +
                                        '被调整人员的<strong>已选择的项目上的服务器权限</strong>将被清除!' +
                                    '</div>'
            $("#append_warning").append(delete_serper_warning);
            $("#serper_projects").attr({disabled: false,});
        } else {
            $("#delete_serper_warning").remove();
            $("#serper_projects").attr({disabled: true,});
        }
    });
    
} );
