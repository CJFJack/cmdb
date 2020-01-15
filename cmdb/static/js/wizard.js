/**
 * Created by horace on 16-7-12.
 */

//Make sure jQuery has been loaded before platform_wizard.js
if (typeof jQuery === "undefined") {
  throw new Error("This JS requires jQuery");
}

var $select2room_name;
var $select2web_conf;
var $platform_wizard_step;

// =====存放第一页数据==== //
var page1_room_name;
var page1_PlatformName;
var page1_PlatformType;
var page1_PlatformTypeName;    // 这个变量用来存放UAT, SIT之类的
var page1_CompanyName;
var company;
var page1_PM_name;
var page1_DM_name;
var confirm_platform_name;
// =====存放第二页数据==== //
var page2_host_json = {};
var page2_host_list;
var page2_service;
// =====存放第三页数据==== //
var page3_network_policy = [];
// =====判断是否已经确认跳过网络策略页码==== //
var skip_network_policy_state = false;
// =====判断是否已经提交数据======= //
var page2_already_finished = false;
// =====存放第三页数据==== //
var page3_network_policy_json;

// 存放每次到第二页的uuid全局变量
var uuid;

var typeArray = ['web','app','mag','ser','msg','cache','jump','db'];
var platform_type_list = [{id: 'U', text: 'UAT'}, {id: 'S', text: 'SIT'},
    {id: 'P', text: 'PRD'}, {id: 'V', text: '运维'}, {id: 'D', text: '灾备'}];
var company_list = [{id: 'A', text: '网金'}, {id: 'B', text: '钱端'},
    {id: 'C', text: '钱途'}, {id: 'D', text: '大数据'}];
var typeArrayName = {'web':'W', 'app':'A', 'ser':'S', 'cache':'C','mag':'M', 'msg':'G', 'db':'D', 'jump': 'J'};

// =======================init============================ //
$(document).ready(function() {
    initSteps();
    initSelect2();
    initSelectGenIP();
    $("#gen_ip").click(function () {
        var text = $("#gen_ip_by_typeName").select2('data')[0];
        if(text){
            addOne(text.text);
            console.log(occupied_ip);
            console.log(occupied_ip_info);
        }else{
            $.alert("请选择IP类型！");
        }
    });
    $("#clear_ip").click(function () {
        var data = {
            'uuid': uuid,
            'clear_field': 'ip_pool_id',
        };
        var encoded = $.toJSON(data);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/assets/reset_using_ip_pool/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function(data){
                $("#ip_list_info").html("");
                occupied_ip = [];
                occupied_ip_info = [];
            }
        });
    });
    // initStepsPage2();
    var table = $('#add_host_datatable').DataTable({
        dom: "<'row'<'col-sm-12'tr>>",
        bSort: false,
    });
    var table2 = $('#network_policy_table').DataTable({
        dom: "tr",
        bSort: false,
        pageLength:50,
        scrollY: '100vh',
        scrollX: true,
        scrollCollapse: true
    });

    $('#network_policy_add').on( 'click', function () {
        table2.row.add( [
            '<input style="width: 100%" class="policy_name">',
            '<select style="width: 100%" class="src_platform"></select>',
            '<select style="width: 100%" class="src_host"></select>',
            '<select style="width: 100%" class="src_ip"></select>',
            '<select style="width: 100%" class="dst_platform"></select>',
            '<select style="width: 100%" class="dst_host"></select>',
            '<select style="width: 100%" class="dst_ip"></select>',
            '<select style="width: 100%" class="protocol"></select>',
            '<input style="width: 100%" class="port" placeholder="3306">',
            '<input style="width: 100%" class="start_date" placeholder="默认当天">',
            '<input style="width: 100%" class="end_date" placeholder="默认永久">'
        ] ).draw( false );
        initStepsPage2Last();
    });
    $('#network_policy_del').on( 'click', function () {
        row_nums = table2.rows().count();
        console.log(row_nums);
        table2.row(row_nums-1).remove().draw()
    });
    $('#page2_info').on('click', function () {
        var html_info;
        (function () {
                var html = '<h3>新增服务器清单：</h3><ol>';
                for(value in page2_host_list){
                    html = html + "<li>&nbsp;"+value+":"+page2_host_list[value]+"&nbsp;</li>";
                }
                html = html + '</ol><h3>VIP清单：</h3><ol>';
                occupied_ip_info.forEach(function (value) {
                    html = html + "<li>&nbsp;"+value[1]+"&nbsp;</li>";
                });
                html_info = html + "</ol>"
        })();
        $.dialog({
            title: false,
            content: html_info,
            columnClass: 'col-md-4 col-md-offset-4',
            backgroundDismiss: true
        });
    })
});




// =========================function====================== //


