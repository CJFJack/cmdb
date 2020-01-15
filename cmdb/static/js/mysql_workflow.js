var workflow;
var $select2Project;
var $selectGame2Project;
var $select2Repo;
var $select2Permission;
var $select2Applicant;
var $select2SVNScheme;


function initMysqlInstance(selector){
    selector.select2( {
        ajax: {
            url: '/mysql/list_mysql_instance/',
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
                            value: item.value,
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

function initMysqlDB(selector){
    selector.select2( {
        ajax: {
            url: '/mysql/list_mysql_instance_db/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    instance: $(selector).parent().parent().find('.instance').select2('data')[0]['value'],
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
            cache: true,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        multiple: true,
        placeholder: '选择一个或者多个DB',
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}


// 获取流程的各个节点的审批人员
function get_workflow_approve_user(workflow, applicant){
    var inputs = {
        'workflow': workflow,
        'username': applicant,
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

function checkBefore(title, content){
    if (title == ''){
        alert('请输入标题');
        return false;
    }

    if (content == ''){
        alert('请输入内容');
        return false;
    }

    return true;
}

function get_instance_permission(){
    // 获取instance和对应的权限
    // 以json的格式存储
    /* [
            {'instance': 'host:port', 'dbs': ["old_cmdb", "cy_devops"], 'permission': 'p1,p2'},
            {'instance': 'host1:port2', 'dbs': ["old_cmdb2", "cy_devops1"], 'permission': 'p1,p2'},
        ]
    */

    var content = new Array();

    $(".mysql_content").each(function(i, e){
        var item = {};

        var instance_id = $($(e).children().find('.instance')).val()
        var instance = $($(e).children().find('.instance')).select2('data')[0].value;
        if ( instance_id == '0' ){
            alert('请选择mysql实例!');
            content = false;
            return content;
        }
        var dbs = $(e).children().find('.db').val();
        if ( dbs == null ) {
            alert('请选择一个DB!');
            content = false;
            return content;
        }

        var permission = $(e).children().find('.permission').val()

        item['instance'] = instance
        item['dbs'] = dbs
        item['permission'] = permission

        content.push(item);

    });

    // console.log(content);
    // return false;

    return content;
};


$(document).ready(function() {

    workflow = $("#workflow_id").text();

    get_workflow_approve_user(workflow, $("#applicant").val());

    // 提交
    $("#bt-commit").confirm({
        text:"确定提交到下一步?",
        confirm: function(button){

            var title = $("#title").val();
            var reason = $("#reason").val();
            
            var result = checkBefore(title, reason);

            var content = get_instance_permission();

            var inputs = {
                'title': title,
                'content': content,
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

    $("#myAdd").click( function() {
        var add_str = '<div class="form-group mysql_content">' +
                    '<div class="col-sm-4">' +
                        '<select style="width: 100%" class="instance">' +
                            '<option value="0" selected="selected">选择mysql实例</option>' +
                        '</select>' +
                    '</div>' +
                    '<div class="col-sm-3">' +
                        '<select style="width: 100%" class="db">' +
                        '</select>' +
                    '</div>' +
                    '<div class="col-sm-4">' +
                        '<select class="permission" style="width: 100%">' +
                            '<option value="select" selected="selected">select</option>' +
                            '<option value="select,insert,update">select,insert,update</option>' +
                            '<option value="select,insert,update,delete">select,insert,update,delete</option>' +
                            '<option value="select,insert,update,delete,drop,create,alter">select,insert,update,delete,drop,create,alter</option>' +
                            // '<option value="ALL PRIVILEGES">ALL PRIVILEGES</option>' +
                        '</select>' +
                    '</div>' +
                    '<button class="btn btn-danger btn-sm myRemove" type="button">x</button>';

        $("#append_before").before(add_str);
        var mysql_instance = $("#append_before").prev().find('.instance')
        var mysql_db = $("#append_before").prev().find('.db')

        initMysqlInstance($(mysql_instance))
        initMysqlDB(mysql_db)

        // 初始化权限
        $(".permission").select2({
            minimumResultsForSearch: Infinity,
        });

        // 添加删除按钮的监听事件
        $(".myRemove").click( function(){
            $(this).parent().remove();

            if ($.trim($('.myRemove').html()) == ''){
                $("#show_scheme").hide();
            }
        } );
    });

    
} );
