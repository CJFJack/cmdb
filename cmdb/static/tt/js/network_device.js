// 修改之前的数据
var origin_data;

var table;
var editFlag;
var deviceFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的网络设备?";
var count=0;

var occupied_ip_info = {};    //客户端占用的ip信息，带有IP类型的id和ip

var select2BelongsToOppositeEnd;

// 下面的变量用来记录input的id和select的id
var device_ip_id = 1;
var device_ip_network_area_id = 1;

var device_internal_ip_id = 1;
var device_internal_ip_network_area_id = 1;

var device_external_ip_id = 1
var device_external_ip_network_area_id = 1;

var device_loopback_ip_id = 1;
var device_loopback_ip_network_area_id = 1;


function format ( d ) {
    // `d` is the original data object for the row
    var ip_info = d.ip_info;
    // 只保留设备互联的
    delete ip_info["带内网管"];
    delete ip_info["带外网管"];
    delete ip_info["loopback"];
    var str = '';
    for (ip_type in ip_info){
        var table = '';
        // ip_info[ip_type] =  [
        //            {'ip1': {'对端设备1': '对端设备ip1'}},
        //            {'ip2': {'对端设备2': '对端设备ip2'}}
        //    ],
        var length = ip_info[ip_type].length;
        for (var x=0; x<length; x++){
            var el = ip_info[ip_type][x];    // {'ip1': {'对端设备1': '对端设备ip1'}}, or {'ip1': {}}
            var ip1 = Object.keys(el)[0];
            var ip1_dict = el[ip1];
            if (Object.keys(ip1_dict).length == 0){
                table += '<tr>' +
                            // '<td>'+ip_type+':</td>'+
                            '<td>'+ip1+'</td>'+
                            '<td>对端设备:</td>'+
                            '<td></td>'+
                            '<td>对端设备IP:</td>'+
                            '<td></td>'+
                         '</tr>';
            }else{
                var opposite_end1 = el[ip1];
                // var opposite_end_ip1 = el[ip1][opposite_end1]
                table += '<tr>' +
                            // '<td>'+ip_type+':</td>'+
                            '<td>'+ip1+'</td>'+
                            '<td>对端设备:</td>'+
                            '<td>'+Object.keys(opposite_end1)[0]+'</td>'+
                            '<td>对端设备IP:</td>'+
                            '<td>'+opposite_end1[Object.keys(opposite_end1)[0]]+'</td>'+
                         '</tr>';
            }
        };
        str += table;
    }
    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
        str +
    '</table>';
}

