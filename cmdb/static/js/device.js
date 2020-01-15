// 修改之前的数据
var origin_data;

var table;
var editFlag;
//预编译模板
var tpl = $("#tpl").html();

var str = "确定删除选中的物理设备?";
var count=0;



var template = Handlebars.compile(tpl);

var $select2Belongs_to_room;
var $select2RoomCol;
var $select2ColIndex;
var $select2StartU;
var $select2EndU;


var $select2Belongs_to_brand;
var $select2Accident_status;

var $select2Belongs_to_model;
var $select2Belongs_to_iptype;
var select2Belongs_to_host_network_area;
var addSelectBelongs_to_cabinet = '';
var addSelectBelongs_to_model = '';
//var room_id;

//选择的额外的PM网络区域id
var selected_addtion_iptype;

//自动分配ip
//var esxi_ip_id;
//var sa_ip_id;
//var esxi_ip = Array();    //客户端占用的esxi_ip
//var sa_ip = Array();    // 客户端占用的sa_ip
var occupied_ip = new Array();    //客户端占用的ip列表，需要在请求服务端的ip时，将此ip作为参数

//客户端占用的ip信息，带有IP类型的id和ip
// format {'192.168.1.1': [id, vlan]}
var occupied_ip_info = {};


function preSelect2(postion,id,text){
    $(postion).html('');
    $(postion).append('<option value="' + id + '">' + text + '</option>');
    $(postion).select2('val',id,true);
};

