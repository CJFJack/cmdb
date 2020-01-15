// 修改之前的数据
var origin_data;

var table;
var editFlag;
var deviceFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的主机?";
var count=0;

var $select2Belongs_to_host_type;
var $select2Belongs_to_platform;
var $select2Belongs_to_device;
var $select2Belongs_to_ostype;
var $iptypes;

var uuid;

/*-------------自动生成主机名需要的变量----------------*/
// 这个变量用来做下拉网络区域的条件筛选
// 刚开始这个值位空的，如果选择了一个网络区域以后
// 会给这个变量赋值，下次选择网络区域的时候会筛选这个字段
// 如果重置了,这个变量为空
// u:UAT, s:SIT, p:PRD, o:运维, d:灾备
// 根据选择的网络区域
var network_zone;

// 公司名 a:网金, b:钱端, c:钱途, d:大数据
// 根据选择的平台
var company;

// 机房序列号 0:亚太, 1:化龙
// 根据选择的网络区域关联到机房
var roomid;

// 业务类型 W:WEB, A:APP, S:SER, C:CACHE, M:MAG, G:MSG, D:DB, J:JUMP
// 根据选择的操作系统类型
var business_type;

// 操作系统类型 Linux 或者 windows 取他们的第一个字母的大写
var os_type;
/*-------------自动生成主机名需要的变量----------------*/

var occupied_ip = new Array();    //客户端占用的ip列表，需要在请求服务端的ip时，将此ip作为参数

//客户端占用的ip信息，带有IP类型的id和ip
// format {'192.168.1.1': [id, vlan]}
var occupied_ip_info = {};


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
        addOne(selectedTypeName[i], uuid);
    }
};

// Add one type of input text with button
function addOne(typename, uuid){
    var platform_id = $("#belongs_to_PlatForm").select2('data')[0].id;
    if (platform_id == '0'){
        $('#lb-msg').text('要分配ip,请选择平台!');
        $('#modal-notify').show();
        return false;
    }
    var typename = typename;
    var showClass = "show_" + typename;
    var inputClass = "text_" + typename;
    var addStr = '<li class="form-group ip_field '+ showClass + '"><label class="col-lg-3 col-sm-3 control-label">' + typename + '</label><div class="col-lg-6"><input type="text" class="form-control ip_input_fields '+ inputClass + '" placeholder="server_alias"></div>'

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
                    $("#show_remarks").before(addStr);
                    $("#show_remarks").before(addStr);
                }else{
                    $("#show_remarks").before(addStr);
                }
                //console.log(JSON.parse(data['data']).length);
                var ipinfo;
                ipinfo = JSON.parse(data['data']);
                //console.log(ipinfo);

                // Find out the input element by typename
                // var selector = ".text_" + typename;
                var selector = "text_" + typename;
                var all_typename = $(document.getElementsByClassName(selector));
                console.log(ipinfo);

                // Since we just want the empty inputs
                var i = all_typename.length;
                while (i--) {
                    if (all_typename[i].value != '' ) {
                        all_typename.splice(i, 1);
                    }
                }
                console.log('当前占用IP',occupied_ip);
                // Let's add ipinfo to the inputs and also push to the occupied_ip
                all_typename.toArray().forEach(function(info, i){ info.value = ipinfo.ip[i]; });
                ipinfo.ip.forEach(function(info, i){ occupied_ip.push(info) });
                // Disabled the input
                // $(selector).attr('disabled', 'disabled');

                ipinfo.ip.forEach(function(value, i){occupied_ip_info[value] = [ipinfo.id[i], ipinfo.vlan[i]]});
                //console.log('after add',occupied_ip_info);

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

