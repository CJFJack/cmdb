// 修改之前的数据
var origin_data;

var table;
var editFlag;
//预编译模板
var tpl = $("#tpl").html();

var str = "确定删除选中的服务?";
var count=0;

var template = Handlebars.compile(tpl);
var $select2Belongs_to_apptype;
var $select2Belongs_to_platform;
var $select2Attach_hosts;
var select2Belongs_to_iptype;
var select2Dns;
var select2Certificate;
var platform;

var occupied_ip = new Array();    //客户端占用的ip，还没有存入数据库的，需要在请求服务端的ip时，将此ip作为参数

//客户端占用的ip信息，带有IP类型的id和ip
// format {'192.168.1.1': [id, vlan]}
var occupied_ip_info = {};


var uuid;

function delByIp(ip){
    delete occupied_ip_info[ip];
};


// 给 input 添加change的监听事件
function inputOnChange(selector){

    $(selector).on('focusin', function(){
        // console.log("Saving value " + $(this).val());
        $(this).data('val', $(this).val());
    });

    $(selector).on("change paste", function() {
        var prev = $(this).data('val');
        var current = $(this).val();
        // 删除掉之前的occupied_in_info 里面的key,然后添加新的key
        occupied_ip_info[current] = occupied_ip_info[prev];
        delete occupied_ip_info[prev];
        console.log(occupied_ip_info);
    });
};

// Add selected ip type!
function addAll(uuid){
    var selectedType = $("#iptypes").select2('data');
    if (selectedType.length == 0) {
        return false;
    }
    var selectedTypeName = new Array();
    // Push selected name
    $("#iptypes").select2('data').forEach(function(info, i){ selectedTypeName.push(info.text) });
    var selectedTypeNameLength = selectedTypeName.length;
    for (var i=0; i<selectedTypeNameLength; i++){
        addOne(selectedTypeName[i],uuid);
    }
};

// Add one type of input text with button
function addOne(typename, uuid){
    var platform_id = $("#belongs_to_platform").select2('data')[0].id;
    var typename = typename;
    var showClass = "show_" + typename;
    var inputClass = "text_" + typename;
    var addStr = '<div class="form-group ip_field '+ showClass + '"><label class="col-lg-3 col-sm-3 control-label">' + typename + '</label><div class="col-lg-6"><input type="text" class="form-control '+ inputClass + '"></div><button class="btn btn-outline btn-danger btn-sm bt-delete" type="button">删除</button></div>';

    // Requeir ip from Server!
    var data = {
        'typename': typename,
        'occupied_ip': occupied_ip,
        'platform_id': platform_id,
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
                if ($.parseJSON(data.is_in_pairs)){
                    //$("#show_remarks").before(addStr);
                    //$("#show_remarks").before(addStr);
                    //$("#show_remarks").before('<li class="form-group ip_field '+ showClass + '"><label class="col-sm-3 control-label">' + typename + data['platform'] +'</label><div class="col-sm-7"><input type="text" class="form-control '+ inputClass + '"></div><button class="btn btn-outline btn-danger btn-sm bt-delete" type="button">删除</button></li>');
                    var typename_platform = JSON.parse(data['data']).platform;
                    for (var i=0; i<typename_platform.length; i++){
                        $("#show_remarks").before('<div class="form-group ip_field '+ showClass + '"><label class="col-lg-3 col-sm-3 control-label">' + typename + '-' + typename_platform[i] +'</label><div class="col-lg-6"><input type="text" class="form-control '+ inputClass + '"></div><button class="btn btn-outline btn-danger btn-sm bt-delete" type="button">删除</button></div>');
                    }

                }else{
                    $("#show_remarks").before(addStr);
                }

                // Add bt-delete event
                $(".bt-delete").click(function(){
                    //console.log($(this).parent());
                    var ip = $(this).parent()[0].children[1].children[0].value;
                    delByIp(ip);
                    occupied_ip.splice($.inArray(ip, occupied_ip), 1);
                    $(this).parent().remove();
                });

                //console.log(JSON.parse(data['data']).length);
                var ipinfo;
                ipinfo = JSON.parse(data['data']);

                // Find out the input element by typename
                var selector = ".text_" + typename;
                var all_typename = $(selector);

                // Since we just want the empty inputs
                var i = all_typename.length;
                while (i--) {
                    if (all_typename[i].value != '' ) {
                        all_typename.splice(i, 1)
                    }
                }
                console.log('当前占用IP',occupied_ip)
                // Let's add ipinfo to the inputs and also push to the occupied_ip
                all_typename.toArray().forEach(function(info, i){ info.value = ipinfo.ip[i]; });
                ipinfo.ip.forEach(function(info, i){ occupied_ip.push(info) });
                // Disabled the input
                // $(selector).attr('disabled', 'disabled');

                // add ip and id to the occupied_ip_info
                // ipinfo.ip.forEach(function(value, i){occupied_ip_info[value] = ipinfo.id[i]});
                ipinfo.ip.forEach(function(value, i){occupied_ip_info[value] = [ipinfo.id[i], ipinfo.vlan[i]]});
                // console.log('after add',occupied_ip_info);

                // 给ip_input 添加绑定事假
                if ($.parseJSON(data.is_in_pairs)){
                    var ip_input = $($("#show_remarks").prev().children().get(1)).children();
                    inputOnChange(ip_input);

                    var ip_input2 = $($("#show_remarks").prev().prev().children().get(1)).children();
                    inputOnChange(ip_input2);
                }else{
                    var ip_input = $($("#show_remarks").prev().children().get(1)).children();
                    inputOnChange(ip_input);
                }
            }
            else {
                $('#lb-msg').text(data['msg']);
                $('#modal-notify').show();                
            }
        }
    });
};