function initNetworkDeviceSelect2(selector){
    $("#"+selector).select2({
        ajax: {
            url: '/assets/list_network_area/',
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
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function initAddNetworkDeviceAreaSelect2(selector){
    $(selector).select2({
        ajax: {
            url: '/assets/list_network_area/',
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
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function initModalSelect2(){
    // 初始化select2

    $(".network_area").select2({
        ajax: {
            url: '/assets/list_network_area/',
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
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $("#binding_device").select2({
        ajax: {
            url: '/assets/list_network_device/',
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
        //minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    
    initOppositeEnd('.opposite_end');

    initOppositeEndIp('.opposite_end_ip');

    

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};

// ---------------------------------------

// 给每个下拉框预选择
function preSelect(selector, select_id, select_value){
    $(selector).html('');
    $(selector).append('<option value="' + select_id + '">'+select_value+'</option>');
    $(selector).select2('val',select_id,true);
}

// 从id为 ‘start’的地方到新增的input field
function fromStart2Input(selector){
    // var inputField = $($($($(selector).next().next().children().get(1)).children().children().get(1)).children().get(0));
    var inputField = $($($(selector).next().next().children().get(1)).children().children().get(0)).children()
    return inputField;
}

function fromStart2Networkarea(selector){
    // var network_area = $($($($(selector).next().next().children().get(1)).children().children().get(2)).children().get(0));
    var network_area = $($($($(selector).next().next().children().get(1)).children().children().get(1)).children().get(0));
    return network_area;
}

function fromStart2Vlan(selector){
    var vlan = $($($(selector).next().next().children().get(1)).children().children().get(2)).children();
    return vlan;
}

function fromStart2OppositeEnd(selector){
    // var opposite_end = $($($($(selector).next().next().next().children().get(1)).children().children().get(1)).children().get(0));
    var opposite_end = $($($(selector).next().next().next().children().get(1)).children().children().get(0)).children();
    return opposite_end;
}

function fromStart2OppositeEndIp(selector){
    // var opposite_end_ip = $($($($(selector).next().next().next().children().get(1)).children().children().get(2)).children().get(0));
    var opposite_end_ip = $($($(selector).next().next().next().children().get(1)).children().children().get(1)).children();
    return opposite_end_ip;
}

// 初始化对端设备select2
function initOppositeEnd(selector){
    var select2OppositeEnd = $(selector).select2({
        ajax: {
            url: '/assets/list_network_device/',
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
        //minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    select2OppositeEnd.on("select2:select", function (e){ log("select2:select", e, $(this)); });
}

// 初始化对端设备IP select2
function initOppositeEndIp(selector){
    var opposite_end = $($($(selector).parent().parent().children().get(0)).children().get(0)).select2('data')[0].id;
    $(selector).select2({
        ajax: {
            url: '/assets/list_opposite_end_ip/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    opposite_end: opposite_end,
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
        //minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function log(name, evt, selector){
    if (name == 'select2:select' || name == 'select2:select2'){
        // console.log(selector);
        var opposite_end = $($($(selector).parent().parent().children().get(1)).children().get(0));
        initOppositeEndIp(opposite_end);
    }
};


function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;

    $.ajax({
        type: "POST",
        url: "/assets/get_resource_network_device/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            occupied_ip_info = {};
            $("#myModalLabel").text("修改网络设备");
            $("#modal-notify").hide();

            $("#id").val(data.id);
            $("#show_id").hide();

            $(".addition").remove();

            $("#device_num").val(data.device_num);
            $("#device_name").val(data.device_name);


            // 清空model，如果有的设备没有某些类型的ip，会有一个之前的数据
            $("#device_ip_1").val('');
            $("#device_internal_ip_1").val('');
            $("#device_external_ip_1").val('');
            $("#device_loopback_ip_1").val('');


            // 预选择网络区域
            $('.network_area').each(function(index, el) {
                preSelect(el, '0', '选择网络区域');           
            });

            // 预选择对端设备
            $('.opposite_end').each(function(index, el) {
                preSelect(el, '0', '选择对端设备');
            });

            // 预选择对端设备IP

            $('.opposite_end_ip').each(function(index, el) {
                preSelect(el, '0', '选择对端IP');
            });


            // 配置设备互联IP
            var device_ip = data.device_ip;
            device_ip.forEach(function(el, index){
                if (index == 0){
                    $("#device_ip_1").val(el.ip);
                    $("#device_ip_1_vlan").val(el.vlan);
                    initSelect2("device_ip_network_area_1", el.network_area_id, el.network_area);
                    initSelect2("device_ip_opposite_end_1", el.opposite_end_id, el.opposite_end);
                    initSelect2("device_ip_opposite_end_ip_1", el.opposite_end_ip_id, el.opposite_end_ip);
                }else{
                    var addStr = '<div class="form-group addition">' +
                                   '<label class="col-lg-2 control-label">设备互联</label>' +
                                   '<div class="col-lg-10">' +
                                     '<div class="form-group row">' +
                                         '<div class="col-lg-4">' +
                                           '<input type="text" class="form-control device_ip" placeholder="192.168.1.1">' +
                                         '</div>' +
                                         '<div class="col-lg-3">' +
                                           '<select class="network_area" style="width: 115%">' +
                                             '<option selected="selected" value="0">选择网络区域</option>' +
                                           '</select>' +
                                         '</div>' +
                                         '<div class="col-lg-3">' +
                                            '<input type="text" class="form-control vlan" placeholder="vlan">' +
                                         '</div>' +
                                         '<div class="col-lg-1">' +
                                            '<button type="button" class="btn btn-outline btn-primary btn-sm btn-danger del_device_ip">删除</button>' +
                                         '</div>' +
                                     '</div>' +
                                    '</div>' +
                                 '</div>' +
                                 '<div class="form-group addition">' +
                                   '<label class="col-sm-2 control-label"></label>' +
                                   '<div class="col-lg-10">' +
                                     '<div class="form-group row">' +
                                       '<div class="col-lg-4">' +
                                         '<select class="device_ip_opposite_end opposite_end" style="width: 100%">' +
                                           '<option selected="selected" value="0">选择对端设备</option>' +
                                         '</select>' +
                                       '</div>' +
                                       '<div class="col-lg-4">' +
                                         '<select class="device_ip_opposite_end_ip opposite_end_ip" style="width: 110%">' +
                                           '<option selected="selected" value="0">选择对端IP</option>' +
                                         '</select>' +
                                       '</div>' +
                                     '</div>' +
                                    '</div>' +
                                 '</div>'

                    $("#device_start").next().after(addStr);
                    // var new_device_ip_network_area = $($($($("#add_ip").parent().parent().parent().next().next().children().get(1)).children().children().get(2)).children().get(0));

                    // 填充数据
                    // ip字段
                    var new_device_ip_input = fromStart2Input($("#device_start"));
                    $(new_device_ip_input).val(el.ip);

                    // 网络区域
                    var new_device_ip_network_area = fromStart2Networkarea($("#device_start"));
                    initAddNetworkDeviceAreaSelect2(new_device_ip_network_area);
                    preSelect(new_device_ip_network_area, el.network_area_id, el.network_area);

                    // vlan
                    var vlan = fromStart2Vlan($("#device_start"));
                    $(vlan).val(el.vlan);

                    // 对端设备
                    var new_opposite_end = fromStart2OppositeEnd($("#device_start"));
                    initOppositeEnd(new_opposite_end);
                    preSelect(new_opposite_end, el.opposite_end_id, el.opposite_end);

                    // 对端设备IP
                    var new_opposite_end_ip = fromStart2OppositeEndIp($("#device_start"))
                    initOppositeEndIp(new_opposite_end_ip);
                    preSelect(new_opposite_end_ip, el.opposite_end_ip_id, el.opposite_end_ip);

                    // 给删除添加监听事件
                    $(".del_device_ip").click(function(event) {
                        /* Act on the event */
                        // console.log($(this).parent().parent().parent());
                        $($(this)).parent().parent().parent().parent().next().remove();
                        $($(this)).parent().parent().parent().parent().remove();
                    });
                }
            });

            // 配置带内网管IP
            var device_internal_ip = data.device_internal_ip;
            device_internal_ip.forEach(function(el, index){
                if (index == 0){
                    $("#device_internal_ip_1").val(el.ip);
                    $("#device_internal_ip_1_vlan").val(el.vlan);
                    initSelect2("device_internal_ip_network_area_1", el.network_area_id, el.network_area);
                    initSelect2("device_internal_ip_opposite_end_1", el.opposite_end_id, el.opposite_end);
                    initSelect2("device_internal_ip_opposite_end_ip_1", el.opposite_end_ip_id, el.opposite_end_ip);
                }else{
                    var addStr = '<div class="form-group addition">' +
                                   '<label class="col-lg-2 control-label">带内网管</label>' +
                                   '<div class="col-lg-10">' +
                                     '<div class="form-group row">' +
                                         '<div class="col-lg-4">' +
                                           '<input type="text" class="form-control device_ip" placeholder="192.168.1.1">' +
                                         '</div>' +
                                         '<div class="col-lg-3">' +
                                           '<select class="network_area" style="width: 115%">' +
                                             '<option selected="selected" value="0">选择网络区域</option>' +
                                           '</select>' +
                                         '</div>' +
                                         '<div class="col-lg-3">' +
                                            '<input type="text" class="form-control vlan" placeholder="vlan">' +
                                         '</div>' +
                                         '<div class="col-lg-1">' +
                                            '<button type="button" class="btn btn-outline btn-primary btn-sm btn-danger del_device_ip">删除</button>' +
                                         '</div>' +
                                     '</div>' +
                                    '</div>' +
                                 '</div>' +
                                 '<div class="form-group addition" style="display: none;">' +
                                   '<label class="col-sm-2 control-label"></label>' +
                                   '<div class="col-lg-10">' +
                                     '<div class="form-group row">' +
                                       '<div class="col-lg-4">' +
                                         '<select class="device_ip_opposite_end opposite_end" style="width: 100%">' +
                                           '<option selected="selected" value="0">选择对端设备</option>' +
                                         '</select>' +
                                       '</div>' +
                                       '<div class="col-lg-4">' +
                                         '<select class="device_ip_opposite_end_ip opposite_end_ip" style="width: 110%">' +
                                           '<option selected="selected" value="0">选择对端IP</option>' +
                                         '</select>' +
                                       '</div>' +
                                     '</div>' +
                                    '</div>' +
                                 '</div>'


                    $("#device_internal_start").next().after(addStr);
                    // var new_device_ip_network_area = $($($($("#add_ip").parent().parent().parent().next().next().children().get(1)).children().children().get(2)).children().get(0));

                    // 填充数据
                    // ip字段
                    var new_device_ip_input = fromStart2Input($("#device_internal_start"));
                    $(new_device_ip_input).val(el.ip);

                    // 网络区域
                    var new_device_ip_network_area = fromStart2Networkarea($("#device_internal_start"));
                    initAddNetworkDeviceAreaSelect2(new_device_ip_network_area);
                    preSelect(new_device_ip_network_area, el.network_area_id, el.network_area);

                    // vlan
                    var vlan = fromStart2Vlan($("#device_internal_start"));
                    $(vlan).val(el.vlan);

                    // 对端设备
                    var new_opposite_end = fromStart2OppositeEnd($("#device_internal_start"));
                    initOppositeEnd(new_opposite_end);
                    preSelect(new_opposite_end, el.opposite_end_id, el.opposite_end);

                    // 对端设备IP
                    var new_opposite_end_ip = fromStart2OppositeEndIp($("#device_internal_start"))
                    initOppositeEndIp(new_opposite_end_ip);
                    preSelect(new_opposite_end_ip, el.opposite_end_ip_id, el.opposite_end_ip);

                    // 给删除添加监听事件
                    $(".del_device_ip").click(function(event) {
                        /* Act on the event */
                        // console.log($(this).parent().parent().parent());
                        $($(this)).parent().parent().parent().parent().next().remove();
                        $($(this)).parent().parent().parent().parent().remove();
                    });
                }
            });

            // 配置带外网管IP
            var device_external_ip = data.device_external_ip;
            device_external_ip.forEach(function(el, index){
                if (index == 0){
                    $("#device_external_ip_1").val(el.ip);
                    $("#device_external_ip_1_vlan").val(el.vlan);
                    initSelect2("device_external_ip_network_area_1", el.network_area_id, el.network_area);
                    initSelect2("device_external_ip_opposite_end_1", el.opposite_end_id, el.opposite_end);
                    initSelect2("device_external_ip_opposite_end_ip_1", el.opposite_end_ip_id, el.opposite_end_ip);
                }else{
                    var addStr = '<div class="form-group addition">' +
                                   '<label class="col-lg-2 control-label">带外网管</label>' +
                                   '<div class="col-lg-10">' +
                                     '<div class="form-group row">' +
                                         '<div class="col-lg-4">' +
                                           '<input type="text" class="form-control device_ip" placeholder="192.168.1.1">' +
                                         '</div>' +
                                         '<div class="col-lg-3">' +
                                           '<select class="network_area" style="width: 115%">' +
                                             '<option selected="selected" value="0">选择网络区域</option>' +
                                           '</select>' +
                                         '</div>' +
                                         '<div class="col-lg-3">' +
                                            '<input type="text" class="form-control vlan" placeholder="vlan">' +
                                         '</div>' +
                                         '<div class="col-lg-1">' +
                                            '<button type="button" class="btn btn-outline btn-primary btn-sm btn-danger del_device_ip">删除</button>' +
                                         '</div>' +
                                     '</div>' +
                                    '</div>' +
                                 '</div>' +
                                 '<div class="form-group addition" style="display: none;">' +
                                   '<label class="col-sm-2 control-label"></label>' +
                                   '<div class="col-lg-10">' +
                                     '<div class="form-group row">' +
                                       '<div class="col-lg-4">' +
                                         '<select class="device_ip_opposite_end opposite_end" style="width: 100%">' +
                                           '<option selected="selected" value="0">选择对端设备</option>' +
                                         '</select>' +
                                       '</div>' +
                                       '<div class="col-lg-4">' +
                                         '<select class="device_ip_opposite_end_ip opposite_end_ip" style="width: 110%">' +
                                           '<option selected="selected" value="0">选择对端IP</option>' +
                                         '</select>' +
                                       '</div>' +
                                     '</div>' +
                                    '</div>' +
                                 '</div>'


                    $("#device_external_start").next().after(addStr);
                    // var new_device_ip_network_area = $($($($("#add_ip").parent().parent().parent().next().next().children().get(1)).children().children().get(2)).children().get(0));

                    // 填充数据
                    // ip字段
                    var new_device_ip_input = fromStart2Input($("#device_external_start"));
                    $(new_device_ip_input).val(el.ip);

                    // 网络区域
                    var new_device_ip_network_area = fromStart2Networkarea($("#device_external_start"));
                    initAddNetworkDeviceAreaSelect2(new_device_ip_network_area);
                    preSelect(new_device_ip_network_area, el.network_area_id, el.network_area);

                    // vlan
                    var vlan = fromStart2Vlan($("#device_external_start"));
                    $(vlan).val(el.vlan);

                    // 对端设备
                    var new_opposite_end = fromStart2OppositeEnd($("#device_external_start"));
                    initOppositeEnd(new_opposite_end);
                    preSelect(new_opposite_end, el.opposite_end_id, el.opposite_end);

                    // 对端设备IP
                    var new_opposite_end_ip = fromStart2OppositeEndIp($("#device_external_start"))
                    initOppositeEndIp(new_opposite_end_ip);
                    preSelect(new_opposite_end_ip, el.opposite_end_ip_id, el.opposite_end_ip);

                    // 给删除添加监听事件
                    $(".del_device_ip").click(function(event) {
                        /* Act on the event */
                        // console.log($(this).parent().parent().parent());
                        $($(this)).parent().parent().parent().parent().next().remove();
                        $($(this)).parent().parent().parent().parent().remove();
                    });
                }
            });

            // 配置loopbackIP
            var device_loopback_ip = data.device_loopback_ip;
            device_loopback_ip.forEach(function(el, index){
                if (index == 0){
                    $("#device_loopback_ip_1").val(el.ip);
                    $("#device_loopback_ip_1_vlan").val(el.vlan);
                    initSelect2("device_loopback_ip_network_area_1", el.network_area_id, el.network_area);
                    initSelect2("device_loopback_ip_opposite_end_1", el.opposite_end_id, el.opposite_end);
                    initSelect2("device_loopback_ip_opposite_end_ip_1", el.opposite_end_ip_id, el.opposite_end_ip);
                }else{
                    var addStr = '<div class="form-group addition">' +
                                   '<label class="col-lg-2 control-label">loopback</label>' +
                                   '<div class="col-lg-10">' +
                                     '<div class="form-group row">' +
                                         '<div class="col-lg-4">' +
                                           '<input type="text" class="form-control device_ip" placeholder="192.168.1.1">' +
                                         '</div>' +
                                         '<div class="col-lg-3">' +
                                           '<select class="network_area" style="width: 115%">' +
                                             '<option selected="selected" value="0">选择网络区域</option>' +
                                           '</select>' +
                                         '</div>' +
                                         '<div class="col-lg-3">' +
                                            '<input type="text" class="form-control vlan" placeholder="vlan">' +
                                         '</div>' +
                                         '<div class="col-lg-1">' +
                                            '<button type="button" class="btn btn-outline btn-primary btn-sm btn-danger del_device_ip">删除</button>' +
                                         '</div>' +
                                     '</div>' +
                                    '</div>' +
                                 '</div>' +
                                 '<div class="form-group addition" style="display: none;">' +
                                   '<label class="col-sm-2 control-label"></label>' +
                                   '<div class="col-lg-10">' +
                                     '<div class="form-group row">' +
                                       '<div class="col-lg-4">' +
                                         '<select class="device_ip_opposite_end opposite_end" style="width: 100%">' +
                                           '<option selected="selected" value="0">选择对端设备</option>' +
                                         '</select>' +
                                       '</div>' +
                                       '<div class="col-lg-4">' +
                                         '<select class="device_ip_opposite_end_ip opposite_end_ip" style="width: 110%">' +
                                           '<option selected="selected" value="0">选择对端IP</option>' +
                                         '</select>' +
                                       '</div>' +
                                     '</div>' +
                                    '</div>' +
                                 '</div>'


                    $("#device_loopback_start").next().after(addStr);
                    // var new_device_ip_network_area = $($($($("#add_ip").parent().parent().parent().next().next().children().get(1)).children().children().get(2)).children().get(0));

                    // 填充数据
                    // ip字段
                    var new_device_ip_input = fromStart2Input($("#device_loopback_start"));
                    $(new_device_ip_input).val(el.ip);

                    // 网络区域
                    var new_device_ip_network_area = fromStart2Networkarea($("#device_loopback_start"));
                    initAddNetworkDeviceAreaSelect2(new_device_ip_network_area);
                    preSelect(new_device_ip_network_area, el.network_area_id, el.network_area);

                    // vlan
                    var vlan = fromStart2Vlan($("#device_loopback_start"));
                    $(vlan).val(el.vlan);

                    // 对端设备
                    var new_opposite_end = fromStart2OppositeEnd($("#device_loopback_start"));
                    initOppositeEnd(new_opposite_end);
                    preSelect(new_opposite_end, el.opposite_end_id, el.opposite_end);

                    // 对端设备IP
                    var new_opposite_end_ip = fromStart2OppositeEndIp($("#device_loopback_start"))
                    initOppositeEndIp(new_opposite_end_ip);
                    preSelect(new_opposite_end_ip, el.opposite_end_ip_id, el.opposite_end_ip);

                    // 给删除添加监听事件
                    $(".del_device_ip").click(function(event) {
                        /* Act on the event */
                        // console.log($(this).parent().parent().parent());
                        $($(this)).parent().parent().parent().parent().next().remove();
                        $($(this)).parent().parent().parent().parent().remove();
                    });
                }
            });

            $("#port").val(data.port);
            $("#remarks").val(data.remarks);
            $("#vc").val(data.vc);

            initSelect2('binding_device', data.binding_device_id, data.binding_device);

            $("#myModal").modal("show");

            // return false;
            


        },
        error: function(data){
            alert('你没有修改ip管理的权限');
        }
    });
};

function checkBeforeAdd(device_num,device_ip,device_internal_ip,device_external_ip,device_external_ip2,device_loopback_ip){

    if (!device_num){
        $('#lb-msg').text('设备号不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if ( device_ip ) {
        var device_ip_network_area_id = $("#device_ip_network_area").select2('data')[0].id;
        if ( device_ip_network_area_id == '0' ){
            $('#lb-msg').text('输入了设备ip，请选择相应的网络区域!');
            $('#modal-notify').show();
            return false;
        }else{
            occupied_ip_info[device_ip] = device_ip_network_area_id;
        }
    }
    if ( device_internal_ip ) {
        var device_internal_ip_network_area_id = $("#device_internal_ip_network_area").select2('data')[0].id;
        if ( device_internal_ip_network_area_id == '0' ){
            $('#lb-msg').text('输入了带外网管ip，请选择相应的网络区域!');
            $('#modal-notify').show();
            return false;
        }else{
            occupied_ip_info[device_internal_ip] = device_internal_ip_network_area_id;
        }
    }
    if ( device_external_ip ) {
        var device_external_ip_network_area_id = $("#device_external_ip_network_area").select2('data')[0].id;
        if ( device_external_ip_network_area_id == '0' ){
            $('#lb-msg').text('输入了带内网管ip，请选择相应的网络区域!');
            $('#modal-notify').show();
            return false;
        }else{
            occupied_ip_info[device_external_ip] = device_external_ip_network_area_id;
        }
    }
    if ( device_external_ip2 ) {
        var device_external_ip2_network_area_id = $("#device_external_ip2_network_area").select2('data')[0].id;
        if ( device_external_ip2_network_area_id == '0' ){
            $('#lb-msg').text('输入了带内网管ip，请选择相应的网络区域!');
            $('#modal-notify').show();
            return false;
        }else{
            occupied_ip_info[device_external_ip2] = device_external_ip2_network_area_id;
        }
    }
    if ( device_loopback_ip ) {
        var device_loopback_ip_network_area_id = $("#device_loopback_ip_network_area").select2('data')[0].id;
        if ( device_loopback_ip_network_area_id == '0' ){
            $('#lb-msg').text('输入了loopbakcip，请选择相应的网络区域!');
            $('#modal-notify').show();
            return false;
        }else{
            occupied_ip_info[device_loopback_ip] = device_loopback_ip_network_area_id;
        }
    }

    return true;
};

function formatRepo (repo) {
    
    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};


// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });


$(document).ready(function() {

    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ordering": false,
        "ajax": "/assets/data_network_device/",
        "columns": [
            {"data": null},
            {
                "className":      'details-control',
                "orderable":      false,
                "data":           null,
                "defaultContent": ''
            },
            {"data": 'id'},
            {"data": 'device_num'},
            {"data": "device_name"},
            {"data": "device_internal_ip"},
            {"data": "device_external_ip"},
            {"data": "device_loopback_ip"},
            {"data": "vc"},
            {"data": "port"},
            {"data": "binding_device"},
            {"data": "remarks"},
            {
              "data": null,
              "orderable": false,
            }
        ],
        "order": [[1, 'asc']],
        columnDefs: [
                {
                  'targets': 0,
                  'searchable':false,
                  'orderable':false,
                  'className': 'dt-body-center',
                  'render': function (data, type, full, meta){
                   return '<input type="checkbox">';
                  },
                },
                {
                    'targets': 2,
                    'visible': false,
                    'searchable': false,
                },
                {    
                    'targets': [5, 6, 7],
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },
                {
                    targets: 12,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                            ]
                        };
                        var html = template(context);
                        return html;
                    }
                }
        ],
        "language": {
                "url": "/static/js/i18n/Chinese.json"
        },
        // 'rowCallback': function(row, data, dataIndex){
        //     // If row ID is in list of selected row IDs
        //     if($.inArray(data[0], rows_selected) !== -1){
        //     $(row).find('input[type="checkbox"]').prop('checked', true);
        //     $(row).addClass('selected');
        //     }
        // },
    });

    $('#example tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
 
        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( format(row.data()) ).show();
            tr.addClass('shown');
        }
    } );

    // Handle click on table cells
    // $('#mytable tbody').on('click', 'td', function(e){
    //     $(this).parent().find('input[type="checkbox"]').trigger('click');
    // });

    $('#chb-all').on('click', function(e){
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function(i,n){
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked){
              $row.addClass('selected');
              count = getSelectedTable('ip_segment').length;
              makeTitle(str, count);
            }else{
              $row.removeClass('selected');
              count = 0;
              makeTitle(str, count);
            }
        });
    });

    initModalSelect2();
    

    $('#mytable tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );

        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( format(row.data()) ).show();
            tr.addClass('shown');
        }
    } );

    // Handle click on checkbox
    $('#mytable tbody').on('click', 'input[type="checkbox"]', function(e){
        var $row = $(this).closest('tr');

        var data = table.row($row).data();
        var index = $.inArray(data[0], rows_selected);

        if(this.checked && index === -1){
            rows_selected.push(data[0]);
        } else if (!this.checked && index !== -1){
            rows_selected.splice(index, 1);
        }

        if(this.checked){
            $row.addClass('selected');
            makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            makeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增网络设备");
        $("#modal-notify").hide();
        $("#show_id").hide();

        // 去除掉添加的
        $(".addition").remove();

        $(".vlan").val('');

        $("#id").val('');
        $("#device_num").val('');
        $("#device_name").val('');
        $("#device_ip_1").val('');
        $("#device_internal_ip_1").val('');
        $("#device_external_ip_1").val('');
        $("#device_loopback_ip_1").val('');

        /*initSelect2('device_ip_network_area_1', '0', '选择网络区域');
        initSelect2('device_internal_ip_network_area_1', '0', '选择网络区域');
        initSelect2('device_external_ip_network_area_1', '0', '选择网络区域');
        initSelect2('device_loopback_ip_network_area_1', '0', '选择网络区域');*/

        // 预选择网络区域
        $('.network_area').each(function(index, el) {
            preSelect(el, '0', '选择网络区域');           
        });

        // 预选择对端设备
        $('.opposite_end').each(function(index, el) {
            preSelect(el, '0', '选择对端设备');
        });

        // 预选择对端设备IP

        $('.opposite_end_ip').each(function(index, el) {
            preSelect(el, '0', '选择对端IP');
        });

        $("#port").val('');
        $("#remarks").val('');
        $("#route_type").val('');
        $("#vc").val('');
        initSelect2('binding_device', '0', '选择绑定网络设备');
        editFlag=false;
        occupied_ip_info = {};    // 清空

        
        $("#myModal").modal("show");
    } );
    $('#file-save').click( function () {
        $("#Modal-file").modal("hide");
    } );

    /*$('#bt-upload').click( function () {
        $("#Modal-file").modal("show");
        $("#upload-notify").hide();
    } );*/

    $('#bt-upload-notify').click( function () {
        $("#upload-notify").hide();
    } );
    $('#bt-modal-notify').click( function () {
        $("#modal-notify").hide();
    } );
    $('#bt-save').click( function(){
        var id = $("#id").val();
        var device_num = $("#device_num").val();
        var device_name = $("#device_name").val();
        var port = $("#port").val();
        var remarks = $("#remarks").val();
        var vc = $("#vc").val();
        var binding_device = $("#binding_device").select2('data')[0].id;
        // var opposite_end = $("#opposite_end").select2('data')[0].id;

        function collect_ip(){
            // 空的ip信息,数据格为{
            //                      'ip': ['网络区域id', '中间表名', '对端设备', '对端设备ip', 'vlan'],
            //                      'ip2': ['网络区域id2', '中间表名2', '对端设备2', '对端设备ip2', 'vlan']
            //                   }
            var ip_info = {};

            // 循环device_ip
            $(".device_ip").each(function(index, e){
                // console.log($(e).parent().next().children())
                var device_ip = $(e).prop('value');    // 1.1.1.1

                if (device_ip){
                    var network_area = $($($(e).parent().parent().parent().children().children().get(1)).children().get(0)).select2('data')[0].id;
                    var vlan = $($(e).parent().parent().parent().children().children().get(2)).children().val();
                    if (network_area == '0' || !vlan){
                        $('#lb-msg').text('输入了设备ip，请选择相应的网络区域和vlan');
                        $('#modal-notify').show();
                        // return false;
                        ip_info = false;
                    }else{
                        // ip_info[device_ip] = [network_area, 'network_device_ip'];
                        var opposite_end_line = $($(e).parent().parent().parent().parent().next().children().get(1)).children().children().parent();
                        // 对端设备select2
                        // console.log(opposite_end_line);
                        var opposite_end = $($($(opposite_end_line).children().get(0)).children().get(0)).select2('data')[0].id;
                        // console.log(opposite_end);
                        // 对端设备ip select2
                        var opposite_end_ip = $($($(opposite_end_line).children().get(1)).children().get(0)).select2('data')[0].text;
                        var opposite_end_ip_id = $($($(opposite_end_line).children().get(1)).children().get(0)).select2('data')[0].id;

                        if (opposite_end != '0'){
                            if (opposite_end_ip_id == '0'){
                                $('#lb-msg').text('选择了对端设备，请选择相应的ip!');
                                $('#modal-notify').show();
                                // return false;
                                ip_info = false;
                            }
                        }
                        ip_info[device_ip] = [network_area, 'network_device_ip', opposite_end, opposite_end_ip, vlan];
                    }
                }
            })

            $(".device_internal_ip").each(function(index, e) {
                var device_internal_ip = $(e).prop('value');

                if (device_internal_ip){
                    var network_area = $($($(e).parent().parent().parent().children().children().get(1)).children().get(0)).select2('data')[0].id;
                    var vlan = $($(e).parent().parent().parent().children().children().get(2)).children().val();
                    if (network_area == '0' || !vlan){
                        $('#lb-msg').text('输入了带内网管ip，请选择相应的网络区域或vlan');
                        $('#modal-notify').show();
                        // return false;
                        ip_info = false;
                    }else{
                        // ip_info[device_ip] = [network_area, 'network_device_ip'];
                        var opposite_end_line = $($(e).parent().parent().parent().parent().next().children().get(1)).children().children().parent();
                        // 对端设备select2
                        // console.log(opposite_end_line);
                        var opposite_end = $($($(opposite_end_line).children().get(0)).children().get(0)).select2('data')[0].id;
                        // console.log(opposite_end);
                        // 对端设备ip select2
                        var opposite_end_ip = $($($(opposite_end_line).children().get(1)).children().get(0)).select2('data')[0].text;
                        var opposite_end_ip_id = $($($(opposite_end_line).children().get(1)).children().get(0)).select2('data')[0].id;

                        if (opposite_end != '0'){
                            if (opposite_end_ip_id == '0'){
                                $('#lb-msg').text('选择了对端设备，请选择相应的ip!');
                                $('#modal-notify').show();
                                // return false;
                                ip_info = false;
                            }
                        }
                        ip_info[device_internal_ip] = [network_area, 'network_device_internal_ip', opposite_end, opposite_end_ip, vlan];
                    }
                }
            });

            $(".device_external_ip").each(function(index, e) {
                var device_external_ip = $(e).prop('value');

                if (device_external_ip){
                    var network_area = $($($(e).parent().parent().parent().children().children().get(1)).children().get(0)).select2('data')[0].id;
                    var vlan = $($(e).parent().parent().parent().children().children().get(2)).children().val();
                    if (network_area == '0' || !vlan){
                        $('#lb-msg').text('输入了带外网管ip，请选择相应的网络区域或vlan');
                        $('#modal-notify').show();
                        // return false;
                        ip_info = false;
                    }else{
                        // ip_info[device_ip] = [network_area, 'network_device_ip'];
                        var opposite_end_line = $($(e).parent().parent().parent().parent().next().children().get(1)).children().children().parent();
                        // 对端设备select2
                        // console.log(opposite_end_line);
                        var opposite_end = $($($(opposite_end_line).children().get(0)).children().get(0)).select2('data')[0].id;
                        // console.log(opposite_end);
                        // 对端设备ip select2
                        var opposite_end_ip = $($($(opposite_end_line).children().get(1)).children().get(0)).select2('data')[0].text;
                        var opposite_end_ip_id = $($($(opposite_end_line).children().get(1)).children().get(0)).select2('data')[0].id;

                        if (opposite_end != '0'){
                            if (opposite_end_ip_id == '0'){
                                $('#lb-msg').text('选择了对端设备，请选择相应的ip!');
                                $('#modal-notify').show();
                                // return false;
                                ip_info = false;
                            }
                        }
                        ip_info[device_external_ip] = [network_area, 'network_device_external_ip', opposite_end, opposite_end_ip, vlan];
                    }
                }
            });

            $(".device_loopback_ip").each(function(index, e) {
                var device_loopback_ip = $(e).prop('value');

                if (device_loopback_ip){
                    var network_area = $($($(e).parent().parent().parent().children().children().get(1)).children().get(0)).select2('data')[0].id;
                    var vlan = $($(e).parent().parent().parent().children().children().get(2)).children().val();
                    if (network_area == '0' || !vlan){
                        $('#lb-msg').text('输入了loopbackip，请选择相应的网络区域或vlan');
                        $('#modal-notify').show();
                        // return false;
                        ip_info = false;
                    }else{
                        // ip_info[device_ip] = [network_area, 'network_device_ip'];
                        var opposite_end_line = $($(e).parent().parent().parent().parent().next().children().get(1)).children().children().parent();
                        // 对端设备select2
                        // console.log(opposite_end_line);
                        var opposite_end = $($($(opposite_end_line).children().get(0)).children().get(0)).select2('data')[0].id;
                        // console.log(opposite_end);
                        // 对端设备ip select2
                        var opposite_end_ip = $($($(opposite_end_line).children().get(1)).children().get(0)).select2('data')[0].text;
                        var opposite_end_ip_id = $($($(opposite_end_line).children().get(1)).children().get(0)).select2('data')[0].id;

                        if (opposite_end != '0'){
                            if (opposite_end_ip_id == '0'){
                                $('#lb-msg').text('选择了对端设备，请选择相应的ip!');
                                $('#modal-notify').show();
                                // return false;
                                ip_info = false;
                            }
                        }
                        ip_info[device_loopback_ip] = [network_area, 'network_device_loopback_ip', opposite_end, opposite_end_ip, vlan];
                    }
                }
            });

            return ip_info;

        };

        var ip_info = collect_ip();

        console.log(ip_info);
        // return false;

        if (!ip_info){
            return false;
        }

        if (!device_num){
            $('#lb-msg').text('请输入设备号!');
            $('#modal-notify').show();
            return false;
        }

        var inputIds = {
                'id': id,
                'device_num': device_num,
                'device_name': device_name,
                'ip_info': ip_info,
                'port': port,
                'remarks': remarks,
                'vc': vc,
                "binding_device": binding_device,
                'origin_data': origin_data,
            };

        // console.log(occupied_ip_info);

        // return false;

        if (editFlag){
            var urls = "/assets/edit_data_network_device/";
        }
        else{
            var urls = "/assets/add_data_network_device/";
        }

        var encoded=$.toJSON( inputIds );
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                
                if (data['data']) {
                    table.ajax.reload();
                    $("#myModal").modal("hide");
                }else{
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                };
            },
            error: function (data) {
                $('#lb-msg').text('你没有增加基础资源的权限');
                $('#modal-notify').show();
            }
        });
    });

    $("#bt-del").confirm({
        //text:"确定删除所选的资源池?",
        confirm: function(button){
            var selected = getSelectedTable('id');

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_network_device/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        
                        if (data['data']) {
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        }else{
                            alert(data['msg'])
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        };
                    }
                });
            }
        },

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    $('#bt-upload').click(function(){
        $('#div-upload').toggleClass('hide');
    });


    $("#reset_binding_device").click(function(){
        $("#in_pair_with").html('');
        $("#in_pair_with").append('<option value="0">选择绑定网络设备</option>');
        $("#in_pair_with").select2('val', "0", true);
    });

    $("#reset_opposite_end").click(function(){
        initSelect2('belongs_to_platform', '0', '选择对端设备');
    });

    // 增加按钮事件
    $("#add_ip").click(function(event) {
        /* Act on the event */
        device_ip_id ++;
        var new_deivce_ip = 'device_ip' + '_' + device_ip_id;

        device_ip_network_area_id ++;
        var new_device_ip_network_area = 'device_ip_network_area' + '_' + device_ip_network_area_id;

        var addStr = '<div class="form-group addition">' +
                       '<label class="col-lg-2 control-label">设备互联</label>' +
                       '<div class="col-lg-10">' +
                         '<div class="form-group row">' +
                             '<div class="col-lg-4">' +
                               '<input type="text" class="form-control device_ip" id="'+new_deivce_ip+'" placeholder="192.168.1.1">' +
                             '</div>' +
                             '<div class="col-lg-3">' +
                               '<select id="'+new_device_ip_network_area+'" class="network_area" style="width: 115%">' +
                                 '<option selected="selected" value="0">选择网络区域</option>' +
                               '</select>' +
                             '</div>' +
                             '<div class="col-lg-3">' +
                                '<input type="text" class="form-control vlan" placeholder="vlan">' +
                             '</div>' +
                             '<div class="col-lg-1">' +
                                '<button type="button" class="btn btn-outline btn-primary btn-sm btn-danger del_device_ip">删除</button>' +
                             '</div>' +
                         '</div>' +
                        '</div>' +
                     '</div>' +
                     '<div class="form-group addition">' +
                       '<label class="col-sm-2 control-label"></label>' +
                       '<div class="col-lg-10">' +
                         '<div class="form-group row">' +
                           '<div class="col-lg-4">' +
                             '<select class="device_ip_opposite_end opposite_end" style="width: 100%">' +
                               '<option selected="selected" value="0">选择对端设备</option>' +
                             '</select>' +
                           '</div>' +
                           '<div class="col-lg-4">' +
                             '<select class="device_ip_opposite_end_ip opposite_end_ip" style="width: 110%">' +
                               '<option selected="selected" value="0">选择对端IP</option>' +
                             '</select>' +
                           '</div>' +
                         '</div>' +
                        '</div>' +
                     '</div>'


        // $(this).parent().parent().parent().next().after(addStr);
        $("#device_start").next().after(addStr);

        $(".del_device_ip").click(function(event) {
            /* Act on the event */
            // console.log($(this).parent().parent().parent());
            $($(this)).parent().parent().parent().parent().next().remove();
            $($(this)).parent().parent().parent().parent().remove();
        });

        initNetworkDeviceSelect2(new_device_ip_network_area);

        // 初始化新增的对端设备
        var new_opposite_end = fromStart2OppositeEnd($("#device_start"));
        var new_opposite_end_ip = fromStart2OppositeEndIp($("#device_start"));
        initOppositeEnd(new_opposite_end);
        initOppositeEndIp(new_opposite_end_ip);
    });

    $("#add_internal_ip").click(function(event) {
        /* Act on the event */
        device_internal_ip_id ++;
        var new_device_internal_ip = 'device_internal_ip' + '_' + device_internal_ip_id;

        device_internal_ip_network_area_id ++;
        var new_device_internal_ip_network_area = 'device_internal_ip_network_area' + '_' + device_internal_ip_network_area_id;

        var addStr = '<div class="form-group addition">' +
                       '<label class="col-lg-2 control-label">带内网管</label>' +
                       '<div class="col-lg-10">' +
                         '<div class="form-group row">' +
                             '<div class="col-lg-4">' +
                               '<input type="text" class="form-control device_ip" id="'+new_device_internal_ip+'" placeholder="192.168.1.1">' +
                             '</div>' +
                             '<div class="col-lg-3">' +
                               '<select id="'+new_device_internal_ip_network_area+'" class="network_area" style="width: 115%">' +
                                 '<option selected="selected" value="0">选择网络区域</option>' +
                               '</select>' +
                             '</div>' +
                             '<div class="col-lg-3">' +
                                '<input type="text" class="form-control vlan" placeholder="vlan">' +
                             '</div>' +
                             '<div class="col-lg-1">' +
                                '<button type="button" class="btn btn-outline btn-primary btn-sm btn-danger del_device_ip">删除</button>' +
                             '</div>' +
                         '</div>' +
                        '</div>' +
                     '</div>' +
                     '<div class="form-group addition" style="display: none;">' +
                       '<label class="col-sm-2 control-label"></label>' +
                       '<div class="col-lg-10">' +
                         '<div class="form-group row">' +
                           '<div class="col-lg-4">' +
                             '<select class="device_ip_opposite_end opposite_end" style="width: 100%">' +
                               '<option selected="selected" value="0">选择对端设备</option>' +
                             '</select>' +
                           '</div>' +
                           '<div class="col-lg-4">' +
                             '<select class="device_ip_opposite_end_ip opposite_end_ip" style="width: 110%">' +
                               '<option selected="selected" value="0">选择对端IP</option>' +
                             '</select>' +
                           '</div>' +
                         '</div>' +
                        '</div>' +
                     '</div>'

        $("#device_internal_start").next().after(addStr);


        $(".del_device_ip").click(function(event) {
            /* Act on the event */
            // console.log($(this).parent().parent().parent());
            $($(this)).parent().parent().parent().parent().next().remove();
            $($(this)).parent().parent().parent().parent().remove();
        });

        initNetworkDeviceSelect2(new_device_internal_ip_network_area);

        // 初始化新增的对端设备
        var new_opposite_end = fromStart2OppositeEnd($("#device_internal_start"));
        var new_opposite_end_ip = fromStart2OppositeEndIp($("#device_internal_start"));
        initOppositeEnd(new_opposite_end);
        initOppositeEndIp(new_opposite_end_ip);
    });

    $("#add_external_ip").click(function(event) {
        /* Act on the event */
        device_external_ip_id ++;
        var new_device_external_ip = 'device_external_ip' + '_' + device_external_ip_id;

        device_external_ip_network_area_id ++;
        var new_device_external_ip_network_area = 'device_external_ip_network_area' + '_' + device_external_ip_network_area_id;

        var addStr = '<div class="form-group addition">' +
                       '<label class="col-lg-2 control-label">带外网管</label>' +
                       '<div class="col-lg-10">' +
                         '<div class="form-group row">' +
                             '<div class="col-lg-4">' +
                               '<input type="text" class="form-control device_ip" id="'+new_device_external_ip+'" placeholder="192.168.1.1">' +
                             '</div>' +
                             '<div class="col-lg-3">' +
                               '<select id="'+new_device_external_ip_network_area+'" class="network_area" style="width: 115%">' +
                                 '<option selected="selected" value="0">选择网络区域</option>' +
                               '</select>' +
                             '</div>' +
                             '<div class="col-lg-3">' +
                                '<input type="text" class="form-control vlan" placeholder="vlan">' +
                             '</div>' +
                             '<div class="col-lg-1">' +
                                '<button type="button" class="btn btn-outline btn-primary btn-sm btn-danger del_device_ip">删除</button>' +
                             '</div>' +
                         '</div>' +
                        '</div>' +
                     '</div>' +
                     '<div class="form-group addition" style="display: none;">' +
                       '<label class="col-sm-2 control-label"></label>' +
                       '<div class="col-lg-10">' +
                         '<div class="form-group row">' +
                           '<div class="col-lg-4">' +
                             '<select class="device_ip_opposite_end opposite_end" style="width: 100%">' +
                               '<option selected="selected" value="0">选择对端设备</option>' +
                             '</select>' +
                           '</div>' +
                           '<div class="col-lg-4">' +
                             '<select class="device_ip_opposite_end_ip opposite_end_ip" style="width: 110%">' +
                               '<option selected="selected" value="0">选择对端IP</option>' +
                             '</select>' +
                           '</div>' +
                         '</div>' +
                        '</div>' +
                     '</div>'

        $("#device_external_start").next().after(addStr);

        $(".del_device_ip").click(function(event) {
            /* Act on the event */
            // console.log($(this).parent().parent().parent());
            $($(this)).parent().parent().parent().parent().next().remove();
            $($(this)).parent().parent().parent().parent().remove();
        });

        initNetworkDeviceSelect2(new_device_external_ip_network_area);

        // 初始化新增的对端设备
        var new_opposite_end = fromStart2OppositeEnd($("#device_external_start"));
        var new_opposite_end_ip = fromStart2OppositeEndIp($("#device_external_start"));
        initOppositeEnd(new_opposite_end);
        initOppositeEndIp(new_opposite_end_ip);
    });

    $("#add_loopback_ip").click(function(event) {
        /* Act on the event */
        device_loopback_ip_id ++;
        var new_device_loopback_ip = 'device_loopback_ip' + '_' + device_loopback_ip_id;

        device_loopback_ip_network_area_id ++;
        var new_device_loopback_ip_network_area = 'device_loopback_ip_network_area' + '_' + device_loopback_ip_network_area_id;

        var addStr = '<div class="form-group addition">' +
                       '<label class="col-lg-2 control-label">loopback</label>' +
                       '<div class="col-lg-10">' +
                         '<div class="form-group row">' +
                             '<div class="col-lg-4">' +
                               '<input type="text" class="form-control device_ip" id="'+new_device_loopback_ip+'" placeholder="192.168.1.1">' +
                             '</div>' +
                             '<div class="col-lg-3">' +
                               '<select id="'+new_device_loopback_ip_network_area+'" class="network_area" style="width: 115%">' +
                                 '<option selected="selected" value="0">选择网络区域</option>' +
                               '</select>' +
                             '</div>' +
                             '<div class="col-lg-3">' +
                                '<input type="text" class="form-control vlan" placeholder="vlan">' +
                             '</div>' +
                             '<div class="col-lg-1">' +
                                '<button type="button" class="btn btn-outline btn-primary btn-sm btn-danger del_device_ip">删除</button>' +
                             '</div>' +
                         '</div>' +
                        '</div>' +
                     '</div>' +
                     '<div class="form-group addition" style="display: none;">' +
                       '<label class="col-sm-2 control-label"></label>' +
                       '<div class="col-lg-10">' +
                         '<div class="form-group row">' +
                           '<div class="col-lg-4">' +
                             '<select class="device_ip_opposite_end opposite_end" style="width: 100%">' +
                               '<option selected="selected" value="0">选择对端设备</option>' +
                             '</select>' +
                           '</div>' +
                           '<div class="col-lg-4">' +
                             '<select class="device_ip_opposite_end_ip opposite_end_ip" style="width: 110%">' +
                               '<option selected="selected" value="0">选择对端IP</option>' +
                             '</select>' +
                           '</div>' +
                         '</div>' +
                        '</div>' +
                     '</div>'

        $("#device_loopback_start").next().after(addStr);

        $(".del_device_ip").click(function(event) {
            /* Act on the event */
            // console.log($(this).parent().parent().parent());
            $($(this)).parent().parent().parent().parent().next().remove();
            $($(this)).parent().parent().parent().parent().remove();
        });

        // 初始化网络区域
        initNetworkDeviceSelect2(new_device_loopback_ip_network_area);

        // 初始化新增的对端设备
        var new_opposite_end = fromStart2OppositeEnd($("#device_loopback_start"));
        var new_opposite_end_ip = fromStart2OppositeEndIp($("#device_loopback_start"));
        initOppositeEnd(new_opposite_end);
        initOppositeEndIp(new_opposite_end_ip);

    });

} );