function initSteps() {
    $platform_wizard_step = $("#platform_wizard_step").steps({
    /* Appearance */
    headerTag: "h3",
    bodyTag: "section",
    contentContainerTag: "div",
    actionContainerTag: "div",
    stepsContainerTag: "div",
    cssClass: "wizard",
    stepsOrientation: $.fn.steps.stepsOrientation.horizontal,

    // transitionEffect: "slideLeft",

    /* Templates */
    titleTemplate: '<span class="number">#index#.</span> #title#',
    loadingTemplate: '<span class="spinner"></span> #text#',

    /* Transition Effects */
    transitionEffect: $.fn.steps.transitionEffect.none,
    transitionEffectSpeed: 200,

    /* Events */
    onStepChanging: function (event, currentIndex, newIndex) {

        // Allways allow previous action even if the current form is not valid!
        if (currentIndex > newIndex)
        {
            return true;
        }
        if (currentIndex < newIndex)
        {
            $("#platform_wizard_step").find(".body .error").removeClass("error");
            if (currentIndex == 0){
                // checkValidate("#room_name");
                var url = '/assets/confirm_platform_name/'+$("#platform_name").val()+'/';
                $.ajax({
                    type:'GET',
                    url: url,
                    dataType:'json',
                    async:false,
                    success:function(data){
                        confirm_platform_name = data["result"];
                    }
                });
                if ($("#room_name").val()==null){$.alert({
                                                        title:"提示",
                                                        content:"请选择机房！",
                                                        confirmButton: '确认',
                                                        confirmButtonClass: 'btn-primary'
                                                        })
                                                ;return false}
                if ($("#platform_name").val()==""){ $("#platform_name").addClass("error");
                                                    $.alert({
                                                        title:"提示",
                                                        content:"请填写平台名称！",
                                                        confirmButton: '确认',
                                                        confirmButtonClass: 'btn-primary'
                                                        });
                                                    return false}
                if (confirm_platform_name){ $("#platform_name").addClass("error");
                                            $.alert({
                                                    title:"提示",
                                                    content:"平台名称重名！",
                                                    confirmButton: '确认',
                                                    confirmButtonClass: 'btn-primary'
                                                    });
                                            return false}
                if ($("#project_manager").val()==""){ $("#project_manager").addClass("error");
                                                    $.alert({
                                                        title:"提示",
                                                        content:"请填写项目经理！",
                                                        confirmButton: '确认',
                                                        confirmButtonClass: 'btn-primary'
                                                        });
                                                    return false }
                if ($("#development_manager").val()==""){ $("#development_manager").addClass("error");
                                                        $.alert({
                                                            title:"提示",
                                                            content:"请填写研发经理！",
                                                            confirmButton: '确认',
                                                            confirmButtonClass: 'btn-primary'
                                                            });
                                                        return false }
                return true;
            }
            if (currentIndex == 1){
                if(!page2_already_finished){
                    $.alert({
                            title:"提示",
                            content:"您需要先提交本页信息，才能进行下一步！",
                            confirmButton: '确认',
                            confirmButtonClass: 'btn-primary'
                            });
                    return false;
                }
                if (!skip_network_policy_state){
                            $.confirm({
                                title: '确认框',
                                content: '是否添加网络策略？',
                                confirmButton: '添加',
                                cancelButton: '跳过',
                                confirmButtonClass: 'btn-primary',
                                cancelButtonClass: 'btn-info',
                                confirm: function(){
                                    $("#platform_wizard_step").steps("next");
                                },
                                cancel: function(){

                                    // $("#platform_wizard_step").steps('remove',2);
                                    $("#platform_wizard_step").steps('setStep',3)
                                }
                            });
                        skip_network_policy_state = true;
                }else{
                    return true;
                }
            }
            if (currentIndex == 2) {
                page3_network_policy =[];
                for(var i=0;i<$(".policy_name").length;i++){
                    var policy_info = {};
                    policy_info['policy_name'] = $(".policy_name").eq(i).val();
                    policy_info['src_platform'] = !$.isEmptyObject($(".src_platform").eq(i).select2('data')) ? $(".src_platform").eq(i).select2('data')[0].text : false;
                    policy_info['src_platform_id'] = !$.isEmptyObject($(".src_platform").eq(i).select2('data')) ? $(".src_platform").eq(i).select2('data')[0].id : false;
                    policy_info['src_host'] = !$.isEmptyObject($(".src_host").eq(i).select2('data')) ? $(".src_host").eq(i).select2('data')[0].text : false;
                    policy_info['src_host_id'] = !$.isEmptyObject($(".src_host").eq(i).select2('data')) ?$(".src_host").eq(i).select2('data')[0].id : false;
                    policy_info['src_ip'] = !$.isEmptyObject($(".src_ip").eq(i).select2('data')) ? $(".src_ip").eq(i).select2('data')[0].text :false;
                    policy_info['dst_platform'] = !$.isEmptyObject($(".dst_platform").eq(i).select2('data')) ? $(".dst_platform").eq(i).select2('data')[0].text : false;
                    policy_info['dst_platform_id'] = !$.isEmptyObject($(".dst_platform").eq(i).select2('data')) ? $(".dst_platform").eq(i).select2('data')[0].id :false;
                    policy_info['dst_host'] = !$.isEmptyObject($(".dst_host").eq(i).select2('data')) ? $(".dst_host").eq(i).select2('data')[0].text:false;
                    policy_info['dst_host_id'] = !$.isEmptyObject($(".dst_host").eq(i).select2('data')) ? $(".dst_host").eq(i).select2('data')[0].id:false;
                    policy_info['dst_ip'] = !$.isEmptyObject($(".dst_ip").eq(i).select2('data')) ? $(".dst_ip").eq(i).select2('data')[0].text:false;
                    policy_info['protocol'] = $(".protocol").eq(i).val();
                    policy_info['port'] = $(".port").eq(i).val();
                    policy_info['start_date'] = $(".start_date").eq(i).val();
                    policy_info['end_date'] = $(".end_date").eq(i).val();
                    if(policy_info['policy_name'] && policy_info['src_platform'] &&  policy_info['src_host'] &&
                        policy_info['src_ip'] && policy_info['dst_platform'] && policy_info['dst_host'] &&
                        policy_info['dst_ip'] && policy_info['port'] ){
                        page3_network_policy.push(policy_info)
                    }else{
                        $.alert({
                            content: "除了生效时间，日期时间，其他都不可为空！",
                            title: false,
                            cancelButton: false,
                            closeIcon: false,
                            backgroundDismiss: true,
                            confirmButton: '确认',
                            confirmButtonClass: 'btn-primary'
                        });
                        return false
                    }
                }
                return true;
            }
            // $platform_wizard_step.find(".body:eq(" + newIndex + ") .error").removeClass("error");
        }
        // 如果是第二页，生成uuid
        /*if (currentIndex == 1){
            console.log('here');
            uuid = generateUUID();
            console.log(uuid);
        }*/

    },
    onStepChanged: function (event, currentIndex, priorIndex) {
        if (priorIndex == 0 ){
            // page1_room_name = $("#room_name").val();
            page1_room_name = $("#room_name").select2('data')[0].roomid,
            page1_PlatformName = $("#platform_name").val();
            page1_PlatformType = $("#platform_type").val();
            page1_PlatformTypeName = $("#platform_type").select2('data')[0].text;
            page1_CompanyName = $("#company_name").val();
            company = $("#company_name").select2('data')[0].text;
            page1_PM_name = $("#project_manager").val();
            page1_DM_name = $("#development_manager").val();
        }
        if (currentIndex == 3){
            var host_table_body = $("#host_table_body");
            var first = true;
            for(value in page2_host_list){
                if(first){
                    var html = "<ol>";
                    occupied_ip_info.forEach(function (value) {
                        html = html + "<li>"+value[1]+"</li>";
                    });
                    html = html + "</ol>"
                    host_table_body.append(
                        "<tr>" +
                        "<td rowspan="+Object.keys(page2_host_list).length+">"+page1_PlatformName+"</td>" +
                        "<td rowspan="+Object.keys(page2_host_list).length+">"+page2_service+"</td>" +
                        "<td>"+value+"</td>" +
                        "<td>"+page2_host_list[value][1]+ "</td>" +
                        "<td>"+page2_host_list[value][0]+' '+'Vlan:'+' '+page2_host_list[value][2]+' '+'Netmask:'+' '+page2_host_list[value][3]+' '+'Gateway:'+' '+page2_host_list[value][4]+' '+'Platform:'+' '+page2_host_list[value][5]+"</td>" +
                        "<td rowspan="+Object.keys(page2_host_list).length+">"+html+"</td>" +
                        "</tr>");
                    first = false
                }else{
                    host_table_body.append(
                        "<tr>" +
                        "<td>"+value+"</td>" +
                        "<td>"+page2_host_list[value][1]+"</td>" +
                        "<td>"+page2_host_list[value][0]+' '+'Vlan:'+' '+page2_host_list[value][2]+' '+'Netmask:'+' '+page2_host_list[value][3]+' '+'Gateway:'+' '+page2_host_list[value][4]+' '+'Platform:'+' '+page2_host_list[value][5]+ "</td>" +
                        "</tr>"
                    )
                }
            }
            var page4_policy_table = $("#page4_policy_table");
            page3_network_policy.forEach(function (data) {
                page4_policy_table.append(
                    "<tr>" +
                    "<td>"+data.policy_name+"</td>" +
                    "<td>"+data.src_platform+"</td>" +
                    "<td>"+data.src_host+"</td>" +
                    "<td>"+data.src_ip+"</td>" +
                    "<td>"+data.dst_platform+"</td>" +
                    "<td>"+data.dst_host+"</td>" +
                    "<td>"+data.dst_ip+"</td>" +
                    "<td>"+data.protocol+"</td>" +
                    "<td>"+data.port+"</td>" +
                    "<td>"+data.start_date+"</td>" +
                    "<td>"+data.end_date+"</td>" +
                    "</tr>");
            })
        }
        // 如果是第二页，生成uuid
        if (currentIndex == 1){
            uuid = generateUUID();
        }

    },
    onCanceled: function (event) { document.location.href="/assets/wizard/" },
    onFinishing: function (event, currentIndex) {
        if(currentIndex == 1) {
            page2_host_json = {};
            typeArray.forEach(function (type) {
                var data;
                // if ($("#" + type).val() && $("#" + type + "_count").val()!=0 && $("#" + type + "_count").val() && $("#" + type + "_conf").val() && $("#" + type + "_host_type").val() && $("#" + type + "_network_area").val()) {
                if ( $("#" + type + "_count").val()!=0 && $("#" + type + "_count").val() && $("#" + type + "_conf").val() && $("#" + type + "_host_type").val() && $("#" + type + "_network_area").val()) {
                    // 获取网络区域id的list
                    var list_network_area_id = new Array();
                    $("#" + type + "_network_area").select2('data').forEach(function(value, index){list_network_area_id.push(value.id)});

                    // 获取网络区域的list
                    var list_network_area = new Array();
                    $("#" + type + "_network_area").select2('data').forEach(function(value, index){list_network_area.push(value.text)});

                    // 获取操作系统的业务类型
                    var business_type = $("#" + type + "_conf").select2('data')[0].business_type.toLowerCase();

                    // 获取操作系统 Linux 或者windows, 取第一个字母大写
                    var os_type = $("#" + type + "_conf").select2('data')[0].os_type.substring(0, 1).toUpperCase();

                    // 查看是否绑定vip
                    if ( $("#" + type + "_with_vip").prop('checked') ){
                        with_vip = true;
                    } else {
                        with_vip = false;
                    }

                    data = {
                        // 'hostname': page1_PlatformType+page1_CompanyName+page1_room_name+typeArrayName[business_type]+ os_type +'00',
                        // 'hostname': page1_PlatformType+page1_CompanyName+page1_room_name+os_type+ typeArrayName[business_type] +'00',
                        'hostname': page1_PlatformType+page1_CompanyName+page1_room_name+os_type+ typeArrayName[business_type],
                        "type": $("#" + type).val(),
                        "count": $("#" + type + "_count").val(),
                        "conf": $("#" + type + "_conf").val(),
                        "host_type": $("#" + type + "_host_type").val(),
                        // "network_area_id": $("#" + type + "_network_area").val(),
                        // "network_area": $("#" + type + "_network_area").select2('data')[0].text,
                        "network_area_id": list_network_area_id,
                        "network_area": list_network_area,
                        "with_vip": with_vip,
                        // "vip_count":$("#"+ type+ "_vip").val(),
                        // "ip_count":$("#"+type+"_ip").val()
                    };
                    page2_host_json[type] = data;
                }
            });
            if($.isEmptyObject(page2_host_json)){
                $.alert({
                    title:"提示",
                    content:"您好像未增加任何主机，请确认！",
                    confirmButton: '确认',
                    confirmButtonClass: 'btn-primary'
                });
                return false;
            }
            else{
                // console.log(page2_host_json);
                var post_data = {
                    'host_data': page2_host_json,
                    'ip_data': occupied_ip_info,
                    'PM':page1_PM_name,
                    'DM':page1_DM_name,
                    'company': company,
                    'platformName':page1_PlatformName,
                    'serviceName':page1_PlatformName+'-未分配',
                    'room_name':page1_room_name,
                    'uuid': uuid,
                };
                var encoded = $.toJSON(post_data);
                var pdata = encoded;
                console.log(pdata);
                // return false;
                /* {"host_data":{
                    "web":{
                        "hostname":"UA1W000","type":"130","count":"2","conf":"238","host_type":"VM","network_area_id":["797"],"network_area":"业务-WEB-亚太"}
                    },
                    "ip_data":[],"PM":"faegae","DM":"faegae","platformName":"faega","serviceName":"faega-未分配","room_name":"1",
                    "uuid":"ae827a35-bba1-471b-8f90-9457088ab8de"}*/
                $.ajax({
                    url: "/assets/wizard/add_wizard_page2/",
                    method: "POST",
                    async: false,
                    data: pdata,
                    // data: page2_host_json,
                    dataType: "json",
                    error: function () {
                        $.alert({
                        title:"提示",
                        content:"提交异常,请检查IP池是否充足,是否有权限增加主机",
                        confirmButton: '确认',
                        confirmButtonClass: 'btn-primary'
                        });
                    },
                    success: function (data) {
                        if(data.result == true){
                            $("#platform_wizard_step").find(".actions a[href$='#finish']").parent().hide();
                            $("#platform_wizard_step").find(".actions a[href$='#cancel']").parent().hide();
                            page2_host_list = data.hosts
                            page2_service = data.service
                            $.dialog({
                                title: false, // hides the title.
                                cancelButton: false, // hides the cancel button.
                                confirmButton: false, // hides the confirm button.
                                closeIcon: false, // hides the close icon.
                                content: "已增加"+data.count+"台服务器,"+"服务名称："+data.service, // hides content block.
                                backgroundDismiss: true
                            });
                            page2_already_finished = true;
                            return true;
                        }
                        else{
                            $.alert({
                                title:"提示",
                                content:data.msg,
                                confirmButton: '确认',
                                confirmButtonClass: 'btn-primary'
                                });
                        }
                    },
                    statusCode:"",
                });
            }
        }
        if(currentIndex == 3) {
            var encoded = $.toJSON({"data":page3_network_policy});
            var pdata = encoded;
            console.log(pdata);
            if (!$.isEmptyObject(page3_network_policy)) {
                $.ajax({
                    type: "POST",
                    url: "/assets/wizard/add_multi_network_policy/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        if (data['data']) {
                            $.confirm({
                                title: "回执",
                                content: "添加成功，点击确认返回主页，点击取消留在当前页面",
                                confirmButton: '确认',
                                confirmButtonClass: 'btn-primary',
                                cancelButton: '取消',
                                cancelButtonClass: 'btn-info',
                                confirm: function () {
                                    // window.location.href = "/";
                                    window.location.href = "/assets/platform_detail/?platform_name=" + page1_PlatformName;
                                },
                                cancel: function () {
                                    $("#platform_wizard_step").find(".actions a[href$='#finish']").parent().hide();
                                }

                            })
                        }
                        else {
                            $.alert(data['msg']);
                        }
                    },
                    error: function (data) {
                        $.alert({
                        title:"提示",
                        content:"添加网络策略异常！",
                        confirmButton: '确认',
                        confirmButtonClass: 'btn-primary'
                        });
                    }
                })
            }else {
                $.confirm({
                            title: "确认",
                            content: "无网络策略需要添加，点击确认返回主页，点击取消留在当前页面",
                            confirmButton: '确认',
                            confirmButtonClass: 'btn-primary',
                            cancelButton: '取消',
                            cancelButtonClass: 'btn-info',
                            confirm: function () {
                                // window.location.href = "/";
                                window.location.href = "/assets/platform_detail/?platform_name=" + page1_PlatformName;
                            },
                            cancel: function () {
                                $("#platform_wizard_step").find(".actions a[href$='#finish']").parent().hide();
                            }
                        })
            }
        }
        return true;
    },
    onFinished: function (event, currentIndex) {
        if(currentIndex == 1){
    
        }
    },

    /* Behaviour */
    autoFocus: true,
    enableAllSteps: false,
    enableKeyNavigation: true,
    enablePagination: true,
    suppressPaginationOnFocus: true,
    enableContentCache: true,
    enableCancelButton: true,
    enableFinishButton: true,
    preloadContent: false,
    showFinishButtonAlways: false,
    forceMoveForward: true,
    saveState: true,
    startIndex: 0,
    labels: {
        cancel: "取消",
        current: "当前步骤:",
        pagination: "页码",
        finish: "保存",
        next: "下一步",
        previous: "上一步",
        loading: "加载中 ..."
    }
});
}