function addBr(position){
    // Add one <br class='adjust'> after a element id
    $(position).after("<br class='adjust'>");
};

function rmBr(position){
    // Remove one <br class="adjust">
    $(position).next().remove();
};


function addSelfInputField(info, hostname){
    // host_to_vip format is
                // [
                //    ['10.1.1.1','SIT-WEB-WEB',2,self, 'vlan'],
                //    ['10.1.1.2','SIT-WEB-DB',3,self, 'vlan']
                // ]
    // info is list
    // self is self
    var addStr = '<div class="form-group host-ip-input-field '+ info[0] + ' ' + hostname + '"><label class="col-lg-3 col-sm-3 control-label">'+ info[1] +'</label><div class="col-lg-6"><input type="text" style="width:100%" class="form-control" value="'+ info[0] + '"></div><button class="btn btn-outline btn-danger btn-sm bt-delete" type="button">删除</button></div>';
    //$("#show_ip_type").after(addStr);
    $("#show_remarks").before(addStr);
    var addElement = $("#show_remarks").prev();
    addElement.children()[1].children[0].disabled = true;
    // 可以重复添加相同的ip，js会自动忽略重复的
    occupied_ip_info[info[0]] = [info[2], info[4]];
}

function addHideInputField(info,hostname){
    // host_to_vip format is
                // [
                //    ['10.1.1.1','SIT-WEB-WEB',2,hostname, 'vlan'],
                //    ['10.1.1.1','SIT-WEB-WEB',2,hostname, 'vlan'],
                //    ['10.1.1.2','SIT-WEB-DB',3,hostname, 'vlan']
                // ]
    // info is list
    // hostname is hostname
    // add an input field with ip info,
    //var liId = hostname + '-' + info[0];
    var addStr = '<div class="form-group host-ip-input-field '+ info[0] + ' ' + hostname + '"><label class="col-lg-3 col-sm-3 control-label">'+ info[1] +'</label><div class="col-lg-6"><input type="text" style="width:100%" class="form-control" value="'+ info[0] + '"></div><button class="btn btn-outline btn-danger btn-sm bt-delete" type="button">删除</button></div>';
    //$("#show_ip_type").after(addStr);
    $("#show_remarks").before(addStr);
    var addElement = $("#show_remarks").prev();
    addElement.children()[1].children[0].disabled = true;
    //document.getElementById(liId).children[1].children[0].disabled = true;

    // 可以重复添加相同的ip，js会自动忽略重复的
    occupied_ip_info[info[0]] = [info[2], info[4]];


    // if the ip input field exist,hide.
    if ( document.getElementsByClassName(info[0]).length != 1 ) {
        //console.log('ip exist,hidden');
        //document.getElementById(liId).hidden = true;
        addElement[0].hidden = true;
    }

    // When edit, add to ip info if ip is not duplicate
    if ( editFlag ){
        if (!occupied_ip_info[info[0]]){
            // occupied_ip_info[info[0]] = info[2];
            occupied_ip_info[info[0]] = [info[2], info[4]];
        }
        //console.log(occupied_ip_info);
    }

    // Add event for bt-delete
    $(".bt-delete").click(function(){
        var ip = $(this).parent()[0].children[1].children[0].value;
        delByIp(ip);
        occupied_ip.splice($.inArray(ip, occupied_ip), 1);
        var classIp = document.getElementsByClassName(ip);
        var classIpLength = classIp.length;
        for (var i=0;i<classIpLength;i++){
            classIp[i].remove();
        }
        //$(this).parent().remove();
    });

};

