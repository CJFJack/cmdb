var workflow;
var $select2Project;
var $selectGame2Project;
var $select2Repo;
var $select2Permission;
var $select2Applicant;
var $select2SVNScheme;


function initRepo() {
    $('.repo').select2({
        ajax: {
            url: '/myworkflows/list_svn_repo/',
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
                    results: $.map(data, function (item) {
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
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}


function initGameProject() {
    $selectGame2Project = $('#project').select2({
        ajax: {
            url: '/assets/list_game_project/',
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
                    results: $.map(data, function (item) {
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
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $selectGame2Project;
    $selectGame2Project.on("select2:select", function (e) {
        change_custom_game_project_name("select2:select", e);
    });
}

function change_custom_game_project_name(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        var project_name = $("#project").select2('data')[0].text;
        $(".svn_project_name").each(function (i, e) {
            $(e).val(project_name);
        });

        var applicant_id = $("#applicant").val()
        var project_id = $("#project").val()
        get_workflow_approve_user(workflow, applicant_id, project_id)
    }
}

// 获取流程的各个节点的审批人员
function get_workflow_approve_user(workflow, applicant_id, project_id) {
    if (applicant_id == '0' | project_id == '0') {
        console.log('none')
    } else {
        var inputs = {
            'workflow': workflow,
            'applicant_id': applicant_id,
            'project_id': project_id,
        }

        var encoded = $.toJSON(inputs);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/myworkflows/get_workflow_approve_user/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                // console.log(data.data, data.current_index);
                if (data.success) {
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
            error: function () {
                /* Act on the event */
                $("#approve_user").removeClass('alert-success')
                $("#approve_user").addClass('alert-danger')
                $("#approve_user").html('获取审批人失败!')
            },
        });
    }
}

function initProject() {

    $select2SVNScheme = $('#svn_scheme').select2({
        ajax: {
            url: '/myworkflows/list_svn_scheme/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: $("#project").select2('data')[0].id,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
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
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2SVNScheme;
    $select2SVNScheme.on("select2:select", function (e) {
        show_svn_scheme("select2:select", e);
    });
}

function show_svn_scheme(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        var svn_scheme_id = $("#svn_scheme").select2('data')[0].id;
        var data = {
            'svn_scheme_id': svn_scheme_id,
        };

        var encoded = $.toJSON(data);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/myworkflows/get_svn_scheme_data/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                // console.log(data);
                $(".cancel").remove();
                data.forEach(function (el) {
                    var add_str = '<div class="form-group cancel">' +
                        '<div class="col-sm-2">' +
                        '<input type="text" class="form-control" style="width: 100%" readonly value=' + el.project + '>' +
                        '</div>' +
                        '<div class="col-sm-2">' +
                        '<input type="text" class="form-control" style="width: 100%" readonly value=' + el.svn_repo + '>' +
                        '</div>' +
                        '<div class="col-sm-4">' +
                        '<input type="text" class="form-control" style="width: 100%" readonly value=' + el.svn_path + '>' +
                        '</div>' +
                        '<div class="col-sm-1">' +
                        '<input type="text" class="form-control" style="width: 100%" readonly value=' + el.svn_perm + '>' +
                        '</div>'
                    $("#insert_svn_scheme").after(add_str);
                    // var newItem = $("#insert_svn_scheme").next()

                    // $(".add_svn_scheme").select2();

                });
            },
        });
    }
}


function initModalSelect2() {
    // 初始化select2


    initGameProject();

    initProject();

    initRepo();

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
                    results: $.map(data, function (item) {
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
    $select2Applicant.on("select2:select", function (e) {
        get_workflow_approve_user(workflow, $("#applicant").val(), $("#project").val())
    });

    $(".permission").select2({
        minimumResultsForSearch: Infinity,
    });

    $.fn.modal.Constructor.prototype.enforceFocus = function () {
    };

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
        alert('请选择申请人!');
        return false;
    }

    return true;

}

function get_path_permission() {
    // 获取path和对应的权限
    // 以json的格式存储
    /* [
            {'project_id': id, 'project': project, 'repo_id': repo, 'repo': repo, 'path': path, 'perm': perm},
            {'project_id': id, 'project': project, 'repo_id': repo, 'repo': repo, 'path': path, 'perm': perm},
        ]
    */

    var content = new Array();

    $(".path").each(function (i, e) {

        var path_to_project_id = $("#project").select2('data')[0].id;
        if (path_to_project_id == '0') {
            alert('请选择项目!');
            content = false;
            return content;
        }

        var path_to_project = $("#project").select2('data')[0].text;


        var path_to_repo_id = $($(e).parent().prev().children().get(0)).select2('data')[0].id;
        if (path_to_repo_id == '0') {
            alert('请选择SVN仓库!');
            content = false;
            return content;
        }

        var path_to_repo = $($(e).parent().prev().children().get(0)).select2('data')[0].text;


        var path_permission = $($(e).parent().next().children().get(0));
        var mpath = $(e).val();
        var mpath = $.trim(mpath);

        if (!/^\//.test(mpath)) {
            alert('仓库内子路径要以/开头');
            content = false;
            return content;
        }

        var perm = path_permission.select2('data')[0].id;

        var item = {};
        item['project_id'] = path_to_project_id;
        item['project'] = path_to_project;
        item['repo_id'] = path_to_repo_id;
        item['repo'] = path_to_repo;
        item['path'] = mpath;
        item['perm'] = perm;

        content.push(item);

    });

    // console.log(content);
    // return false;

    return content;
};


$(document).ready(function () {

    workflow = $("#workflow_id").text();

    initModalSelect2();

    $("#show_scheme").hide();

    // 提交
    $("#bt-commit").confirm({
        text: "确定提交到下一步?",
        confirm: function (button) {

            var project = $("#project").select2('data')[0].id;
            var applicant = $("#applicant").select2('data')[0].id;
            var title = $("#title").val();
            var reason = $("#reason").val();
            var svn_scheme = $("#svn_scheme").select2('data')[0].id;

            var result = checkBefore(title, reason, applicant);

            var content = get_path_permission();

            if (svn_scheme == '0') {
                // 如果没有选择套餐
                if (typeof(content) == 'boolean') {
                    if (!content) {
                        alert('你没有选择任何的svn');
                        return false;
                    }
                } else {
                    if (content.length == 0) {
                        alert('你没有选择任何的svn');
                        return false;
                    }
                }
            } else {
                // 如果选择了svn套餐，但是自定义的有错
                // 如果没有选择套餐
                if (typeof(content) == 'boolean') {
                    if (!content) {
                        // 没有按照格式
                        return false;
                    }
                }
            }

            var inputs = {
                'project': project,
                'applicant': applicant,
                'title': title,
                'content': content,
                'reason': reason,
                'svn_scheme': svn_scheme,
                'workflow': workflow,
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
                        } else {
                            alert(data.data);
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

    $("#bt-test").click(function () {
        get_path_permission();
    });

    $("#cancle-btn").click(function () {
        $(".cancel").remove();
        $("#svn_scheme").val('0').trigger('change');
    });

    $("#myAdd").click(function () {
        var project_id = $("#project").select2('data')[0].id;
        var project_name = $("#project").select2('data')[0].text;
        if (project_id == '0') {
            alert('请先选择项目!');
            return false;
        } else {
            var add_str = '<div class="form-group">' +
                '<div class="col-sm-2">' +
                '<input type="text" class="form-control svn_project_name" style="width: 100%" readonly="readonly" value=' + project_name + '>' +
                '</div>' +
                '<div class="col-sm-2">' +
                '<select style="width: 100%" class="repo">' +
                '<option value="0" selected="selected">选择仓库</option>' +
                '</select>' +
                '</div>' +
                '<div class="col-sm-4">' +
                '<input type="text" class="form-control path" style="width: 100%" placeholder="整个仓库为/,子路径以/开头">' +
                '</div>' +
                '<div class="col-sm-1">' +
                '<select class="permission" style="width: 90%">' +
                '<option value="读" selected="selected">读</option>' +
                '<option value="读写">读写</option>' +
                '</select>' +
                '</div>' +
                '<button class="btn btn-danger btn-sm myRemove" type="button">x</button>';
            // $(this).parent().after(add_str);
            $("#show_scheme").show();
            $("#append_before").before(add_str);

            // initProject();
            initRepo();

            // 初始化权限
            $(".permission").select2({
                minimumResultsForSearch: Infinity,
            });

            // 添加删除按钮的监听事件
            $(".myRemove").click(function () {
                $(this).parent().remove();

                if ($.trim($('.myRemove').html()) == '') {
                    $("#show_scheme").hide();
                }
            });
        }


    });

    // test loading
    $("#bt-load").click(function () {
        $.ajax({
            type: "GET",
            url: "/myworkflows/test_load/",
            contentType: "application/json; charset=utf-8",
            async: true,
            beforeSend: function () {
                $("#load").show();
            },
            success: function (data) {
                $("#load").hide();
                alert('执行成功');
            },
            error: function () {
                $("#load").hide();
            }
        });
    });


    $("#project").change(function(){
        $(".cancel").remove();
    })

});