var confOptions = {
        placeholder: '请选择模板',
        // cacheDataSource: [],
        // minimumResultsForSearch: Infinity,
        ajax: {
            url: '/assets/list_ostype/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                 return {
                     q: params.term,
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
            cache: false
        }
};



function get_option_osType(apptype) {
    var selectOsType = $("#" + apptype +"_host_type").val();
    var areaOptions = {
        placeholder: '请选择网络区域',
        // cacheDataSource: [],
        // minimumResultsForSearch: Infinity,
        ajax: {
            url: '/assets/list_iptype/',
            dataType: 'json',
            type: 'POST',
            // data:{ip_type: 'VM'},
            data: function(params){
                return {
                    page1_PlatformTypeName: page1_PlatformTypeName,
                    q: params.term,
                }
            },
            delay: 250,
            // data: function (params) {
            //     return {
            //         q: params.term,
            //         page: params.page
            //     };
            // },

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
            cache: false
        },
        multiple: true,
        // dropdownAutoWidth: true,
    };
    return areaOptions
}

/*function get_option_appType(apptype) {
    var appTypeOptions = {
    placeholder: '请选择业务类型',
        // cacheDataSource: [],
        // minimumResultsForSearch: Infinity,
        ajax: {
            url: '/assets/list_apptype/',
            dataType: 'json',
            type: 'POST',
            data:{q: apptype},
            delay: 250,
            // data: function (params) {
            //     return {
            //         q: params.term,
            //         page: params.page
            //     };
            // },

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
            cache: false
        }
    };
    return appTypeOptions
}*/