//初始化列
function initModalSelect2RoomCol(){

    var room_id =  $("#belongs_to_room").select2('data')[0].id;

    $select2RoomCol = $('#room_col').select2( {
        ajax: {
            url: '/assets/get_room_col/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: {'room_id': room_id},
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
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2RoomCol;
    $select2RoomCol.on("select2:select", function (e){ logCol("select2:select", e); });

};

//初始化行
function initModalSelect2ColIndex(){
    var room_id =  $("#belongs_to_room").select2('data')[0].id;
    var col = $("#room_col").select2('data')[0].id;

    $select2ColIndex = $('#col_index').select2( {
        ajax: {
            url: '/assets/get_room_row/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: {'room_id': room_id,'col': col},
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
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2ColIndex;
    $select2ColIndex.on("select2:select", function (e){ logRow("select2:select", e); });
};

//初始化u位
function initModalSelect2StartU(){
    var room_id =  $("#belongs_to_room").select2('data')[0].id;
    var col = $("#room_col").select2('data')[0].id;
    var col_index = $("#col_index").select2('data')[0].id;

    $select2StartU = $("#start_u").select2( {
        ajax: {
            url: '/assets/get_col_index_u/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: {'room_id': room_id,'col': col,'col_index': col_index},
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
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
};


function logRoom(name, evt, className){
    if (name == 'select2:select' || name == 'select2:select2'){
        $("#room_col").val('0').trigger('change');
        $("#col_index").val('0').trigger('change');
        $("#start_u").val('0').trigger('change');
        $("#end_u").val('0').trigger('change');

        console.log('select room');

        initModalSelect2RoomCol();
        initModalSelect2ColIndex();
        initModalSelect2StartU();

    }
};

function logCol(name, evt, className){
    if (name == 'select2:select' || name == 'select2:select2'){
        $("#col_index").val('0').trigger('change');
        $("#start_u").val('0').trigger('change');
        $("#end_u").val('0').trigger('change');

        initModalSelect2ColIndex();
        initModalSelect2StartU();
    }
};

function logRow(name, evt, className){
    if (name == 'select2:select' || name == 'select2:select2'){
        $("#start_u").val('0').trigger('change');
        $("#end_u").val('0').trigger('change');

        initModalSelect2StartU("#start_u");
    }
};

function initModalSelect2(){
    // 初始化select2
    $select2Belongs_to_room = $('#belongs_to_room').select2( {
        ajax: {
            url: '/assets/list_room/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            /*data: function (params) {
                var selected = $('#belongs_to_room').select2('data');
                if (selected != '') {
                    params = {'data': selected[0].text}
                }else {
                  params = ''
                };
                return $.toJSON(params)
            },*/
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
    });

    $select2Belongs_to_room;
    //$select2Belongs_to_room.on("select2:open", function (e){ log("select2:open", e); });
    $select2Belongs_to_room.on("select2:select", function (e){ logRoom("select2:select", e); });

    //$select2RoomCol = $("#room_col").select2();

    // 初始化room col
    initModalSelect2RoomCol();

    //初始化col_total
    initModalSelect2ColIndex();

    initModalSelect2StartU();


    // listen events
    //$select2Belongs_to_room;
    //$select2Belongs_to_room.on("select2:open", function (e){ log("select2:open", e); });
    //$select2Belongs_to_room.on("select2:select", function (e){ log("select2:select", e); });

    $select2Belongs_to_brand = $('#belongs_to_brand').select2( {
        ajax: {
            url: '/assets/list_brand/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            /*data: function (params) {
                var selected = $('#belongs_to_room').select2('data');
                if (selected != '') {
                    params = {'data': selected[0].text}
                }else {
                  params = ''
                };
                return $.toJSON(params)
            },*/
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
    });
    $select2Belongs_to_brand;
    //$select2Belongs_to_brand.on("select2:open", function(e){ log2("select2:open", e); });
    $select2Belongs_to_brand.on("select2:select", function(e){ log2("select2:select", e); });

    //$("#device_status").select2();

    $select2Belongs_to_host_network_area = $('#addition_iptype').select2( {
        ajax: {
            url: '/assets/list_iptype/',
            dataType: 'json',
            type: 'POST',
            data: function(term, page){
                return {
                    'ip_type': 'VM',
                }
            },
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
    });

    $select2Belongs_to_host_network_area;
    $select2Belongs_to_host_network_area.on("select2:select", function(e){ logId("select2:select", e); });

    $select2Belongs_to_iptype = $("#iptypes").select2({
        ajax: {
            url: '/assets/list_iptype/',
            dataType: 'json',
            type: 'POST',
            //data: {'ip_type': 'PM','addition_id': selected_addtion_iptype},
            data: function(term, page){
                return {
                    'ip_type': 'PM',
                    'addition_id': selected_addtion_iptype
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
};

function log(name, evt, className){
    if (name == 'select2:select' || name == 'select2:select2'){
        //console.log('select event fired');
        $("#belongs_to_cabinet").next().remove("");
        $('#belongs_to_cabinet').remove();
        addSelectBelongs_to_cabinet = '';
        if ( addSelectBelongs_to_cabinet == '' ){
            addSelectBelongs_to_cabinet = '<select id="belongs_to_cabinet",style="width: 100%"><option selected="selected">选择机柜</option></select>';
            $("#show_room_cabinet").append(addSelectBelongs_to_cabinet);
        }
        
        //room_id = $("#belongs_to_room").select2('data')[0].id;
        //console.log(room_id);
        $("#belongs_to_cabinet").select2({
            ajax: {
                url: "/assets/list_cabinets/",
                dataType: 'json',
                type: 'POST',
                delay: 250,
                data: {'room_id':  $("#belongs_to_room").select2('data')[0].id},
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
            minimumResultsForSearch: Infinity,
            escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
            // minimumInputLength: 1,
            templateResult: formatRepo, // omitted for brevity, see the source of this page
            templateSelection: formatRepoSelection // omitted for brevity, see the source of this page
        });
    }else{
        if (name == 'select2:open'){
            $("#belongs_to_cabinet").next().remove("");
            $('#belongs_to_cabinet').remove();
            addSelectBelongs_to_cabinet = '';
        }
    }

};

function logId(name, evt, className){
    if (name == 'select2:select' || name == 'select2:select2'){
        selected_addtion_iptype = $("#addition_iptype").select2('data')[0].id;
    }
};

function log2(name, evt, className){
    if (name == 'select2:select' || name == 'select2:select2'){
        $("#belongs_to_model").next().remove("");
        $('#belongs_to_model').remove();
        addSelectBelongs_to_model = '';
        if ( addSelectBelongs_to_model == '' ){
            addSelectBelongs_to_model = '<select id="belongs_to_model",style="width: 100%"><option selected="selected">选择型号</option></select>';
            $("#show_brand_model").append(addSelectBelongs_to_model);
        }
        //brand_id = $("#belongs_to_brand").select2('data')[0].id;
        //console.log(room_id);
        $("#belongs_to_model").select2({
            ajax: {
                url: "/assets/list_model/",
                dataType: 'json',
                type: 'POST',
                delay: 250,
                data: {'brand_id': $("#belongs_to_brand").select2('data')[0].id},
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
            minimumResultsForSearch: Infinity,
            escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
            // minimumInputLength: 1,
            templateResult: formatRepo, // omitted for brevity, see the source of this page
            templateSelection: formatRepoSelection // omitted for brevity, see the source of this page
        });
    }else{
        if (name == 'select2:open'){
            $("#belongs_to_model").next().remove("");
            $('#belongs_to_model').remove();
            addSelectBelongs_to_model = '';
        }
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
        url: "/assets/get_resource_device/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
                origin_data = data;
                $("#myModalLabel").text("修改设备信息");
                $("#modal-notify").hide();
                //console.log(data.assgined_ip);
                //$("#show_edit_device_id").hide();
                $("#device_id").val(id);
                $("#show_device_id").hide();
                $("#maintenance_code").val(data.maintenance_code);

                // !---Add belongs_to_room and position select2
                $("#belongs_to_room").val('0').trigger('change');
                $("#room_col").val('0').trigger('change');
                $("#col_index").val('0').trigger('change');
                $("#start_u").val('0').trigger('change');


                if (data.belongs_to_room_id != '0'){
                    //$("#belongs_to_room").html('');
                    //$("#belongs_to_room").append('<option value="' + data.belongs_to_room_id + '">' + data.belongs_to_roomname + '</option>');
                    //$("#belongs_to_room").select2('val',data.belongs_to_room_id,true);
                    preSelect2("#belongs_to_room",data.belongs_to_room_id,data.belongs_to_roomname);
                    initModalSelect2RoomCol();
                }
                else{
                    //$("#belongs_to_room").val('0').trigger('change');
                    //preSelect2("belongs_to_room",'0','选择机房',selected=false);
                    //$("#belongs_to_room").html('');
                    //$("#belongs_to_room").append('<option value="0">选择机房</option>');
                    //$("#belongs_to_room").select2('val','0',true);
                    preSelect2("#belongs_to_room",'0','选择机房');
                    initModalSelect2RoomCol();
                }

                
                if (data.room_col != '0'){
                    //$("#room_col").html('');
                    //$("#room_col").append('<option value="' + data.room_col + '">' + data.room_col + '</option>');
                    //$("#room_col").select2('val',data.room_col,true);
                    initModalSelect2RoomCol();
                    preSelect2("#room_col",data.room_col,data.room_col);
                }
                else{
                    //$("#room_col").val('0').trigger('change');
                    //preSelect2("room_col",'0','列',selected=false);
                    //$("#room_col").html('');
                    //$("#room_col").append('<option value="0">列</option>');
                    //$("#room_col").select2('val','0',true);
                    preSelect2("#room_col",'0','列');
                    initModalSelect2RoomCol();
                }

                if (data.col_index!='0'){
                    //$("#col_index").html('');
                    //$("#col_index").append('<option value="' + data.col_index + '">' + data.col_index + '</option>');
                    //$("#col_index").select2('val',data.col_index,true);
                    preSelect2("#col_index",data.col_index,data.col_index);
                    initModalSelect2ColIndex();
                }
                else{
                    //$("#col_index").val('0').trigger('change');
                    //preSelect2("col_index",'0','行',selected=false);
                    //$("#col_index").html('');
                    //$("#col_index").append('<option value="0">行</option>');
                    //$("#col_index").select2('val','0',true);
                    preSelect2("#col_index",'0','行');
                    initModalSelect2ColIndex();
                }

                if (data.start_u != '0'){
                    //$("#start_u").html('');
                    //$("#start_u").append('<option value="' + data.start_u + '">' + data.start_u + '</option>');
                    //$("#start_u").select2('val',data.start_u,true);
                    preSelect2("#start_u",data.start_u,data.start_u);
                    initModalSelect2StartU();
                }
                else{
                    //$("#start_u").val('0').trigger('change');
                    //preSelect2("start_u",'0','起始u位',selected=false);
                    //$("#start_u").html('');
                    //$("#start_u").append('<option value="0">起始u位</option>');
                    //$("#start_u").select2('val','0',true);
                    preSelect2("#start_u",'0','起始u位');
                    initModalSelect2StartU();
                }


                // reinit postion select2
                //initModalSelect2RoomCol();
                //initModalSelect2ColIndex();
                //initModalSelect2StartU();
                // -- End

                // !-- Add belongs_to_brand and belongs_to_model select2
                $("#belongs_to_brand").html('');
                $("#belongs_to_brand").append('<option value="' + data.belongs_to_brand_id + '">' + data.belongs_to_brandname + '</option>')
                $("#belongs_to_brand").select2('val',data.belongs_to_brand_id,true);
                $("#belongs_to_model").next().remove("");
                $('#belongs_to_model').remove();
                var addSelectBelongs_to_model = '';
                if ( addSelectBelongs_to_model == '' ){
                    addSelectBelongs_to_model = '<select id="belongs_to_model",style="width: 100%"><option selected="selected" value="' + data.belongs_to_model_id + '">' + data.belongs_to_modelname + '</option></select>';
                    $("#show_brand_model").append(addSelectBelongs_to_model);
                    $("#belongs_to_model").select2({
                        ajax: {
                            url: "/assets/list_model/",
                            dataType: 'json',
                            type: 'POST',
                            delay: 250,
                            data: {'brand_id': $("#belongs_to_brand").select2('data')[0].id},
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
                        minimumResultsForSearch: Infinity,
                        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
                        // minimumInputLength: 1,
                        templateResult: formatRepo, // omitted for brevity, see the source of this page
                        templateSelection: formatRepoSelection // omitted for brevity, see the source of this page
                    });
                }
                // -- End

                $("#cpu").val(data.device_cpu);
                $("#mem").val(data.device_mem);
                $("#disk").val(data.device_disk);
                $("#purchase_date").val(data.purchase_date);
                $("#warranty_date").val(data.warranty_date);
                $("#device_status").val(parseInt(data.device_status));

                // !-- Add addition_iptype select2
                /*$("#addition_iptype").html('');
                $("#addition_iptype").append('<option value="' + data.iptype_id + '">' + data.iptype_name + '</option>')
                $("#addition_iptype").select2('val',data.iptype_id,true)*/
                // -- End

                // !-- Add iptypes select2, multiple select!
                $("#iptypes").val('').trigger('change');
                $(".adjust").remove();
                $(".ip_field").remove();
                $("#iptypes").html('');
                var values = Array();
                data.typename_info.forEach(function(info, i){
                    $("#iptypes").append('<option value="' + i + '">' + info + '</option>');
                    values.push(i);
                    // if (i!=0) {addBr()}
                });
                $("#iptypes").select2('val',values);
                // -- End

                // !--Add input field
                occupied_ip = Array();
                occupied_ip_info = {};
                var assgined_ip_info = $.parseJSON(data.assgined_ip);
                assgined_ip_info.forEach(function(info, n){
                    // occupied_ip_info[assgined_ip_info[n][0]] = assgined_ip_info[n][1];
                    occupied_ip_info[assgined_ip_info[n][0]] = [assgined_ip_info[n][1], assgined_ip_info[n][3]];
                    var typename = assgined_ip_info[n][2];
                    var showClass = "show_" + typename;
                    var inputClass = "text_" + typename;
                    var addStr = '<div class="form-group ip_field '+ showClass + '"><label class="col-sm-3 control-label">' + typename + '</label><div class="col-sm-7"><input type="text" class="form-control ' + inputClass + '" value="'+ assgined_ip_info[n][0] + '"></div>';
                    var selector = '.text_' + typename;
                    $("#show_remarks").before(addStr);
                    $(selector).attr('disabled', 'disabled');
                });
                // -- End
                //console.log(occupied_ip_info);

                $("#device_remarks").val(data.device_remarks);
                // Do some adjust
                $("#show_remarks").before("<br class='adjust'>");

                $("#myModal").modal("show");
        },
        error: function(data){
            alert('你没有修改基础资源权限');
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


function saveBeforeCheck(maintenance_code,belongs_to_brand,room_col,col_index,start_u_bit,belongs_to_model,cpu,mem,disk,purchase_date,warranty_date,device_status){
    if (maintenance_code == ''){
        $('#lb-msg').text('服务编号不能为空!');
        $('#modal-notify').show();
        return false;
    }

    if (belongs_to_brand == '0'){
        $('#lb-msg').text('请选择品牌!');
        $('#modal-notify').show();
        return false;
    }

    if (room_col != '0'){
        // 如果选择了行
        if (col_index == '0'){
            $('#lb-msg').text('你选择了位置,请选择柜!');
            $('#modal-notify').show();
            return false;
        }
        if (start_u_bit == '0'){
            $('#lb-msg').text('你选择了位置,请选择起始u位!');
            $('#modal-notify').show();
            return false;
        }
    }
    

    if (belongs_to_model == '0'){
        $('#lb-msg').text('请选择型号!');
        $('#modal-notify').show();
        return false;
    }
    if (cpu == ''){
        $('#lb-msg').text('请输入cpu!');
        $('#modal-notify').show();
        return false;
    }
    if (mem == ''){
        $('#lb-msg').text('请输入内存!');
        $('#modal-notify').show();
        return false;
    }
    if (disk == ''){
        $('#lb-msg').text('请输入硬盘!');
        $('#modal-notify').show();
        return false;
    }
    if (purchase_date == ''){
        $('#lb-msg').text('请输入购买日期!');
        $('#modal-notify').show();
        return false;
    }
    if (warranty_date == ''){
        $('#lb-msg').text('请输入保险时期!');
        $('#modal-notify').show();
        return false;
    }
    if (device_status == null){
        $('#lb-msg').text('请选择设备状态!');
        $('#modal-notify').show();
        return false;
    }
    return true;

};
// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });

/*function ipToint(str){
    //将ip转化为十进制的数字
    var to_array = str.split('.');
    var l = to_array.length;
    var sum = 0;
    to_array.reverse();
    for (var x=0;x<l;x++){
        num = parseInt(to_array[x]) * Math.pow(10, x);
        sum += num;
    }
    return sum;
};*/

/*function compareNumbers(a, b){
    return ipToint(a) - ipToint(b);
};*/

/*function truncateForm(form_id){
    var next = $("#"+form_id).next().attr('id');
    if ( next != undefined || next != 'show_remarks'){
        $("#"+next).remove();
        truncateForm(form_id);
    }
};*/

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
function addAll(){
    var selectedType = $("#iptypes").select2('data');
    if (selectedType.length == 0) {
        return false;
    }
    var selectedTypeName = new Array();
    // Push selected name
    $("#iptypes").select2('data').forEach(function(info, i){ selectedTypeName.push(info.text) });
    var selectedTypeNameLength = selectedTypeName.length;
    for (var i=0; i<selectedTypeNameLength; i++){
        addOne(selectedTypeName[i]);
    }
};

// Add one type of input text with button
function addOne(typename){
    var typename = typename;
    var showClass = "show_" + typename;
    var inputClass = "text_" + typename;
    var addStr = '<li class="form-group ip_field '+ showClass + '"><label class="col-sm-3 control-label">' + typename + '</label><div class="col-sm-7"><input type="text" class="form-control '+ inputClass + '" placeholder="server_alias"></div>'

    // Requeir ip from Server!
    var data = {
        'typename': typename,
        'occupied_ip': occupied_ip
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

                // ipinfo.ip.forEach(function(value, i){occupied_ip_info[value] = ipinfo.id[i]});
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

/*function addEsxi(obj){
    ++esxi_ip_id;
    var set_esxi_ip_id = "esxi_ip_" + esxi_ip_id;
    var show_esxi_ip_id = "show_esxi_ip_" + esxi_ip_id;
    var require_esxi_ip_id = "require_esxi_ip_" + esxi_ip_id;
    var delete_esxi_ip_id = "delete_esxi_ip_" + esxi_ip_id;
    var addEsxiIp = '<li class="form-group" id=' + show_esxi_ip_id + '><label class="col-sm-3 control-label">Esxi IP</label><div class="col-sm-5"><input type="text" class="form-control" placeholder="server_alias" id=' + set_esxi_ip_id + '></div><button class="btn btn-outline btn-primary btn-sm require_esxi_ip" type="button" id=' + require_esxi_ip_id + '>增加</button><button class="btn btn-outline btn-primary btn-sm btn-danger delete_esxi_ip" type="button" id=' + delete_esxi_ip_id + '>删除</button></li>';
    if ( (obj).attr('id') == 'acquire' ){
        $("#acquire_ip").after(addEsxiIp);
    }
    else{
        var parenNodeSelector = "#" + obj.parent().attr('id');
        $(parenNodeSelector).after(addEsxiIp);
    }
    // Get ip
    var data = {
        'typename': 'PM-带外网管',
        'occupied_ip': esxi_ip,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/gen_ip/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            if ( data['success'] ){
                //console.log(JSON.parse(data['data']).length);
                var ipinfo;
                ipinfo = JSON.parse(data['data']);
                var set_esxi_ip_id_selector = "#" + set_esxi_ip_id;
                $(set_esxi_ip_id_selector).val(ipinfo.ip).attr('disabled', 'disabled');
                esxi_ip.push(ipinfo);
                //console.log('now',esxi_ip)
            }
        }
    });

    // Add event
    var requireSelector = "#" + require_esxi_ip_id;
    $(requireSelector).click(function(){
        addEsxi($(this));
    });

    var deleteSelector = "#" + delete_esxi_ip_id;
    $(deleteSelector).click(function(){
        var parenNodeSelector = "#" + $(this).parent().attr('id');
        var id = delete_esxi_ip_id.split('_').pop();
        var set_esxi_ip_id = "esxi_ip_" + id;
        var ip_selector = "#" + set_esxi_ip_id;
        var remove_ip = $(ip_selector).val();
        var index;
        esxi_ip.forEach(function(info,i){ if (info.ip==remove_ip){index=i} });
        esxi_ip.splice(index, 1);
        $(parenNodeSelector).remove();
    });
};*/

/*function addSa(obj){
    ++sa_ip_id;
    var set_sa_ip_id = "sa_ip_" + sa_ip_id;
    var show_sa_ip_id = "show_sa_ip_" + sa_ip_id;
    var require_sa_ip_id = "require_sa_ip_" + sa_ip_id;
    var delete_sa_ip_id = "delete_sa_ip_" + sa_ip_id;
    var addSaIp = '<li class="form-group" id=' + show_sa_ip_id + '><label class="col-sm-3 control-label">外带网管IP</label><div class="col-sm-5"><input type="text" class="form-control" placeholder="server_alias" id=' + set_sa_ip_id + '></div><button class="btn btn-outline btn-primary btn-sm require_sa_ip" type="button" id=' + require_sa_ip_id + '>增加</button><button class="btn btn-outline btn-primary btn-sm btn-danger delete_sa_ip" type="button" id=' + delete_sa_ip_id + '>删除</button></li>'
    if ( (obj).attr('id') == 'acquire' ){
        $("#acquire_ip").after(addSaIp);
    }
    else{
        var parenNodeSelector = "#" + obj.parent().attr('id');
        $(parenNodeSelector).after(addSaIp);
    }

    // Get ip
    var data = {
        'typename': 'PM-esxi',
        'occupied_ip': sa_ip,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/gen_ip/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            if ( data['success'] ){
                //console.log(JSON.parse(data['data']).length);
                var ipinfo;
                ipinfo = JSON.parse(data['data']);
                var set_sa_ip_id_selector = "#" + set_sa_ip_id;
                $(set_sa_ip_id_selector).val(ipinfo.ip).attr('disabled', 'disabled');
                sa_ip.push(ipinfo);
            }
        }
    });

    // Add event
    var requireSelector = "#" + require_sa_ip_id;
    $(requireSelector).click(function(){
        addSa($(this));
    });

    var delEsxiSelector = "#" + delete_sa_ip_id;
    $(delEsxiSelector).click(function(){
        var parenNodeSelector = "#" + $(this).parent().attr('id');
        // according delete id get input text id
        var id = delete_sa_ip_id.split('_').pop();
        var set_sa_ip_id = "sa_ip_" + id;
        var ip_selector = "#" + set_sa_ip_id;
        var remove_ip = $(ip_selector).val();
        var index;
        esxi_ip.forEach(function(info,i){ if (info.ip==remove_ip){index=i} });
        sa_ip.splice(index, 1);
        $(parenNodeSelector).remove();
    });
};*/

$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        //"scrollX": true,
        "ajax": "/assets/data_device",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": 'maintenance_code'},
            {"data": "belongs_to_room"},
            {"data": "position"},
            {"data": "belongs_to_model"},
            {"data": "device_cpu"},
            {"data": "device_mem"},
            {"data": "device_disk"},
            {"data": "purchase_date"},
            {"data": "warranty_date"},
            {"data": "device_status"},
            {"data": "device_remarks"},
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
                    targets: 13,
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

    $('a.toggle-vis').on( 'click', function (e) {
        e.preventDefault();
 
        // Get the column API object
        var column = table.column( $(this).attr('data-column') );
 
        // Toggle the visibility
        column.visible( ! column.visible() );

        // Change the is_display content
        if (column.visible()){
            $(this)[0].children[0].textContent = '隐藏';
        }else{
            $(this)[0].children[0].textContent = '显示';
        }
    } );

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

    $('#purchase_date').Zebra_DatePicker({
    });
    $('#warranty_date').Zebra_DatePicker({
    });
    initModalSelect2();
    

    // 多选
    // $('#mytable tbody').on( 'click', 'tr', function () {
    //     $(this).toggleClass('selected');
    // } );

    //删除
    $("#bt-del").confirm({
        //text:"确定删除所选的物理设备?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_device/",
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

    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增设备信息");
        $("#modal-notify").hide();
        $("#show_device_id").hide();
        $("#maintenance_code").val('').removeAttr("disabled");

        //$("#belongs_to_room").val('0').trigger('change');
        //$("#room_col").val('0').trigger('change');
        //$("#col_index").val('0').trigger('change');
        //$("#start_u").val('0').trigger('change');
        preSelect2("#belongs_to_brand",'0','选择品牌',selected=true);

        preSelect2("#belongs_to_room",'0','选择机房',selected=true);

        preSelect2("#room_col",'0','列',selected=true);
        initModalSelect2RoomCol();

        preSelect2("#col_index",'0','柜',selected=true);
        initModalSelect2ColIndex();
        preSelect2("#start_u",'0','起始u位',selected=true);
        initModalSelect2StartU();


        //$("#belongs_to_brand").val('0').trigger('change');
        $("#belongs_to_model").next().remove();
        $("#belongs_to_model").remove();
        $("#cpu").val('');
        $("#mem").val('');
        $("#disk").val('');
        $("#purchase_date").val('');
        $("#warranty_date").val('');
        $("#device_status").val('');
        $("#addition_iptype").val('0').trigger('change');
        $("#iptypes").val('').trigger('change');
        $(".adjust").remove()
        $(".ip_field").remove()
        $("#device_remarks").val('');
        editFlag=false;
        //esxi_ip_id = 0;
        //sa_ip_id = 0;
        //esxi_ip = Array();
        //sa_ip = Array();
        occupied_ip = Array();
        occupied_ip_info = {};
        selected_addtion_iptype = '';
        //truncateForm('show_ip_type');
        $("#myModal").modal("show");
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
        // var inputIds=$('#modal-list div input').map(function(i,n){
        //     return $(n).val();
        // }).get();
        var id = $("#device_id").val();
        var maintenance_code = $("#maintenance_code").val();

        var belongs_to_room = $("#belongs_to_room").select2('data')[0].id;

        var room_col = $("#room_col").select2('data')[0].id;
        var col_index = $("#col_index").select2('data')[0].id;
        var start_u_bit = $("#start_u").select2('data')[0].id;

        var belongs_to_brand = $("#belongs_to_brand").select2('data')[0].id;
        var belongs_to_model = $("#belongs_to_model").select2('data')[0].id;
        var cpu = $("#cpu").val();
        var mem = $("#mem").val();
        var disk = $("#disk").val();
        var purchase_date = $("#purchase_date").val();
        var warranty_date = $("#warranty_date").val();
        var device_status = $("#device_status").val();
        var device_remarks = $("#device_remarks").val();

        if (!saveBeforeCheck(maintenance_code,belongs_to_brand,room_col,col_index,start_u_bit,belongs_to_model,cpu,mem,disk,purchase_date,warranty_date,device_status)){
            return false;
        }

        var inputIds = {
            'id': id,
            'maintenance_code': maintenance_code,
            'belongs_to_room': belongs_to_room,
            'room_col': room_col,
            'col_index': col_index,
            'start_u_bit': start_u_bit,
            'belongs_to_brand': belongs_to_brand,
            'belongs_to_model': belongs_to_model,
            'device_cpu': cpu,
            'device_mem': mem,
            'device_disk': disk,
            'purchase_date': purchase_date,
            'warranty_date': warranty_date,
            'device_status': device_status,
            'device_remarks': device_remarks,
            'occupied_ip_info': occupied_ip_info,
            "origin_data": origin_data,
        };
        
        if (editFlag){
            var urls="/assets/edit_data_device/";
        }else{
            var urls="/assets/add_data_device/";
        }
        
        console.log(occupied_ip_info);
        //return false;
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
    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });

    // Click to acquire all ip
    $("#require_ip").click(function(){
        addAll();
    });

    // Click to reset all ip
    $("#reset_ip").click(function(){
        $(".adjust").remove()
        $(".ip_field").remove()
        // $("#iptypes").val('').trigger('change');
        initSelect2("iptypes", '0', '选择网络区域');
        occupied_ip = Array();
        occupied_ip_info = {};
    });

    $("#reset_position").click(function(){
        preSelect2("#belongs_to_room",'0','选择机房');

        preSelect2("#room_col",'0','列');
        initModalSelect2RoomCol();

        preSelect2("#col_index",'0','行');
        initModalSelect2ColIndex();
        
        preSelect2("#start_u",'0','起始u位');
        initModalSelect2StartU();



    });


} );