function DisplayRemoveInputField(hostname){
    // Remove the input field when unselected
    //var hostnameToIp = document.getElementsByClassName(hostname)[0].className.split(/\s+/)[2];
    var classHostName = document.getElementsByClassName(hostname);
    console.log(classHostName);

    var hostnameToIp = new Array();
    for (var i=0;i<classHostName.length;i++){
        hostnameToIp.push(classHostName[i].className.split(/\s+/)[2]);
    }

    // Remove all hostname
    var classHostName_length = classHostName.length;
    for (var i=0;i<classHostName_length;i++){
        classHostName[0].remove();
    }

    // Display the hidden
    for (var i=0;i<hostnameToIp.length;i++){
        //console.log(hostnameToIp[i]);
        if ( document.getElementsByClassName(hostnameToIp[i]).length >=1 ){
            console.log('find other ip');
            // Always display the first one since it does't matter
            document.getElementsByClassName(hostnameToIp[i])[0].hidden = false;
        }
        else{
            if (editFlag){
                delByIp(hostnameToIp[i]);
            }
        }
        console.log('unselected',occupied_ip_info)
    }
};

function adjustWithSelect2(name, evt, className){
    //adjust with select2 multiple select
    //console.log(className.attr('id'));
    //console.log(evt.currentTarget);
    var selector = "#" + evt.currentTarget.parentNode.parentNode.id;
    if (name == "select2:select" || name == "select2:select2"){
        //var selectedCount = $("#attache_hosts").select2('data').length;
        //console.log(evt.params.data);
        var data = {
            'id': evt.params.data.id,
        };
        var encoded = $.toJSON(data);
        var pdata = encoded;

        var hostname = evt.params.data.text;

        if ( evt.currentTarget.id == "attache_hosts" ){
            $.ajax({
                type: "POST",
                url: "/assets/host_get_ip/",
                data: pdata,
                contentType: "application/json; charset=utf-8",
                success: function(data){
                    // !-- Add input field
                    var vip_info = $.parseJSON(data.host_vip);
                    console.log(vip_info);
                    vip_info.forEach(function(info, n){
                        //console.log(typeof vip_info[n][0]);
                        /*occupied_ip_info[vip_info[n][0]] = vip_info[n][1];
                        var typename = vip_info[n][1];
                        var showClass = "show_" + typename;
                        var inputClass = "text_" + typename;
                        var addStr = '<li class="form-group vip_field_' + evt.params.data.id + ' '+ showClass + '"><label class="col-sm-3 control-label">' + typename + '</label><div class="col-sm-7"><input type="text" style="width:100%" class="form-control ' + inputClass + '" value="'+ vip_info[n][0] + '"></div></li>';
                        var selector = '.text_' + typename;
                        $("#show_ip_type").after(addStr);
                        $(selector).attr('disabled', 'disabled');*/

                        // Add event for click
                        /*$(".delete").click(function(){
                             console.log($(this).parent());
                        });*/


                        addHideInputField(info,hostname);

                    });
                    //console.log(occupied_ip_info);
                    // -- End
                }
            });
        }
        //addBr(selector);
    }
    if (name == "select2:unselect"){
        console.log(evt.params.data);
        /*var input_selector = ".vip_field_" + evt.params.data.id;
        $(input_selector).toArray().forEach(function(info, i){
            var ip = info.children[1].children[0].value;
            console.log(input_selector);
            delByIp(ip);
        });
        $(input_selector).remove();*/
        DisplayRemoveInputField(evt.params.data.text);
        //$("#" + evt.currentTarget.id).val('').trigger("change");
        //rmBr(selector);
    }
};

