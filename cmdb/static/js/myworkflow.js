var wse;
var $selectGame2Project;


function myshow_svn_scheme(){
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
        success: function(data){
            // console.log(data);
            $(".cancel").remove();
            data.forEach(function(el){
                var add_str = '<div class="form-group row">' +
                                '<div class="col-sm-4">' +
                                    '<input type="text" class="form-control" readonly value='+ el.svn_repo + '>' +
                                '</div>' +
                                '<div class="col-sm-6">' +
                                    '<input type="text" class="form-control" readonly value='+ el.svn_path + '>' +
                                '</div>' +
                                '<div class="col-sm-2">' +
                                    '<input type="text" class="form-control" readonly value='+ el.svn_perm +'>' +
                                '</div>'+
                              '</div>'
                $("#insert_svn_scheme").after(add_str);

            });
        },
    });
}

function checkBefore(title, content){
    if (title == ''){
        alert('请输入标题');
        return false
    }

    if (content == ''){
        alert('请输入内容');
        return false
    }

    return true

}

function initRepo(){
    $('.repo').select2( {
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
}


function initGameProject(){
    $selectGame2Project = $('#project').select2( {
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

    $selectGame2Project;
    $selectGame2Project.on("select2:select", function (e){ change_custom_game_project_name("select2:select", e); });
}

function change_custom_game_project_name(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        var project_name = $("#project").select2('data')[0].text;
        $(".svn_project_name").each(function(i, e){
            $(e).val(project_name);
        });
    }
}

function initProject(){

    $select2SVNScheme = $('#svn_scheme').select2( {
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

    $select2SVNScheme;
    $select2SVNScheme.on("select2:select", function (e){ show_svn_scheme("select2:select", e); });
}

function show_svn_scheme(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
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
            success: function(data){
                // console.log(data);
                $(".cancel").remove();
                data.forEach(function(el){
                    var add_str = '<div class="form-group cancel">' +
                                    '<div class="col-sm-2">' +
                                        '<select style="width: 70%" class="add_svn_scheme" disabled>' +
                                            '<option value="0" selected="selected">'+ el.project +'</option>' +
                                        '</select>' +
                                    '</div>' +
                                    '<div class="col-sm-2">' +
                                        '<select style="width: 70%" class="add_svn_scheme" disabled>' +
                                            '<option value="0" selected="selected">'+ el.svn_repo +'</option>' +
                                        '</select>' +
                                    '</div>' +
                                    '<div class="col-sm-4">' +
                                        '<input type="text" class="form-control" style="width: 100%" disabled value='+ el.svn_path +'>' +
                                    '</div>' +
                                    '<div class="col-sm-1">' +
                                        '<select style="width: 90%" class="add_svn_scheme" disabled>' +
                                            '<option value="0" selected="selected">'+ el.svn_perm +'</option>' +
                                        '</select>' +
                                    '</div>'
                    $("#insert_svn_scheme").after(add_str);
                    $(".add_svn_scheme").select2();

                });
            },
        });
    }
}

function get_path_permission(){
    // 获取path和对应的权限
    // 以json的格式存储
    /* [
            {'project_id': id, 'project': project, 'repo_id': repo, 'repo': repo, 'path': path, 'perm': perm},
            {'project_id': id, 'project': project, 'repo_id': repo, 'repo': repo, 'path': path, 'perm': perm},
        ]
    */

    var content = new Array();

    $(".path").each(function(i, e){
        var path_permission = $($(e).parent().next().children().get(0));
        var mpath = $(e).val();
        var mpath = $.trim(mpath);

        if ( !/^\//.test(mpath) ){
            alert('仓库内子路径要以/开头');
            content = false;
            return content;
        }

        var path_to_repo_id = $($(e).parent().prev().children().get(0)).select2('data')[0].id;
        if (path_to_repo_id == '0'){
            alert('请选择SVN项目!');
            content = false;
            return content;
        }

        var path_to_repo = $($(e).parent().prev().children().get(0)).select2('data')[0].text;

        var path_to_project_id = $("#project").select2('data')[0].id;
        if (path_to_project_id == '0'){
            alert('请选择SVN仓库!');
            content = false;
            return content;
        }

        var path_to_project = $("#project").select2('data')[0].text;

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



function initModalSelect2(){
    // 初始化select2

    initGameProject();

    initProject();
    initRepo();

    myshow_svn_scheme();

    $("#applicant").select2();

    $(".permission").select2({
        /*data: [
            {'id': '读', 'text': '读'},
            {'id': '写', 'text': '写'},
            {'id': '读写', 'text': '读写'},
        ],*/
        minimumResultsForSearch: Infinity,
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

    // 提交
    $("#bt-commit").confirm({
        text:"确定重新提交?",
        confirm: function(button){

            var project = $("#project").select2('data')[0].id;
            var applicant = $("#applicant").select2('data')[0].id;
            var title = $("#title").val();
            var reason = $("#reason").val();
            var svn_scheme = $("#svn_scheme").select2('data')[0].id;
            
            var result = checkBefore(title, reason, applicant);

            var content = get_path_permission();

            if (svn_scheme == '0'){
                // 如果没有选择套餐
                if (typeof(content) == 'boolean'){
                    if (! content){
                        alert('你没有选择任何的svn');
                        return false;
                    }
                } else {
                    if (content.length == 0){
                        alert('你没有选择任何的svn');
                        return false;
                    }
                }
            } else {
                // 如果选择了svn套餐，但是自定义的有错
                // 如果没有选择套餐
                if (typeof(content) == 'boolean'){
                    if (! content){
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


    $(".myRemove").click( function(){
        $(this).parent().remove();
    } );

    $("#cancle-btn").click( function(){
        $(".cancel").remove();
        initSelect2("svn_scheme", '0', '选择方案');
    } );

    $("#myAdd").click( function() {
        var project_id = $("#project").select2('data')[0].id;
        var project_name = $("#project").select2('data')[0].text;
        if (project_id == '0'){
            alert('请先选择项目!');
            return false;
        } else {
            var add_str = '<div class="form-group">' +
                        '<div class="col-sm-2">' +
                            '<input type="text" class="form-control svn_project_name" style="width: 100%" readonly="readonly" value=' + project_name + '>' +
                        '</div>' +
                        '<div class="col-sm-2">' +
                            '<select style="width: 70%" class="repo">' +
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
            $("#append_before").before(add_str);

            // initProject();
            initRepo();

            // 初始化权限
            $(".permission").select2({
                data: [
                    {'id': '读', 'text': '读'},
                    {'id': '写', 'text': '写'},
                    {'id': '读写', 'text': '读写'},
                ],
                minimumResultsForSearch: Infinity,
            });

            // 添加删除按钮的监听事件
            $(".myRemove").click( function(){
                $(this).parent().remove();

                if ($.trim($('.myRemove').html()) == ''){
                    $("#show_scheme").hide();
                }
            } );
        }
       


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
    } )
    
} );
