//Make sure jQuery has been loaded before network_policy.js
if (typeof jQuery === "undefined") {
  throw new Error("This JS requires jQuery");
}


var table;
var editFlag;
//预编译模板
var tpl = $("#tpl").html();

var str = "确定删除选中的策略?";
var count=0;

var template = Handlebars.compile(tpl);
// var $selectBelong_project;
// var $select2Belong_mechine_room;
// var $select2Belong_idc;
// var $select2Belong_cabinets;
// var $select2Accident_status;
// //var $resourceType;
// var $select2NetIP;
// var $col4_filter;
// var $col5_filter;
// var $col8_filter;
// var $col9_filter;
// var $col10_filter;
// var $col11_filter;
var $select2Belongs_src_platform;
var $select2Belongs_dst_platform;
var $select2Belongs_src_host;
var $select2Belongs_dst_host;
var $select2Belongs_src_host_ip;
var $select2Belongs_dst_host_ip;



function initModalSelect2(){
    // 初始化select2
    $("#belongs_src_platform").select2();
    $("#belongs_src_host").select2();
    $("#src_host_ip").select2();
    $("#belongs_dst_platform").select2();
    $("#belongs_dst_host").select2();
    $("#dst_host_ip").select2();
    $("#policy_protocol").select2({minimumResultsForSearch: Infinity});
    $("#state").select2({minimumResultsForSearch: Infinity});

    
    $select2Belongs_src_platform = $("#belongs_src_platform").select2({
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
        }
    }).on('change', function () {
        $("#belongs_src_host").html('');
        $select2Belongs_src_host = $("#belongs_src_host").select2({
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
                        platform: $select2Belongs_src_platform.val(),
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
            $("#src_host_ip").html('');
            $select2Belongs_src_host_ip = $("#src_host_ip").select2({
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
                            host: $select2Belongs_src_host.val(),
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

    $select2Belongs_dst_platform = $("#belongs_dst_platform").select2({
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
        $("#belongs_dst_host").html('');
        $select2Belongs_dst_host = $("#belongs_dst_host").select2({
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
                        platform: $select2Belongs_dst_platform.val(),
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
            $("#dst_host_ip").html('');
            $select2Belongs_dst_host_ip = $("#dst_host_ip").select2({
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
                            host: $select2Belongs_dst_host.val(),
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
};

$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ajax": "/assets/data_network_policy/",
        "columns": [
            {"data": null},
            {"data": 'policy_id'},
            {"data": "policy_name"},
            {"data": 'src_platform'},
            {"data": 'src_host'},
            {"data": 'src_ip'},
            {"data": 'dst_platform'},
            {"data": 'dst_host'},
            {"data": 'dst_ip'},
            {"data": 'policy_protocol'},
            {"data": 'port'},
            {"data": 'start_date'},
            {"data": 'end_date'},
            {"data": 'state'},
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
                    targets: 14,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.policy_id + "\')", "type": "primary"},
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

    $('#chb-all').on('click', function(e){
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function(i,n){
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked){
              $row.addClass('selected');
              count = getSelectedTable('policy_id').length;
              makeTitle(str, count);
            }else{
              $row.removeClass('selected');
              count = 0;
              makeTitle(str, count);
            }
        });
    });

    $('#start_date').Zebra_DatePicker({
        direction: true,
    });
    $('#end_date').Zebra_DatePicker({
        direction: true,
    });

    initModalSelect2();
    //$resourceType.on("select2:select", function (e) { autofill("select2:select", e); });
    //show or hide column
    $('a.abc').on( 'click', function (e) {

        if ($(this).find('input').attr('checked')){
            $(this).find('input').attr('checked',false);
        }
        else{
            $(this).find('input').attr('checked',true);
        };
        // e.preventDefault();
        // Get the column API object
        var column = table.column( $(this).attr('data-column') );
        // Toggle the visibility
        column.visible( ! column.visible() );
    } );
    $('input.global_filter').on( 'keyup click', function () {
        filterGlobal();
    } );

    $('input.column_filter').on( 'keyup click', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );
    $('select.column_filter').on('change', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );
    $('#filter_start').Zebra_DatePicker({
        // pair: $('#filter_end'),
    });
    $('#filter_end').Zebra_DatePicker({
        // direction: 1,
    });
    $('#filter_start,#filter_end').focusout(function () {
        var start_time = Date.parse($("#filter_start").val());
        var end_time = Date.parse($("#filter_end").val());
        console.log("start_time:"+start_time+';'+'end_time:'+end_time);
        if ( !isNaN( start_time ) && !isNaN( end_time ))
        {
            if (end_time < start_time){
                alert('结束时间要大于开始时间!');
                return false;
            }
        };
        table.ajax.reload();
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


    // 多选
    // $('#mytable tbody').on( 'click', 'tr', function () {
    //     $(this).toggleClass('selected');
    // } );
//删除
    $("#bt-del").confirm({
        //text:"确定删除所选的机房?",
        confirm: function(button){
            var selected = getSelectedTable('policy_id');

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_network_policy/",
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
        $("#myModalLabel").text("新增网络策略");
        $("#modal-notify").hide();
        $("#show_state").hide()
        $("#show_network_policy_id").hide();
        $("#policy_name").val('');
        $("#belongs_src_platform").val('').trigger('change');
        $("#belongs_src_host").val('').trigger('change');
        $("#src_host_ip").val('');
        $("#belongs_dst_platform").val('').trigger('change');
        $("#belongs_dst_host").val('').trigger('change');
        $("#dst_host_ip").val('');
        $("#policy_port").val('');
        $("#start_date").val('');
        $("#end_date").val('');
        editFlag=false;
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
        var policy_id = $("#policy_id").val();
        var policy_name = $("#policy_name").val();
        var belongs_src_platform = $("#belongs_src_platform").val();
        var belongs_src_host = $("#belongs_src_host").val();
        var src_host_ip = $("#src_host_ip").val();
        var belongs_dst_platform = $("#belongs_dst_platform").val();
        var belongs_dst_host = $("#belongs_dst_host").val();
        var dst_host_ip = $("#dst_host_ip").val();
        var policy_protocol = $("#policy_protocol").val();
        var policy_port = $("#policy_port").val();
        var start_date = $("#start_date").val();
        var end_date = $("#end_date").val();
        var state = $("#state").val()
        var inputIds = {
            'policy_id': policy_id,
            'policy_name': policy_name,
            'src_platform': belongs_src_platform,
            'src_host': belongs_src_host,
            'src_ip': src_host_ip,
            'dst_platform': belongs_dst_platform,
            'dst_host': belongs_dst_host,
            'dst_ip': dst_host_ip,
            'policy_protocol': policy_protocol,
            'port': policy_port,
            'start_date': start_date,
            'end_date': end_date,
            'state': state
        };

        if (!saveBeforeCheck(policy_name,belongs_src_platform,belongs_src_host,src_host_ip,belongs_dst_platform,belongs_dst_host,dst_host_ip,policy_protocol,policy_port)){
            return false;
        }

        if (editFlag){
            var urls = "/assets/edit_data_network_policy/";
        }
        else{
            var urls = "/assets/add_data_network_policy/";
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
                $('#lb-msg').text('你没有增加网络策略的权限');
                $('#modal-notify').show();
            }
        });
    });
    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });


} );


// ========================= function ==================================
function saveBeforeCheck(policy_name,belongs_src_platform,belongs_src_host,src_host_ip,belongs_dst_platform,belongs_dst_host,dst_host_ip,policy_protocol,policy_port){
    if (policy_name == ''){
        $('#lb-msg').text('请输入网络策略名称!');
        $('#modal-notify').show();
        return false;
    };

    if (!belongs_src_platform){
        $('#lb-msg').text('请选择平台!');
        $('#modal-notify').show();
        return false;
    };

    

    if (!belongs_src_host){
        $('#lb-msg').text('请选择主机!');
        $('#modal-notify').show();
        return false;
    };


    if (!src_host_ip){
        $('#lb-msg').text('请选择IP!');
        $('#modal-notify').show();
        return false;
    };

    if (!belongs_dst_platform){
        $('#lb-msg').text('请选择平台!');
        $('#modal-notify').show();
        return false;
    };

    if (!belongs_dst_host){
        $('#lb-msg').text('请选择主机!');
        $('#modal-notify').show();
        return false;
    };

    if (!dst_host_ip){
        $('#lb-msg').text('请选择IP!');
        $('#modal-notify').show();
        return false;
    };

    if (!policy_port){
        $('#lb-msg').text('请输入端口!');
        $('#modal-notify').show();
        return false;
    };
    return true;

};

function preSelect2(postion,id,text){
    $(postion).html('');
    $(postion).append('<option value="' + id + '">' + text + '</option>');
    $(postion).select2('val',id,true);
};

function edit(id) {
    var data = {
        'id': id
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    table.ajax.reload();
    editFlag = true;
    $.ajax({
        type: "POST",
        url: "/assets/get_resource_network_policy/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            $("#myModalLabel").text("修改网络策略信息");
            $("#modal-notify").hide();
            $("#policy_id").val(data.policy_id);
            $("#show_network_policy_id").hide();
            $("#show_state").show();
            //console.log(roomid);
            $("#policy_name").val(data.policy_name);
            preSelect2("#belongs_src_platform", data.src_platform_id, data.src_platform);
            preSelect2("#belongs_src_host", data.src_host_id, data.src_host);
            preSelect2("#src_host_ip", data.src_ip, data.src_ip);
            preSelect2("#belongs_dst_platform", data.dst_platform_id, data.dst_platform);
            preSelect2("#belongs_dst_host", data.dst_host_id, data.dst_host);
            preSelect2("#dst_host_ip", data.dst_ip, data.dst_ip);
            $("policy_protocol").val(data.policy_protocol);
            $("state").val(data.state);
            $("#start_date").val(data.start_date);
            $("#end_date").val(data.end_date)
            $("#policy_port").val(data.port);
            $("#myModal").modal("show");
        },
        error: function(data){
            alert('你没有修改基础资源权限');
        }
    });
};