function get_option_ostype(apptype){
    var confOptions = {
        placeholder: '请选择模板',
        // cacheDataSource: [],
        // minimumResultsForSearch: Infinity,
        ajax: {
            url: '/assets/list_ostype/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                 return {
                    business_type: apptype,
                    q: params.term,
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
                            business_type: item.business_type,
                            os_type: item.os_type,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false
        }
    };

    return confOptions;
};

function initSelect2(){
    //初始化业务类型select2
    // $(".os_conf").select2(confOptions);
    $(".os_conf").each(function(index, el) {
        var apptype = $(el).parent().siblings(":first").text();
        $(el).select2(get_option_ostype(apptype));
    });
    $(".host_type").select2({
        data:[{id: 'VM', text: '虚拟机'}, {id: 'PM', text: '物理机'}],
        minimumResultsForSearch: Infinity
    });
    typeArray.forEach(function (type) {
        $("#"+type+"_network_area").select2(get_option_osType(type))
    });
    typeArray.forEach(function (type) {
        $("#"+type+"_host_type").select().on("select2:select",function () {
            $("#"+type+"_network_area").val(null).html("").trigger("change").select2(get_option_osType(type));
        });
    });
    /*typeArray.forEach(function (type) {
        $("#"+type).select2(get_option_appType(type))
    });*/

    
    $select2room_name = $("#room_name").select2({
        placeholder: '请选择机房',
        // cacheDataSource: [],
        minimumResultsForSearch: Infinity,
        ajax: {
            url: '/assets/list_room/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function(params){
                return {
                    'list_room_id': true,
                    q: params.term,
                }
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
                            roomid: item.roomid,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false
        }
    });
    // $select2web_conf = $("#web_conf").select2(confOptions);
    $("#platform_type").select2({
        data: platform_type_list,
        minimumResultsForSearch: Infinity
    });
    $("#company_name").select2({
        data: company_list,
        minimumResultsForSearch: Infinity
    })
}