function initModalSelect2(){
    // 初始化select2
    $select2Belongs_to_host_type = $("#belongs_to_host_type").select2({
        /*data: [
            {'id': 0, 'text':'虚拟机'},
            {'id': 1, 'text':'物理机'},
        ],*/
        placeholder: '选择属性',
        minimumResultsForSearch: Infinity,
    });
    // listen event
    $select2Belongs_to_host_type;
    $select2Belongs_to_host_type.on("select2:select", function (e){ log2("select2:select", e); });
    $select2Belongs_to_host_type.on("select2:open", function (e){ log2("select2:open", e); });

    $select2Belongs_to_platform = $('#belongs_to_PlatForm').select2( {
        ajax: {
            url: '/assets/list_platform/',
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
                            company: item.company,
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
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    $select2Belongs_to_platform;
    $select2Belongs_to_platform.on("select2:select", function (e){ log4("select2:select", e); });

    $iptypes = $("#iptypes").select2({
        ajax: {
            url: '/assets/list_iptype/',
            dataType: 'json',
            type: 'POST',
            //data: {'ip_type': 'PM','addition_id': selected_addtion_iptype},
            data: function(params){
                return {
                    'ip_type': 'VM',
                    'network_zone': network_zone,
                    q: params.term,
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
                            network_zone: item.network_zone,
                            roomid: item.roomid,
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
        //minimumResultsForSearch: Infinity,
        //escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        //templateResult: formatRepo, // omitted for brevity, see the source of this page
        //templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    $iptypes;
    $iptypes.on("select2:select", function (e){ log3("select2:select", e); });

    $select2Belongs_to_ostype = $('#belongs_to_ostype').select2( {
        ajax: {
            url: '/assets/list_ostype/',
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
                            business_type: item.business_type,
                            os_type: item.os_type,
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

    //add listen event for select2Belongs_to_ostype
    $select2Belongs_to_ostype;
    $select2Belongs_to_ostype.on("select2:select", function (e){ log("select2:select", e); });
    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};

function log(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        var ostype = $('#belongs_to_ostype').select2('data')[0].id;
        business_type = $('#belongs_to_ostype').select2('data')[0].business_type;
        $.ajax({
            type: "POST",
            url: '/assets/get_ostype_detail/',
            dataType: "json",
            data: $.toJSON({'ostype_id': ostype}),
            success: function(data){
                $("#host_cpu").val(data[0].template_cpu);
                $("#host_mem").val(data[0].template_mem);
                $("#host_disk").val(data[0].template_disk);
            },
        });
    }
};

function log2(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        var host_type = $("#belongs_to_host_type").select2('data')[0].text;
        //$("#belongs_to_host_type").next().remove("");
        //$('#belongs_to_host_type').remove();
        var addSelection = '';
        if (host_type == "物理机" && !addSelection){
            addSelection = '<select id="belongs_to_device"><option selected="selected" value="0">选择物理服务编号</option></select>';
            $("#show_belongs_to_device").append(addSelection);
            $select2Belongs_to_device = $('#belongs_to_device').select2( {
                ajax: {
                    url: '/assets/list_device/',
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
                dropdownAutoWidth: true,
            });
            deviceFlag = true;
        }
        if (host_type == '虚拟机'){
            $("#belongs_to_device").next().remove();
            $('#belongs_to_device').remove();
            addSelection = '';
            deviceFlag = false;
        }
        
    }
};

function log3(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        network_zone = $("#iptypes").select2('data')[0].network_zone;
        roomid = $("#iptypes").select2('data')[0].roomid;
    }
};

function log4(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        company = $("#belongs_to_PlatForm").select2('data')[0].company;
    }
};

function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    // 重新生成uuid
    uuid = generateUUID();
    // 隐藏继续添加按钮
    $("#bt-contiune-save").hide();
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_resource_host/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改设备信息");
            $("#modal-notify").hide();
            $("#host_id").val(id);
            $("#show_host_id").hide();

            // Fill data
            //console.log(data.belongs_to_host_type);
            $("#belongs_to_host_type").val(data.belongs_to_host_type);

            // !-- Add select2 belongs_to_device 
            var host_type = $("#belongs_to_host_type").select2('data')[0].text;
            console.log(host_type);
            var addSelection = '';
            if (host_type == "物理机" && !addSelection){
                $("#belongs_to_device").next().remove();
                $('#belongs_to_device').remove();
                var addSelection = '<select id="belongs_to_device" style="width: 50%"><option selected="selected" value="0">选择物理服务编号</option></select>';
                $("#show_belongs_to_device").append(addSelection);
                
                $select2Belongs_to_device = $('#belongs_to_device').select2( {
                    ajax: {
                        url: '/assets/list_device/',
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
                    dropdownAutoWidth: true,
                });

                $("#belongs_to_device").html('');
                $("#belongs_to_device").append('<option value="' + data.belongs_to_device_id + '">' + data.belongs_to_device + '</option>');
                $("#belongs_to_device").select2('val',data.belongs_to_device_id,true);
                deviceFlag = true;
            }
            if (host_type == '虚拟机'){
                $("#belongs_to_device").next().remove();
                $('#belongs_to_device').remove();
                $("#belongs_to_host_type").val(data.belongs_to_host_type).trigger('change');
                var addSelection = '';
                deviceFlag = false;
            }
            // -- End

            $("#hostname").val(data.hostname);

            $("#belongs_to_PlatForm").html('');
            $("#belongs_to_PlatForm").append('<option value="' + data.belongs_to_PlatForm_id + '">' + data.belongs_to_PlatForm + '</option>');
            $("#belongs_to_PlatForm").select2('val',data.belongs_to_PlatForm_id,true);

            $("#belongs_to_ostype").html('');
            $("#belongs_to_ostype").append('<option value="' + data.belongs_to_ostype_id + '">' + data.belongs_to_ostype + '</option>');
            $("#belongs_to_ostype").select2('val',data.belongs_to_ostype_id,true);

            $("#host_cpu").val(data.host_cpu);
            $("#host_mem").val(data.host_mem);
            $("#host_disk").val(data.host_disk);

            $("#vcenter").val(data.vcenter);

            $("#host_status").val(data.host_status);

            $("#iptypes").html('');
            $("#iptypes").append('<option value="0">选择网络区域</option>');
            $("#iptypes").select2('val',0);

            $("#host_remarks").val(data.host_remarks);

            // !--Add input field
            $(".ip_field").remove();
            occupied_ip = Array();
            occupied_ip_info = {};
            var assgined_ip_info = $.parseJSON(data.assgined_ip);
            // console.log(assgined_ip_info);    [["10.1.20.8", 813, "测试（SIT+压力测试）-亚太", "1500"]]
            assgined_ip_info.forEach(function(info, n){
                occupied_ip_info[assgined_ip_info[n][0]] = [assgined_ip_info[n][1], assgined_ip_info[n][3]];
                var typename = assgined_ip_info[n][2];
                var showClass = "show_" + typename;
                var inputClass = "text_" + typename;
                var addStr = '<div class="form-group ip_field '+ showClass + '"><label class="col-sm-3 control-label">' + typename + '</label><div class="col-sm-8"><input type="text" class="form-control ' + inputClass + '" value="'+ assgined_ip_info[n][0] + '"></div>';
                var selector = '.text_' + typename;
                $("#show_remarks").before(addStr);
                var ip_input = $($("#show_remarks").prev().children().get(1)).children();
                inputOnChange(ip_input);
                // $(selector).attr('disabled', 'disabled');
            });
            // -- End

            $("#myModal").modal("show");
        },
        error: function(data){
            alert('你没有修改基础资源权限');
        }
    });

};

function checkBeforeAdd(hostname,belongs_to_device,belongs_to_PlatForm,belongs_to_ostype,host_cpu,host_mem,host_disk,iptypes,host_status){
    if (hostname == ''){
        $('#lb-msg').text('主机名不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (!editFlag){
        if (deviceFlag){
            if (belongs_to_device == '0'){
                $('#lb-msg').text('请输入物理编号!');
                $('#modal-notify').show();
                return false;
            }
        }
    }

    if (belongs_to_PlatForm == '0'){
        $('#lb-msg').text('所属平台名不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (iptypes == '0') {
        $('#lb-msg').text('请选择网络区域!');
        $('#modal-notify').show();
        return false;
    }
    if (belongs_to_ostype == '0'){
        $('#lb-msg').text('请选择操作系统模版!');
        $('#modal-notify').show();
        return false;
    }
    if (host_cpu == ''){
        $('#lb-msg').text('请输入cpu型号!');
        $('#modal-notify').show();
        return false;
    }
    if (host_mem == ''){
        $('#lb-msg').text('请输入内存型号!');
        $('#modal-notify').show();
        return false;
    }
    if (host_disk == ''){
        $('#lb-msg').text('请输入硬盘信息!');
        $('#modal-notify').show();
        return false;
    }
    if (host_status == null){
        $('#lb-msg').text('请选择主机状态!');
        $('#modal-notify').show();
        return false;  
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
        "ajax": "/assets/data_host",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": 'hostname'},
            {"data": 'belongs_to_PlatForm'},
            // {"data": "network_area"},
            {"data": "belongs_to_device"},
            {"data": "host_cpu"},
            {"data": "host_mem"},
            {"data": "host_disk"},
            {"data": "belongs_to_ostype"},
            {"data": "vcenter"},
            {"data": "host_status"},
            {"data": "host_remarks"},
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

    // Handle click on table cells
    // $('#mytable tbody').on('click', 'td', function(e){
    //     $(this).parent().find('input[type="checkbox"]').trigger('click');
    // });

    // 设置权限
    is_superuser = $("#is_superuser").data('is-superuser');

    if (!is_superuser) {
        table.column(12).visible(false);
    }

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

    initModalSelect2();
    //$resourceType.on("select2:select", function (e) { autofill("select2:select", e); });
    //show or hide column
    /*$('input.global_filter').on( 'keyup click', function () {
        filterGlobal();
    } );*/

    /*$('input.column_filter').on( 'keyup click', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );*/
    /*$('select.column_filter').on('change', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );*/
    /*$('#filter_start').Zebra_DatePicker({
        // pair: $('#filter_end'),
    });*/
    /*$('#filter_end').Zebra_DatePicker({
        // direction: 1,
    });*/


    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增主机信息");
        $("#modal-notify").hide();
        $("#show_host_id").hide();
        $("#belongs_to_host_type").val('0').trigger('change');
        $("#belongs_to_device").next().remove();
        $("#belongs_to_device").remove();
        $("#hostname").val('');
        // $("#hostname").val('').removeAttr("disabled");
        // $("#belongs_to_PlatForm").val('0').trigger('change');
        $("#belongs_to_PlatForm").html('');
        $("#belongs_to_PlatForm").append('<option value="0">选择平台</option>');
        $("#belongs_to_PlatForm").select2('val','0',true);

        $("#iptypes").val('0').trigger('change');
        $("#belongs_to_device").val('0').trigger('change');
        $("#host_cpu").val('');
        $("#host_mem").val('');
        $("#host_disk").val('');
        //$("#belongs_to_ostype").val('0').trigger("change");
        $("#belongs_to_ostype").html('');
        $("#belongs_to_ostype").append('<option value="0">选择系统模版</option>');
        $("#belongs_to_ostype").select2('val','0',true);
        $("#vcenter").val('');
        // $("#host_status").val('');
        $("#iptypes").val('0').trigger('change');
        $("#host_remarks").val('');
        $(".ip_field").remove();
        editFlag=false;
        $("#myModal").modal("show");

        $("#bt-contiune-save").show();

        // 生成全局的uuid
        uuid = generateUUID();

        occupied_ip = Array();
        occupied_ip_info = {};
    } );
    $('#file-save').click( function () {
        $("#Modal-file").modal("hide");
    } );

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
        var host_id = $("#host_id").val();
        var hostname = $("#hostname").val();
        var belongs_to_device = '';
        if ($('#belongs_to_host_type').select2('data').length == 0){
            $('#lb-msg').text('请选择属性!');
            $('#modal-notify').show();
            return false;
        }
        if (deviceFlag){
            belongs_to_device = $("#belongs_to_device").select2('data')[0].id;
        }
        var belongs_to_PlatForm = $("#belongs_to_PlatForm").select2('data')[0].id;

        // 去掉网络区域
        /*if ( $("#iptypes").select2('data')[0].id == '0' ){
            $('#lb-msg').text('请选择网络区域!');
            $('#modal-notify').show();
            return false;
        }else{
            var iptypes = $("#iptypes").select2('data')[0].text;
        }*/

        var belongs_to_ostype = $("#belongs_to_ostype").select2('data')[0].id;
        var host_cpu = $("#host_cpu").val();
        var host_mem = $("#host_mem").val();
        var host_disk = $("#host_disk").val();
        var vcenter = $("#vcenter").val();
        var host_status = $("#host_status").val();
        var host_remarks = $("#host_remarks").val();

        if (editFlag){
            var urls = "/assets/edit_data_host/";
        }else{
            var urls = "/assets/add_data_host/";
        }

        var inputIds = {
                'host_id': host_id,
                'hostname': hostname,
                'belongs_to_PlatForm': belongs_to_PlatForm,
                // 'host_network_area': iptypes,
                'belongs_to_device': belongs_to_device,
                'belongs_to_ostype': belongs_to_ostype,
                'host_cpu':host_cpu,
                'host_mem': host_mem,
                'host_disk': host_disk,
                'vcenter':vcenter,
                'host_status': host_status,
                'host_remarks': host_remarks,
                'occupied_ip_info': occupied_ip_info,
                "origin_data": origin_data,
                'uuid': uuid,
            };
        
        if ( !checkBeforeAdd(hostname,belongs_to_device,belongs_to_PlatForm,belongs_to_ostype,host_cpu,host_mem,host_disk,iptypes,host_status) ){
            return false;
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
                $('#lb-msg').text('你没有增加基础资源权限');
                $('#modal-notify').show();
            }
        });
    });

    $('#bt-contiune-save').click( function(){
        var host_id = $("#host_id").val();
        var hostname = $("#hostname").val();
        var belongs_to_device = '';
        if ($('#belongs_to_host_type').select2('data').length == 0){
            $('#lb-msg').text('请选择属性!');
            $('#modal-notify').show();
            return false;
        }
        if (deviceFlag){
            belongs_to_device = $("#belongs_to_device").select2('data')[0].id;
        }
        var belongs_to_PlatForm = $("#belongs_to_PlatForm").select2('data')[0].id;

        // 去掉网络区域
        /*if ( $("#iptypes").select2('data')[0].id == '0' ){
            $('#lb-msg').text('请选择网络区域!');
            $('#modal-notify').show();
            return false;
        }else{
            var iptypes = $("#iptypes").select2('data')[0].text;
        }*/

        var belongs_to_ostype = $("#belongs_to_ostype").select2('data')[0].id;
        var host_cpu = $("#host_cpu").val();
        var host_mem = $("#host_mem").val();
        var host_disk = $("#host_disk").val();
        var vcenter = $("#vcenter").val();
        var host_status = $("#host_status").val();
        var host_remarks = $("#host_remarks").val();

        var urls = "/assets/add_data_host/";

        var inputIds = {
                'host_id': host_id,
                'hostname': hostname,
                'belongs_to_PlatForm': belongs_to_PlatForm,
                // 'host_network_area': iptypes,
                'belongs_to_device': belongs_to_device,
                'belongs_to_ostype': belongs_to_ostype,
                'host_cpu':host_cpu,
                'host_mem': host_mem,
                'host_disk': host_disk,
                'vcenter':vcenter,
                'host_status': host_status,
                'host_remarks': host_remarks,
                'occupied_ip_info': occupied_ip_info,
                "origin_data": origin_data,
                'uuid': uuid,
            };
        
        if ( !checkBeforeAdd(hostname,belongs_to_device,belongs_to_PlatForm,belongs_to_ostype,host_cpu,host_mem,host_disk,iptypes,host_status) ){
            return false;
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
                    // $("#myModal").modal("hide");

                    // 重新初始化全局参数
                    uuid = generateUUID();
                    occupied_ip = Array();
                    occupied_ip_info = {};

                    editFlag=false;

                    $("#vcenter").val('');
                    $("#hostname").val('');
                    $("#host_remarks").val('');
                    $(".adjust").remove();
                    $(".ip_field").remove();
                    $.toast({
                        text: "成功添加一条主机", // Text that is to be shown in the toast
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
                $('#lb-msg').text('你没有增加基础资源权限');
                $('#modal-notify').show();
            }
        });
    });


    $("#bt-del").confirm({
        //text:"确定删除所选的主机?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_host/",
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

    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });

    // Click to acquire all ip
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
                $(".adjust").remove();
                $(".ip_field").remove();
                network_zone = '';
                // $("#iptypes").val('0').trigger('change');
                initSelect2("iptypes", '0', '选择网络区域');
                occupied_ip = Array();
                occupied_ip_info = {};
            }
        });
        
    });

    // 自动生成主机名
    $("#auto").click(function(event) {
        /* Act on the event */
        /* console.log(network_zone);
        console.log(company);
        console.log(roomid);
        console.log(business_type); */
        // 这里暂时不使用全局的变量，使用局部的变量
        var network_zone = $("#iptypes").select2('data')[0].network_zone;
        var company = $("#belongs_to_PlatForm").select2('data')[0].company;
        var roomid = $("#iptypes").select2('data')[0].roomid;
        var business_type = $('#belongs_to_ostype').select2('data')[0].business_type;
        var os_type = $('#belongs_to_ostype').select2('data')[0].os_type;
        var vcenter_name = $('#belongs_to_PlatForm').select2('data')[0].text
        if (typeof network_zone=='undefined' || typeof company=='undefined' || typeof roomid=='undefined' || typeof business_type=='undefined' || typeof os_type=='undefined'){
            // console.log('bad');
            return false;
        }else{
            // console.log('ok');
            var data = {
                'platform_type': network_zone,
                'company': company,
                'roomid': roomid,
                'business_type': business_type,
                'os_type': os_type
            };
            var encoded = $.toJSON(data);
            var pdata = encoded;
            $.ajax({
                type: "POST",
                url: "/assets/auto_hostname/",
                data: pdata,
                contentType: "application/json; charset=utf-8",
                success: function(data){
                    // console.log(data);
                    console.log(data);
                    $("#hostname").val(data.hostname);
                    $("#vcenter").val(vcenter_name + '-' + data.hostname);
                }
            });
        }

    });

    // 给ip_input 添加绑定事假
    $('#vcenter').on('focusin', function(){
        console.log("Saving value " + $(this).val());
        $(this).data('val', $(this).val());
    });
    $("#vcenter").on("change paste", function() {
        var prev = $(this).data('val');
        var current = $(this).val();
        console.log("Prev value " + prev);
        console.log("New value " + current);
    });


    // test
    /*$("#bt-test").click( function(event){
        $.toast({
            text: "成功添加一条主机", // Text that is to be shown in the toast
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
    });*/



} );
