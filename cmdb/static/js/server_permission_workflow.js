var workflow;
var $select2Project;
var $select2Room;
var $select2IPs;
var $select2Group;

function initModalSelect2(){
    // 初始化select2

    $select2Project = $('#project').select2( {
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

    $select2Room = $("#room").select2( {
        ajax: {
            url: '/assets/list_room/',
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

    $select2Group = $("#group").select2();

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};
};


/*function reset_ips(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        $("#ips").val(null).trigger('change');
    }
};*/


function initGameServerIP(selector){
    selector.select2({
        ajax: {
            url: '/assets/list_ip_room_game_server/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page || 1,
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
                    results: data.results,
                    pagination: {
                        more: (params.page * 10) < data.count_filtered
                    }
                };
            },
            cache: true,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function initIpRoom(selector){
    selector.select2({
        ajax: {
            url: '/assets/list_ip_room/',
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
            cache: true,                                                                                                                                                
        },                                                                                                                                                              
        //minimumResultsForSearch: Infinity,                                                                                                                            
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work                                                                            
        // minimumInputLength: 1,                                                                                                                                       
        // templateResult: formatRepo, // omitted for brevity, see the source of this page                                                                              
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page                                                                  
    });                                                                                                                                                                 
}                                          

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

function checkBefore(project, title, key, reason){

    if (project == '0'){
        alert('请选择项目');
        return false;
    }

    if (title == ''){
        alert('请输入标题');
        return false;
    }

    if (reason == ''){
        alert('请输入原因');
        return false;
    }

    if (key == ''){
        alert('请输入你的key');
        return false;
    } else {
        if (key.split(/\s+/, 3)[2] != $("#first_name").text()){
            console.log(key);
            console.log(key.split(/\s+/, 3));
            console.log(key.split(/\s+/, 3)[2]);
            alert('key的格式不对，需要以申请人的拼音名称结尾');
            return false;
        }
    }

    return true;
}


function get_ip_room(){
    // 获取单个ip-机房
    var ips = new Array();
    $(".ip_room").each(function(i, e){
        var id = $(e).select2('data')[0].id;
        var ip = $(e).select2('data')[0].text;
        if (id == '0'){
            ips = false
            return ips;
        } else{
            var info = {};
            info['id'] = id;
            info['ip'] = ip;
            ips.push(info);
        }

    });

    return ips;
}

// 获取流程的各个节点的审批人员
function get_workflow_approve_user(workflow){
    var inputs = {
        'workflow': workflow,
        'username': $("#applicant").val(),
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


$(document).ready(function() {

    workflow = $("#workflow_id").text();

    initModalSelect2();

    initDateTime();
    get_workflow_approve_user(workflow)

    // 提交
    $("#bt-commit").confirm({
        text:"确定提交到下一步?",
        confirm: function(button){

            var project = $("#project").select2('data')[0].id;
            var title = $("#title").val();
            var reason = $("#reason").val();
            var key = $("#key").val();
            var is_root = $.parseJSON($('input[name=keyType]:checked').val());
            var room = $("#room").select2('data')[0].id;

            var ips = get_ip_room();

            var group = $("#group").select2('data')[0].id;

            var start_time = $("#start_time").val();
            var end_time = $("#end_time").val();

            var temporary = $.parseJSON($('input[name=timeliness]:checked').val());

            if ( temporary ){

                if (start_time == "" || end_time == "") {
                    alert('请选择起始时间或者结束时间');
                    return false;
                }

                if (start_time > end_time) {
                    alert('起始时间不能大于结束时间!');
                    return false;
                }

                if ( parseInt((new Date( $("#end_time").val() ) - new Date( $("#start_time").val() )) / 1000) < 600 ){
                    alert('结束时间要在开始时间10分钟之后');
                    return false;
                }
            }

            if (room == '0'){
                // 如果没有选择全部的机房IP
                if (typeof(ips) == 'boolean'){
                    if (!ips){
                        alert('你添加了单个IP，但是没有选择');
                        return false;
                    }
                } else {
                    if (ips.length == 0){
                        alert('你没有添加任何IP或者机房的全部IP');
                        return false;
                    }
                }
            } else {
                // 如果选择了全部的机房IP
                if (typeof(ips) == 'boolean'){
                    alert('你添加了单个IP，但是没有选择');
                    return false;
                }
            }

            var result = checkBefore(project, title, key, reason);

            var inputs = {
                'project': project,
                'title': title,
                'reason': reason,
                'key': key,
                'is_root': is_root,
                'room': room,
                'ips': ips,
                'group': group,
                'start_time': start_time,
                'end_time': end_time,
                'temporary': temporary,
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
                    },
                    error: function (data) {
                        alert(data);
                    }
                });
            }
        },

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    /*$("#all_ip").click( function(){
        if ( $("#all_ip").is(':checked') ){
            $("#ips").val('').trigger('change');
            $("#ips").prop("disabled", true);

        } else {
            $("#ips").prop("disabled", false);
        }
    } );*/

    $("#myAdd").click( function(){
        var add_str = `<div class="form-group">
                          <div class="col-sm-6">
                            <select class="ip_room" style="width: 100%">
                              <option value="0" selected="selected">选择IP-机房</option>
                            </select>
                          </div>
                          <button class="btn btn-danger btn-sm myRemove" type="button">x</button>
                        </div>
                        `
        $("#insert_ip_before").before(add_str);

        // 初始化select2
        var selector = $($($("#insert_ip_before").prev().children().get(0)).children().get(0));
        initIpRoom(selector);

        // 添加删除按钮的监听事件
        $(".myRemove").click( function(){
            $(this).parent().remove();
        } );
    } );

    $("#myAdd2").click( function(){
        var add_str = `<div class="form-group">
                          <div class="col-sm-6">
                            <select class="ip_room" style="width: 100%">
                              <option value="0" selected="selected">选择IP-机房-区服ID</option>
                            </select>
                          </div>
                          <button class="btn btn-danger btn-sm myRemove2" type="button">x</button>
                        </div>
                        `
        $("#insert_gameserver_before").before(add_str);

        // 初始化select2
        var selector = $($($("#insert_gameserver_before").prev().children().get(0)).children().get(0));
        initGameServerIP(selector);

        // 添加删除按钮的监听事件
        $(".myRemove2").click( function(){
            $(this).parent().remove();
        } );
    } );
    
} );