// function initStepsPage2() {
//     $(".src_platform").select2();
//     $(".src_host").select2();
//     $(".src_ip").select2();
//     $(".dst_platform").select2();
//     $(".dst_host").select2();
//     $(".dst_ip").select2();
//     $(".protocol").select2({
//         data: [
//             {'id': 'TCP', 'text':'TCP'},
//             {'id': 'UDP', 'text':'UDP'}
//         ],
//         minimumResultsForSearch: Infinity
//     });
//     $('.start_date').Zebra_DatePicker({
//         direction: true
//     });
//     $('.end_date').Zebra_DatePicker({
//         direction: true
//     });
//
//
//     $(".src_platform").select2({
//         /*data: [
//             {'id': 0, 'text':'虚拟机'},
//             {'id': 1, 'text':'物理机'},
//         ],*/
//         placeholder: '选择源平台',
//         // cacheDataSource: [],
//         // minimumResultsForSearch: Infinity,
//         ajax: {
//             url: '/assets/list_platform/',
//             dataType: 'json',
//             type: 'POST',
//             delay: 250,
//             data: function (params) {
//                 return {
//                     q: params.term,
//                     unfinished_platform: page1_PlatformName,
//                     page: params.page
//                 };
//             },
//
//             processResults: function (data, params) {
//                 // parse the results into the format expected by Select2
//                 // since we are using custom formatting functions we do not need to
//                 // alter the remote JSON data, except to indicate that infinite
//                 // scrolling can be used
//                 params.page = params.page || 1;
//                 return {
//                     results: $.map(data, function(item){
//                         return {
//                             id: item.id,
//                             text: item.text,
//                         }
//                     })
//                     // pagination: {
//                     //     more: (params.page * 30) < data.total_count
//                     // };
//                 }
//             },
//             cache: false
//
//         }
//     }).on('change', function () {
//         var prePlatform = $(this);
//         prePlatform.closest('td').next().find('.src_host').select2({
//             /*data: [
//                 {'id': 0, 'text':'虚拟机'},
//                 {'id': 1, 'text':'物理机'},
//             ],*/
//             placeholder: '选择源主机',
//             // minimumResultsForSearch: Infinity,
//             ajax: {
//                 url: '/assets/list_hosts/',
//                 // data: {platform: $select2Belongs_src_platform.val()},
//                 dataType: 'json',
//                 type: 'POST',
//                 delay: 250,
//                 data: function (params) {
//                     return {
//                         platform: prePlatform.val(),
//                         q: params.term,
//                         page: params.page
//                     };
//                 },
//
//                 processResults: function (data, params) {
//                     // parse the results into the format expected by Select2
//                     // since we are using custom formatting functions we do not need to
//                     // alter the remote JSON data, except to indicate that infinite
//                     // scrolling can be used
//                     params.page = params.page || 1;
//                     return {
//                         results: $.map(data, function(item){
//                             return {
//                                 id: item.id,
//                                 text: item.text,
//                             }
//                         })
//                         // pagination: {
//                         //     more: (params.page * 30) < data.total_count
//                         // };
//                     }
//                 },
//                 cache: false,
//             },
//         }).on('change', function () {
//             var preHost = $(this);
//             preHost.closest('td').next().find('.src_ip').html('').select2({
//                 /*data: [
//                     {'id': 0, 'text':'虚拟机'},
//                     {'id': 1, 'text':'物理机'},
//                 ],*/
//                 placeholder: '选择源IP',
//                 // minimumResultsForSearch: Infinity,
//                 ajax: {
//                     url: '/assets/list_host_ip/',
//                     // data: {host: $select2Belongs_src_host.val()},
//                     dataType: 'json',
//                     type: 'POST',
//                     delay: 250,
//                     data: function (params) {
//                         return {
//                             host: preHost.val(),
//                             q: params.term,
//                             page: params.page
//                         };
//                     },
//
//                     processResults: function (data, params) {
//                         // parse the results into the format expected by Select2
//                         // since we are using custom formatting functions we do not need to
//                         // alter the remote JSON data, except to indicate that infinite
//                         // scrolling can be used
//                         params.page = params.page || 1;
//                         return {
//                             results: $.map(data, function(item){
//                                 return {
//                                     id: item.id,
//                                     text: item.text,
//                                 }
//                             })
//                             // pagination: {
//                             //     more: (params.page * 30) < data.total_count
//                             // };
//                         }
//                     },
//                     cache: false,
//                 },
//             });
//         });
//     });
//
//     $(".dst_platform").select2({
//         /*data: [
//             {'id': 0, 'text':'虚拟机'},
//             {'id': 1, 'text':'物理机'},
//         ],*/
//         placeholder: '选择目的平台',
//         // minimumResultsForSearch: Infinity,
//         ajax: {
//             url: '/assets/list_platform/',
//             dataType: 'json',
//             type: 'POST',
//             delay: 250,
//             // data: function (params) {
//             //     return {
//             //         q: params.term,
//             //         page: params.page
//             //     };
//             // },
//
//             processResults: function (data, params) {
//                 // parse the results into the format expected by Select2
//                 // since we are using custom formatting functions we do not need to
//                 // alter the remote JSON data, except to indicate that infinite
//                 // scrolling can be used
//                 params.page = params.page || 1;
//                 return {
//                     results: $.map(data, function(item){
//                         return {
//                             id: item.id,
//                             text: item.text,
//                         }
//                     })
//                     // pagination: {
//                     //     more: (params.page * 30) < data.total_count
//                     // };
//                 }
//             },
//             cache: false,
//         },
//     }).on('change', function () {
//         var prePlatform = $(this);
//         prePlatform.closest('td').next().find('.dst_host').html('').select2({
//             /*data: [
//                 {'id': 0, 'text':'虚拟机'},
//                 {'id': 1, 'text':'物理机'},
//             ],*/
//             placeholder: '选择目的主机',
//             // minimumResultsForSearch: Infinity,
//             ajax: {
//                 url: '/assets/list_hosts/',
//                 // data: {platform: $select2Belongs_dst_platform.val()},
//                 dataType: 'json',
//                 type: 'POST',
//                 delay: 250,
//                 data: function (params) {
//                     return {
//                         platform: prePlatform.val(),
//                         q: params.term,
//                         page: params.page
//                     };
//                 },
//
//                 processResults: function (data, params) {
//                     // parse the results into the format expected by Select2
//                     // since we are using custom formatting functions we do not need to
//                     // alter the remote JSON data, except to indicate that infinite
//                     // scrolling can be used
//                     params.page = params.page || 1;
//                     return {
//                         results: $.map(data, function(item){
//                             return {
//                                 id: item.id,
//                                 text: item.text,
//                             }
//                         })
//                         // pagination: {
//                         //     more: (params.page * 30) < data.total_count
//                         // };
//                     }
//                 },
//                 cache: false,
//             },
//         }).on('change', function () {
//             var preHost = $(this);
//             preHost.closest('td').next().find('.dst_ip').html('').select2({
//                 /*data: [
//                     {'id': 0, 'text':'虚拟机'},
//                     {'id': 1, 'text':'物理机'},
//                 ],*/
//                 placeholder: '选择目的IP',
//                 // minimumResultsForSearch: Infinity,
//                 ajax: {
//                     url: '/assets/list_host_ip/',
//                     // data: {host: $select2Belongs_dst_host.val()},
//                     dataType: 'json',
//                     type: 'POST',
//                     delay: 250,
//                     data: function (params) {
//                         return {
//                             host: preHost.val(),
//                             q: params.term,
//                             page: params.page
//                         };
//                     },
//
//                     processResults: function (data, params) {
//                         // parse the results into the format expected by Select2
//                         // since we are using custom formatting functions we do not need to
//                         // alter the remote JSON data, except to indicate that infinite
//                         // scrolling can be used
//                         params.page = params.page || 1;
//                         return {
//                             results: $.map(data, function(item){
//                                 return {
//                                     id: item.id,
//                                     text: item.text,
//                                 }
//                             })
//                             // pagination: {
//                             //     more: (params.page * 30) < data.total_count
//                             // };
//                         }
//                     },
//                     cache: false,
//                 },
//             });
//         });
//     });
// }