function initModalSelect2(){
    // 初始化select2
    $select2Belongs_to_apptype = $('#belongs_to_apptype').select2( {
        ajax: {
            url: '/assets/list_apptype/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
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
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
        dropdownAutoWidth: true,
    });

    $select2Dns = $('#sdns').select2( {
        ajax: {
            url: '/assets/list_sdns/',
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
            cache: true,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
        dropdownAutoWidth: true,
    });

    $select2Certificate = $('#certificate').select2( {
        ajax: {
            url: '/assets/list_certificate/',
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
            cache: true,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
        dropdownAutoWidth: true,
    });


    $select2Belongs_to_platform = $('#belongs_to_platform').select2( {
        ajax: {
            url: '/assets/list_platform/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
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
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
        dropdownAutoWidth: true,
    });

    $select2Attach_hosts = $('#attache_hosts').select2( {
        ajax: {
            url: '/assets/list_hosts/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
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
        placeholder: '选择主机',
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        multiple: true,
        //templateResult: formatRepo, // omitted for brevity, see the source of this page
        //templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
        dropdownAutoWidth: true,
    });
    $select2Attach_hosts;
    $select2Attach_hosts.on("select2:select", function(e){ adjustWithSelect2("select2:select",e); });
    $select2Attach_hosts.on("select2:unselect", function(e){ adjustWithSelect2("select2:unselect",e); });


    $select2Belongs_to_platform;
    $select2Belongs_to_platform.on("select2:select", function (e){ log("select2:select", e); });

    $select2Belongs_to_iptype = $("#iptypes").select2({
        ajax: {
            url: '/assets/list_iptype/',
            dataType: 'json',
            type: 'POST',
            //data: {'ip_type': 'PM','addition_id': selected_addtion_iptype},
            data: function(term, page){
                return {
                    'ip_type': 'VIP',
                    //'addition_id': selected_addtion_iptype
                }
            },
            delay: 250,
            processResults: function (data, params) {
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
        placeholder: '选择IP类型',
        multiple: true,
        minimumResultsForSearch: Infinity,
        //escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        //templateResult: formatRepo, // omitted for brevity, see the source of this page
        //templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    $select2Belongs_to_iptype;
    $select2Belongs_to_iptype.on("select2:select", function(e){ adjustWithSelect2("select2:select",e); });
    $select2Belongs_to_iptype.on("select2:unselect", function(e){ adjustWithSelect2("select2:unselect",e); });
    $.fn.modal.Constructor.prototype.enforceFocus = function() {};


};

function log(name, evt, className){
    if (name == 'select2:select' || name == 'select2:select2'){
        platform = $("#belongs_to_platform").select2('data')[0].id;
        $('#attache_hosts').select2( {
            ajax: {
                url: '/assets/list_hosts/',
                dataType: 'json',
                type: 'POST',
                delay: 250,
                data: {'platform': platform},
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
            multiple: true,
            //templateResult: formatRepo, // omitted for brevity, see the source of this page
            //templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
            dropdownAutoWidth: true,
        });
        $("#attache_hosts").val('').trigger("change");
    }
};


function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    // 重新生成uuid
    uuid = generateUUID();
    var encoded = $.toJSON(data);
    // 隐藏继续添加按钮
    $("#bt-contiune-save").hide();
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_business_service/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
                origin_data = data;
                $("#myModalLabel").text("修改服务信息");
                $("#modal-notify").hide();
                $("#reset_ip").hide()
                // clear
                $(".adjust").remove();
                $(".ip_field").remove();
                $(".host-ip-input-field").remove();
                //console.log(data.typename_info);
                $("#service_id").val(data.id);
                $("#show_service_id").hide();

                $("#belongs_to_apptype").html('');
                $("#belongs_to_apptype").append('<option value="' + data.app_type_id + '">' + data.app_type_name + '</option>');
                $("#belongs_to_apptype").select2('val',data.app_type_id,true);

                $("#application_name").val(data.application_name);

                $("#hostname").val(data.hostname);

                //$("#belongs_to_platform").val('0').trigger('change');

                $("#belongs_to_platform").html('');
                $("#belongs_to_platform").append('<option value="' + data.platform_id + '">' + data.platform_name + '</option>');
                $("#belongs_to_platform").select2('val',data.platform_id,true);


                $("#sdns").html('');
                $("#sdns").append('<option value="' + data.sdns_id + '">' + data.sdns + '</option>');
                $("#sdns").select2('val',data.sdns_id,true);

                $("#certificate").html('');
                $("#certificate").append('<option value="' + data.certificate_id + '">' + data.certificate + '</option>');
                $("#certificate").select2('val',data.certificate_id,true);



                //$("#attache_hosts").html('');
                //$("#attache_hosts").append('<option value="' + data.app_type_id + '">' + data.app_type_name + '</option>');
                //$("#attache_hosts").select2('val',data.app_type_id,true);

                // !-- Add attache_hosts,multiple select!
                var host_info = $.parseJSON(data.host_info);
                $("#attache_hosts").html('');
                var values = Array();
                host_info.forEach(function(value, i){
                    $("#attache_hosts").append('<option value="' + value[1] + '">' + value[0] + '</option>');
                    values.push(value[1]);
                    //addBr("#show_attach_hosts");
                });
                $("#attache_hosts").select2('val',values,true);

                // -- End

                // !-- Add iptypes,multiple select!
                $("#iptypes").val('').trigger('change');
                $("#iptypes").html('');
                var values = Array();
                data.typename_info.forEach(function(info, i){
                    $("#iptypes").append('<option value="' + i + '">' + info + '</option>');
                    values.push(i);
                    //addBr("#show_ip_type");
                });
                $("#iptypes").select2('val',values);
                // -- End

                // !-- Add input field
                occupied_ip = Array();
                occupied_ip_info = {};
                /*var assgined_ip_info = $.parseJSON(data.assgined_ip);
                assgined_ip_info.forEach(function(info, n){
                    //occupied_ip_info[assgined_ip_info[n][0]] = assgined_ip_info[n][1];
                    var typename = assgined_ip_info[n][2];
                    var showClass = "show_" + typename;
                    var inputClass = "text_" + typename;
                    var addStr = '<li class="form-group ip_field '+ showClass + '"><label class="col-sm-3 control-label">' + typename + '</label><div class="col-sm-7"><input type="text" style="width:100%" class="form-control ' + inputClass + '" value="'+ assgined_ip_info[n][0] + '"></div></li>';
                    var selector = '.text_' + typename;
                    $("#show_ip_type").after(addStr);
                    $(selector).attr('disabled', 'disabled');


                });*/

                //显示自己的vip的input,同时更新occupied_ip_info
                // self_to_vip format is
                // [
                //    ['10.1.1.1','SIT-WEB-WEB',2,self, 'vlan'],
                //    ['10.1.1.2','SIT-WEB-DB',3,self, 'vlan']
                // ]
                var self_to_vip = $.parseJSON(data.self_to_vip);
                self_to_vip.forEach(function(info, n){
                    addSelfInputField(info, info[3]);
                });

                // host_to_vip format is
                // [
                //    ['10.1.1.1','SIT-WEB-WEB',2,hostname, 'vlan'],
                //    ['10.1.1.1','SIT-WEB-WEB',2,hostname, 'vlan'],
                //    ['10.1.1.2','SIT-WEB-DB',3,hostname, 'vlan']
                // ]
                var host_to_vip = $.parseJSON(data.host_to_vip);
                host_to_vip.forEach(function(info, n){
                    addHideInputField(info,info[3]);
                });

                // -- End

                /*var brCount = $.parseJSON(data.assgined_ip).length;    //增加br的个数
                for (var i=0; i<brCount; i++){
                    $("#show_ip_type").after("<br class='adjust'>");
                }*/

                $("#myModal").modal("show");


        },
        error: function(data){
            alert('你没有修改平台应用权限');
        }
    });
}

function formatRepo (repo) {
    
    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};

function addBeforeCheck(belongs_to_apptype,application_name,host_ids){
    if (belongs_to_apptype == '0'){
        $('#lb-msg').text('请选择应用类型!');
        $('#modal-notify').show();
        return false;
    }
    if (host_ids.length == 0){
        $('#lb-msg').text('请选择host!');
        $('#modal-notify').show();
        return false;
    }
    
    if (!application_name){
        $('#lb-msg').text('应用名不能为空!');
        $('#modal-notify').show();
        return false;
    }
    return true;
};

// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });


$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "autoWidth": false,
        "ajax": "/assets/data_service/",
        "ordering": false,
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": 'app_type'},
            {"data": 'app_detail_type'},
            {"data": 'application_name'},
            {"data": 'vip'},
            {"data": 'sdns'},
            {"data": 'certificate'},
            {"data": 'belongs_to_platform'},
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
                    'targets': 1,
                    'visible': false,
                    'searchable': false
                },
                {
                    'targets': 2,
                    "width": "10%",
                },
                {
                    'targets': 3,
                    "width": "10%",
                },
                {
                    'targets': 4,
                    "width": 1,
                },
                {    
                    'targets': [5],
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },
                {
                    'targets': 7,
                    "width": "10%",
                },
                {
                    targets: 9,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\', \'" + c.application_name + "\')", "type": "primary"},
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

    $('#chb-all').on('click', function(e){
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function(i,n){
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked){
              $row.addClass('selected');
              count = getSelectedTable().length;
              makeTitle(str, count);
            }else{
              $row.removeClass('selected');
              count = 0;
              makeTitle(str, count);
            }
        });
    });

    initModalSelect2();

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

    //删除
    $("#bt-del").confirm({
        //text:"确定删除所选的服务?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_service/",
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

    // 增加button
    $('#bt-add').click( function () {
        $("#show_service_id").hide();
        $("#show_belongs_to_apptpye").show();
        //$("#belongs_to_apptype").val('0').trigger("change");
        initSelect2('belongs_to_apptype', '0', '应用类型');
        $("#application_name").val('');
        $("#show_belongs_to_platform").show();
        //$("#belongs_to_platform").val('0').trigger("change");
        
        initSelect2('belongs_to_platform', '0', '选择平台');
        initSelect2('sdns', '0', '选择DNS');
        initSelect2('certificate', '0', '选择证书');


        $("#show_attach_hosts").show();
        $("#attache_hosts").val('').trigger("change");
        $("#iptypes").val('').trigger("change");
        $(".ip_field").remove();
        $(".host-ip-input-field").remove();
        $(".adjust").remove();

        //$('#hostname').val('');

        editFlag=false;
        occupied_ip = Array();
        occupied_ip_info = {};

        // 生成全局的uuid
        uuid = generateUUID();

        $("#myModalLabel").text('新增服务');
        $("#modal-notify").hide();
        $("#myModal").modal("show");
        $("#bt-contiune-save").show();
    } );

    $('#file-save').click( function () {
        $("#Modal-file").modal("hide");
    } );
    // $('#bt-export').click( function () {
    //     window.location.href()
    // } );
    $('#bt-upload').click( function () {
        $("#Modal-file").modal("show");
        $("#upload-notify").hide();
    } );

    $('#bt-upload-notify').click( function () {
        $("#upload-notify").hide();
    } );

    $('#bt-modal-notify').click( function () {
        $("#modal-notify").hide();
    } );

    $('#bt-save').click( function(){
        // 增加、修改保存
        var service_id = $("#service_id").val();
        var belongs_to_apptype = $("#belongs_to_apptype").select2('data')[0].id;
        var application_name = $("#application_name").val();
        var sdns = $("#sdns").select2('data')[0].id;
        var certificate = $("#certificate").select2('data')[0].id;
        var device_remarks = $("#device_remarks").val();
        //var hostname = $("#hostname").val();

        var attache_hosts = $("#attache_hosts").select2('data');
        var host_ids = Array();
        for (i=0; i<attache_hosts.length; i++){
            host_ids.push(attache_hosts[i].id)
        }

        var inputIds = {
            'id': service_id,
            'belongs_to_apptype': belongs_to_apptype,
            'application_name': application_name,
            'device_remarks': device_remarks,
            'sdns': sdns,
            'certificate': certificate,
            //'hostname': hostname,
            'host_ids': host_ids,
            'occupied_ip_info': occupied_ip_info,
            "origin_data": origin_data,
            'uuid': uuid,
        }

        if (!addBeforeCheck(belongs_to_apptype,application_name,host_ids)){
            return false;
        };

        console.log('POST ipinfo',occupied_ip_info);
        //return false;
        
        if (editFlag){
            var urls = "/assets/edit_data_service/"
        }
        else{
            var urls = "/assets/add_data_service/"
        };

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
                $('#lb-msg').text('你没有增加平台业务的权限');
                $('#modal-notify').show();
            }
        });
    });

    $('#bt-contiune-save').click( function(){
    // 继续增加、修改保存
        var service_id = $("#service_id").val();
        var belongs_to_apptype = $("#belongs_to_apptype").select2('data')[0].id;
        var application_name = $("#application_name").val();
        var sdns = $("#sdns").select2('data')[0].id;
        var certificate = $("#certificate").select2('data')[0].id;
        var device_remarks = $("#device_remarks").val();
        //var hostname = $("#hostname").val();

        var attache_hosts = $("#attache_hosts").select2('data');
        var host_ids = Array();
        for (i=0; i<attache_hosts.length; i++){
            host_ids.push(attache_hosts[i].id)
        }

        var inputIds = {
            'id': service_id,
            'belongs_to_apptype': belongs_to_apptype,
            'application_name': application_name,
            'device_remarks': device_remarks,
            'sdns': sdns,
            'certificate': certificate,
            //'hostname': hostname,
            'host_ids': host_ids,
            'occupied_ip_info': occupied_ip_info,
            "origin_data": origin_data,
            'uuid': uuid,
        }

        if (!addBeforeCheck(belongs_to_apptype,application_name,host_ids)){
            return false;
        };

        console.log('POST ipinfo',occupied_ip_info);
        //return false;
        
        if (editFlag){
            var urls = "/assets/edit_data_service/"
        }
        else{
            var urls = "/assets/add_data_service/"
        };

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
                    uuid = generateUUID();

                    editFlag=false;

                    $("#application_name").val('');
                    $("#device_remarks").val('');
                    //console.log('start');
                    $.toast({
                        text: "成功添加一个服务", // Text that is to be shown in the toast
                        heading: 'Success', // Optional heading to be shown on the toast
                        icon: 'success', // Type of toast icon
                        showHideTransition: 'slide', // fade, slide or plain
                        allowToastClose: true, // Boolean value true or false
                        hideAfter: 1000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                        stack: 5, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                        position: 'top-center', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values
                        
                        
                        
                        textAlign: 'left',  // Text alignment i.e. left, right or center
                        loader: true,  // Whether to show loader or not. True by default
                        loaderBg: '#9EC600',  // Background color of the toast loader
                        beforeShow: function () {}, // will be triggered before the toast is shown
                        afterShown: function () {}, // will be triggered after the toat has been shown
                        beforeHide: function () {}, // will be triggered before the toast gets hidden
                        afterHidden: function () {}  // will be triggered after the toast has been hidden
                    });
                }else{
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                };
            },
            error: function (data) {
                $('#lb-msg').text('你没有增加平台业务的权限');
                $('#modal-notify').show();
            }
        });
    });

    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });

    $("#require_ip").click(function(){
        addAll(uuid);
    });

    // Click to reset all ip
    $("#reset_ip").click(function(){
        var data = {'uuid': uuid,};
        var encoded = $.toJSON(data);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/assets/reset_using_ip_pool/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function(data){
                $(".adjust").remove()
                $(".ip_field").remove()
                $("#iptypes").val('').trigger('change');
                occupied_ip = Array();
                occupied_ip_info = {};
            }
        });
        
    });



});