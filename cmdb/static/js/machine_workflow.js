var workflow;
var $select2Applicant;
var $select2Name;
var $select2IpType;
var $select2Config;
var $select2Project;


function initModalSelect2(){
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

    $select2Name = $("#name").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2IpType = $("#ip_type").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2Config = $("#config").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2Config.on("select2:select", function (e) { show_custom("select2:select", e, $( this )); });

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
    $select2Project.on("select2:select", function (e){
        get_workflow_approve_user(workflow, $("#applicant").val(), $("#project").val())
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

// 获取流程的各个节点的审批人员
function get_workflow_approve_user(workflow, applicant_id, project_id){
    if ( applicant_id == '0' | project_id == '0' ){
        console.log('none')
    } else {
        var inputs = {
            'workflow': workflow,
            'applicant_id': applicant_id,
            'project_id': project_id,
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

function checkBefore(title, project, purpose){

    if (project == '0'){
        alert('请选择项目');
        return false;
    }

    if (title == ''){
        alert('请输入标题');
        return false;
    }

    if (purpose == ''){
        alert('请输入用途');
        return false;
    }

    if ( $(".machine-config-all").length == 0) {
        alert('请添加机器配置');
        return false;
    }

    var config_result = true;

    $(".machine-config-all").each(function(index, el) {
        var configs = $(el).children('.col-lg-3');
        var config_cpu = configs[0];
        var config_mem = configs[1];
        var config_disk = configs[2];

        var config_cpu_value = $(config_cpu).children().children('.machine-config-cpu').val();
        var config_mem_value = $(config_mem).children().children('.machine-config-mem').val();
        var config_disk_value = $(config_disk).children().children('.machine-config-disk').val();

        if ( config_cpu_value == '' || config_mem_value == '' || config_disk_value == '' ) {
            alert('请填写机器配置参数');
            // return false;
            config_result = false;
        }
    });

    if ( config_result ) {
        return true
    } else {
        return false;
    }
}


// 获取机器配置
function get_config(){
    var config = new Array();
    $(".machine-config-all").each(function(index, el) {
        info = {};
        var configs = $(el).children('.col-lg-3');
        var config_cpu = configs[0];
        var config_mem = configs[1];
        var config_disk = configs[2];

        var config_cpu_value = $(config_cpu).children().children('.machine-config-cpu').val();
        var config_mem_value = $(config_mem).children().children('.machine-config-mem').val();
        var config_disk_value = $(config_disk).children().children('.machine-config-disk').val();
        var config_number = $(el).children('.number').val();

        info['config_cpu_value'] = config_cpu_value;
        info['config_mem_value'] = config_mem_value;
        info['config_disk_value'] = config_disk_value;
        info['config_number'] = config_number;

        config.push(info);
    });

    return config;
}


// 监听增加台数和减少台数事件
function add_listen_number(selector){
    // 添加
    var number_add_selector = $(selector).children('.number-add');
    $(number_add_selector).click(function(event) {
        /* Act on the event */
        var number_selector = $(selector).children('.number');
        var current_number_value = parseInt($(number_selector).val());
        $(number_selector).val(current_number_value + 1);
    });

    // 删除
    var number_reduce_selector = $(selector).children('.number-reduce');
    $(number_reduce_selector).click(function(event) {
        /* Act on the event */
        var number_selector = $(selector).children('.number');
        var current_number_value = parseInt($(number_selector).val());
        if ( current_number_value == 1 ){
            return false;
        }
        $(number_selector).val(current_number_value - 1);
    });
}


$(document).ready(function() {

    workflow = $("#workflow_id").text();
    initModalSelect2();

    // 提交
    $("#bt-commit").confirm({
        text:"确定提交到下一步?",
        confirm: function(button){

            var applicant = $("#applicant").select2('data')[0].id;
            var title = $("#title").val();
            var project = $("#project").select2('data')[0].id;
            var purpose = $("#purpose").val();
            var ip_type = $("#ip_type").val();
            var number = $("#number").val();
            var requirements = $("#requirements").val();

            var config = get_config();

            var result = checkBefore(title, project, purpose);

            var inputs = {
                'applicant': applicant,
                'title': title,
                'project': project,
                'purpose': purpose,
                'ip_type': ip_type,
                'config': config,
                'number': number,
                'requirements': requirements,
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

    $("#myAdd").click(function(event) {
        /* 添加机器配置 */
        var server_config = '<div class="form-group machine-config-all">' +
                                '<label class="col-sm-12">机器配置</label>' +
                                '<div class="col-lg-3">' +
                                    '<div class="input-group">' +
                                        '<input type="text" class="form-control machine-config-cpu" placeholder="4">' +
                                        '<span class="input-group-addon">CPU核心数</span>' +
                                    '</div>' +
                                '</div>' +
                                '<div class="col-lg-3">' +
                                    '<div class="input-group">' +
                                        '<input type="text" class="form-control machine-config-mem" placeholder="8">' +
                                        '<span class="input-group-addon">内存G</span>' +
                                    '</div>' +
                                '</div>' +
                                '<div class="col-lg-3">' +
                                    '<div class="input-group">' +
                                        '<input type="text" class="form-control machine-config-disk" placeholder="100">' +
                                        '<span class="input-group-addon">硬盘G</span>' +
                                    '</div>' +
                                '</div>' +
                                '<button class="btn btn-danger btn-sm number-reduce" type="button">-</button>' +
                                '<input tpye="text" value=1 style="width: 5%" class="number" readonly="readonly"></input><span>台</span>' +
                                '<button class="btn btn-success btn-sm number-add" type="button">+</button>' +
                            '</div>'

        $("#add-server-config").after(server_config);
        var selector = $("#add-server-config").next();
        add_listen_number(selector);
    });

} );