function initStepsPage2Last() {
    $(".src_platform:last").select2();
    $(".src_host:last").select2();
    $(".src_ip:last").select2();
    $(".dst_platform:last").select2();
    $(".dst_host:last").select2();
    $(".dst_ip:last").select2();

    $(".protocol:last").select2({
        data: [
            {'id': 'TCP', 'text':'TCP'},
            {'id': 'UDP', 'text':'UDP'}
        ],
        minimumResultsForSearch: Infinity
    });
    $('.start_date:last').Zebra_DatePicker({
        direction: true
    });
    $('.end_date:last').Zebra_DatePicker({
        direction: true
    });


    $(".src_platform:last").select2({
        /*data: [
            {'id': 0, 'text':'虚拟机'},
            {'id': 1, 'text':'物理机'},
        ],*/
        placeholder: '选择源平台',
        // cacheDataSource: [],
        // minimumResultsForSearch: Infinity,
        ajax: {
            url: '/assets/list_platform/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term,
                    unfinished_platform: page1_PlatformName,
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
            cache: false
        }
    }).on('change', function () {
        var prePlatform = $(this);
        prePlatform.closest('td').next().find('.src_host').select2({
            /*data: [
                {'id': 0, 'text':'虚拟机'},
                {'id': 1, 'text':'物理机'},
            ],*/
            placeholder: '选择源主机',
            // minimumResultsForSearch: Infinity,
            ajax: {
                url: '/assets/list_hosts/',
                // data: {platform: $select2Belongs_src_platform.val()},
                dataType: 'json',
                type: 'POST',
                delay: 250,
                data: function (params) {
                    return {
                        platform: prePlatform.val(),
                        q: params.term,
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
            tags: true,
            escapeMarkup: function (markup) { return markup; }
        }).on('change', function () {
            var preHost = $(this);
            preHost.closest('td').next().find('.src_ip').html('').select2({
                /*data: [
                    {'id': 0, 'text':'虚拟机'},
                    {'id': 1, 'text':'物理机'},
                ],*/
                placeholder: '选择源IP',
                // minimumResultsForSearch: Infinity,
                ajax: {
                    url: '/assets/list_host_ip/',
                    // data: {host: $select2Belongs_src_host.val()},
                    dataType: 'json',
                    type: 'POST',
                    delay: 250,
                    data: function (params) {
                        return {
                            host: preHost.val(),
                            q: params.term,
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
                tags: true,
                escapeMarkup: function (markup) { return markup; }
            });
        });
    });

    $(".dst_platform:last").select2({
        /*data: [
            {'id': 0, 'text':'虚拟机'},
            {'id': 1, 'text':'物理机'},
        ],*/
        placeholder: '选择目的平台',
        // minimumResultsForSearch: Infinity,
        ajax: {
            url: '/assets/list_platform/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            // data: function (params) {
            //     return {
            //         q: params.term,
            //         page: params.page
            //     };
            // },

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
    }).on('change', function () {
        var prePlatform = $(this);
        prePlatform.closest('td').next().find('.dst_host').html('').select2({
            /*data: [
                {'id': 0, 'text':'虚拟机'},
                {'id': 1, 'text':'物理机'},
            ],*/
            placeholder: '选择目的主机',
            // minimumResultsForSearch: Infinity,
            ajax: {
                url: '/assets/list_hosts/',
                // data: {platform: $select2Belongs_dst_platform.val()},
                dataType: 'json',
                type: 'POST',
                delay: 250,
                data: function (params) {
                    return {
                        platform: prePlatform.val(),
                        q: params.term,
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
            tags: true,
            escapeMarkup: function (markup) { return markup; }
        }).on('change', function () {
            var preHost = $(this);
            preHost.closest('td').next().find('.dst_ip').html('').select2({
                /*data: [
                    {'id': 0, 'text':'虚拟机'},
                    {'id': 1, 'text':'物理机'},
                ],*/
                placeholder: '选择目的IP',
                // minimumResultsForSearch: Infinity,
                ajax: {
                    url: '/assets/list_host_ip/',
                    // data: {host: $select2Belongs_dst_host.val()},
                    dataType: 'json',
                    type: 'POST',
                    delay: 250,
                    data: function (params) {
                        return {
                            host: preHost.val(),
                            q: params.term,
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
                tags: true,
                escapeMarkup: function (markup) { return markup; }
            });
        });
    });
}

function initSelectGenIP() {
    $("#gen_ip_by_typeName").select2({
        placeholder: '选择IP分类',
        // cacheDataSource: [],
        minimumResultsForSearch: Infinity,
        ajax: {
            url: '/assets/list_iptype/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            // data: {'ip_type':'VIP'},
            data: function (params) {
                return {
                    q: params.term,
                    ip_type:'VIP',
                    // unfinished_platform: page1_PlatformName,
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
            cache: false

        }
    })
}

var occupied_ip = [];
var occupied_ip_info = [];

function addOne(typename){
    var typename = typename;

    // Requeir ip from Server!
    var data = {
        'typename': typename,
        'occupied_ip': occupied_ip,
        'platform_name': page1_PlatformName,
        'uuid': uuid,
    }
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/gen_ip/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            if ( data['success'] ){
                ip_info = JSON.parse(data.data);
                console.log(ip_info)
                if ($.parseJSON(data.is_in_pairs)){
                    $("#ip_list_info").append('<label class="label label-info">'+typename+'</label><button class="btn btn-sm btn-default list-ip">'+ip_info.ip[0]+'</button><button class="btn btn-sm btn-default">'+ip_info.ip[1]+'</button>&nbsp;&nbsp;&nbsp;&nbsp;')
                    occupied_ip_info.push([ip_info.id[0],ip_info.ip[0],ip_info.vlan[0]]);
                    occupied_ip_info.push([ip_info.id[1],ip_info.ip[1],ip_info.vlan[1]]);
                }else{
                    $("#ip_list_info").append('<label class="label label-info">'+typename+'</label><button class="btn btn-sm btn-default">'+ip_info.ip[0]+'</button>&nbsp;&nbsp;&nbsp;&nbsp;');
                    occupied_ip_info.push([ip_info.id[0],ip_info.ip[0],ip_info.vlan[0]]);
                }
                occupied_ip = occupied_ip.concat(ip_info.ip);
            }
            else {
                $.alert({
                            title:"提示",
                            content:data['msg'],
                            confirmButton: '确认',
                            confirmButtonClass: 'btn-primary'
                        });
            }
        }
    });
}



