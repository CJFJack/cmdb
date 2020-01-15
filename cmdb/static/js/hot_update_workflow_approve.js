var workflow;
var wse
var $select2Project;
var $select2UpdateType;
var $select2UpdateVersion;
var $select2ChooseServer;

var $select2TestHead;
var $select2OperationHead;

var hot_update_file_list_html = `
    <div class="form-group update_backend">
      <label class="col-sm-12" for="TextArea">热更文件列表</label>
      <div class="col-sm-6">
          <textarea class="form-control" id="file_list" rows="5"></textarea>
      </div>
    </div>
    <div class="form-group erlang_cmd">
      <label class="col-sm-12" for="TextArea">erlang命令</label>
      <div class="col-sm-6">
          <textarea class="form-control" id="erlang_cmd" rows="5"></textarea>
      </div>
    </div>
`


function initDateTime(){
    var dt = new Date();
    var current_month = dt.getMonth() + 1
    var from = dt.getFullYear() + '-' + current_month + '-' + dt.getDate();
    var next_month = dt.getMonth() + 2
    var to = dt.getFullYear() + '-' + next_month + '-' + dt.getDate();
    $(".flatpickr").flatpickr({
        enableTime: true,
        time_24hr: true,
        locale: "zh",
        /*disable: [
            function(date) {
                var dt = new Date();
                return (date < new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()));
            }
        ],*/
        enable: [
            {
                from: from,
                to: to,
            },
        ],
    });

    $("#update_time").val( $("#update_time").attr("data-time") );
}

/*function reset_ips(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        $("#ips").val(null).trigger('change');
    }
};*/

function initChooseServer(){
    $("#choose_server").select2({
        minimumResultsForSearch: Infinity,
    });
    $select2ChooseServer.on("select2:select", function (e) { clean_choose_server("select2:select", e, "update_type"); });
}



function initModalSelect2(){
    $select2Project = $('#project').select2( {
        ajax: {
            url: '/myworkflows/list_game_project/',
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
        // minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2Project.on("select2:select", function (e) { rest_update_version("select2:select", e, "project"); });

    // 初始化测试负责人，只能是测试部门的人
    $select2TestHead = $("#test_head").select2({
        ajax: {
            url: '/assets/list_test_user/',
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

    // 初始化测试负责人，只能是测试部门的人
    $select2OperationHead = $("#operation_head").select2({
        ajax: {
            url: '/assets/list_operation_user/',
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

    // 更新类型，前端or后端
    $select2UpdateType = $("#update_type").select2({
        minimumResultsForSearch: Infinity,
    });
    $select2UpdateType.on("select2:select", function (e) { rest_update_version("select2:select", e, "update_type"); });

    // 更新版本
    $select2UpdateVersion = $('#update_version').select2( {
        ajax: {
            url: '/myworkflows/list_game_version/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            cache: true,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project_id: $("#project").select2('data')[0].id,
                    update_type: $("#update_type").select2('data')[0].text,
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

    // 选服方式
    $select2ChooseServer = $("#choose_server").select2({
        minimumResultsForSearch: Infinity,
    }).on("select2:select", function (e) { $(".clean_choose_server").remove(); });
    
}

function rest_update_version(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        // 重置更新版本号
        $("#update_version").val('0').trigger('change');

        // 清除之前的选服的数据
        $(".clean_choose_server").remove();

        // 如果是更新类型的改变，需要加入是否热更文件列表和erlang命令
        if ( className == "update_type" ){
            if ( $("#update_type").select2('data')[0].text == '后端' ) {
                $("#update_backend_before").before(hot_update_file_list_html);
                $("#choose_server").html('');
                $("#choose_server").append('<option value="0" selected="selected">选服方式</option>');
                $("#choose_server").append('<option value="1">版本号</option>');
                $("#choose_server").append('<option value="2">区服列表</option>');
                initChooseServer();
            } else {
                $(".update_backend").remove();
                $("#choose_server").html('');
                $("#choose_server").append('<option value="0" selected="selected">选服方式</option>');
                $("#choose_server").append('<option value="1">前端CDN</option>');
                $("#choose_server").append('<option value="2">版本号</option>');
                initChooseServer();
            }
        }
    }
}


// 初始化cdn url的下拉
function initCDNUrl(selector){
    selector.select2( {
        ajax: {
            url: '/myworkflows/list_cdnurl/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project_id: $("#project").select2('data')[0].id,
                    update_type: $("#update_type").select2('data')[0].text,
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
                            version: item.version,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        // minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    } ).on("select2:select", function (e) { console.log( $( selector ).parent().parent().find('.cdn_url_version').val( $( selector ).select2('data')[0].version )); });
}

// 清除选区服的方式
function clean_choose_server(){
    var update_type = $("#update_type").select2('data')[0].text;
    var choose_server = $("#choose_server").select2('data')[0].text;
}

// 添加选服的方式
function add_server(){
    var update_type = $("#update_type").select2('data')[0].text;
    var choose_server = $("#choose_server").select2('data')[0].text;

    if ( update_type == '前端' ) {
        if ( choose_server == '前端CDN' ) {
            var add_str = `
                <div class="form-group clean_choose_server">
                    <div class="col-sm-4">
                        <select style="width: 100%" class="cdn_url">
                            <option value="0" selected="selected">选择cdn地址</option>
                        </select>
                    </div>
                    <div class="col-sm-4">
                        <input type="text" class="form-control cdn_url_version" style="width: 100%" readonly>
                    </div>
                    <button class="btn btn-danger btn-sm myRemove" type="button">x</button>
                </div>
                
            `

            $("#choose_server_before").before(add_str);

            // 找到刚刚添加的add_str
            var add_str_html = $(".clean_choose_server").last();
            var add_cdn_url = add_str_html.find('.cdn_url');
            initCDNUrl(add_cdn_url);
            $(".myRemove").click( function() {
                $( this ).parent().remove();
            } );
        } else if ( choose_server == '版本号' ) {

            if ( ! $(".clean_choose_server").length ){
                var update_version_id = $("#update_version").select2('data')[0].id;
                var project_id = $("#project").select2('data')[0].id;

                if ( update_version_id != '0' && project_id != '0' ) {
                    var update_version = $("#update_version").select2('data')[0].text;
                    var update_type = $("#update_type").select2('data')[0].text;
                    var inputs = {
                        'project_id': project_id,
                        'update_version': update_version,
                        'update_type': update_type,
                    }

                    var encoded=$.toJSON( inputs );
                    var pdata = encoded;

                    $.ajax({
                        type: "POST",
                        url: "/myworkflows/get_server_tree/",
                        contentType: "application/json; charset=utf-8",
                        data: pdata,
                        success: function (data) {
                            var server_list = `
                                    <div class="form-group clean_choose_server">
                                      <label class="col-sm-12">区服列表</label>
                                      <div class="col-sm-6">
                                        <select id="server_list" multiple="multiple">
                                        </select>
                                      </div>
                                    </div>
                                `
                            $("#choose_server_before").before(server_list);
                            data.forEach( function(e, i){
                                var option = "<option" + " " +
                                                "vlaue=" + e.srv_name + " " +
                                                "data-section=" + e.pf_name + " " +
                                                "data-platform=" + e.pf_name + " " +
                                                "data-srv=" + e.srv_id + " " +
                                                "data-server=" + e.server_id + " " +
                                                "data-host=" + e.host_id + " " +
                                                "data-ip=" + e.ip + " " +
                                                "data-pf=" + e.platform_id + " " +
                                                ">" + e.srv_name +
                                             "</option>"
                                $("#server_list").append(option);
                            } );

                            // 初始化区服列表
                            $("#server_list").treeMultiselect(
                                {
                                    searchable: true, searchParams: ['section', 'text'],
                                    freeze: false, hideSidePanel: true, startCollapsed: true
                                }
                            );
                        }
                    });
                }
            }

            

        }
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

function checkBefore(title, reason, project, test_head){

    if (applicant == '0'){
        alert('请选择申请人');
        return false;
    }

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


// 获取选择的区服列表
function get_server_list(){
    // 返回 json list的格式
    var data = new Array();
    $($('.option:checkbox:checked')).each( function(i, e){
        var server_info = {}
        var parent_element = $(e).parent()
        server_info.platform_id = parent_element.attr('data-pf');
        server_info.pf_name = parent_element.attr('data-platform');
        server_info.srv_id = parent_element.attr('data-srv');
        server_info.server_id = parent_element.attr('data-server');
        server_info.srv_name = parent_element.attr('data-value');
        server_info.host_id = parent_element.attr('data-host');
        server_info.ip = parent_element.attr('data-ip');
        data.push(server_info);
    } );

    return data;
}

$(document).ready(function() {

    // workflow = $("#workflow_id").text();
    // initModalSelect2();

    wse = $("#wse_id").text();

    initDateTime();

    $("#server_list").treeMultiselect(
        {
            searchable: true, searchParams: ['section', 'text'],
            freeze: true, hideSidePanel: true, startCollapsed: true
        }
    );

    get_workflow_state_approve_process();


    // 提交
   // 提交
    $("#bt-commit").confirm({
        text:"确定提交?",
        confirm: function(button){

            var transition = $('input[name=transitions]:checked').attr('id');

            if ( !transition ){
                alert('请选择审批意见!');
                return false;
            }

            var inputs = {
                'wse': wse,
                'transition': transition,
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

    $("#add_server").click( function(){
        add_server();
    } );

    $("#reset_server").click( function() {
        $(".clean_choose_server").remove()
    } );

} );
