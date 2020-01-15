// 修改之前的数据
var origin_data;

var table;
var editFlag;
var deviceFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的机房?";
var count=0;



var select2PoolStatus;
var select2PoolType;
var select2Bleongs_to_iptype;
var select2Bleongs_to_iptype2;
var select2InPairWith;
var select2Belongs_to_platform;


function initModalSelect2(){
    // 初始化select2

    $select2PoolStatus = $("#pool_status").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2PoolType = $("#pool_type").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2Bleongs_to_iptype = $("#belongs_to_iptype").select2({
        ajax: {
            url: '/assets/list_iptype/',
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

    $select2Bleongs_to_iptype2 = $("#belongs_to_iptype2").select2({
        ajax: {
            url: '/assets/list_iptype/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            /*data: function(term, page){
                return {
                    'ip_type': 'any',
                }
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
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2InPairWith = $("#in_pair_with").select2({
        ajax: {
            url: '/assets/list_ip_pool/',
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
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};

function log(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        var ostype = $('#belongs_to_ostype').select2('data')[0].id;
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



function edit(ip_segment) {
    editFlag = true;
    var data = {
        'id': ip_segment,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;

    $.ajax({
        type: "POST",
        url: "/assets/get_ip_ip_pool/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改IP资源池信息");
            $("#modal-notify").hide();

            $("#ip_segment").val(data.ip_segment);
            $("#show_ip_segment").hide();

            $("#start_ip").val(data.start_ip);
            $("#en_ip").val(data.en_ip);
            $("#gateway").val(data.gateway);
            $("#netmask").val(data.netmask);
            $("#vlan").val(data.vlan);
            $("#pool_status").val(data.pool_status).trigger('change');

            $("#belongs_to_iptype").html('');
            $("#belongs_to_iptype").append('<option value="' + data.belongs_to_iptype_id + '">' + data.belongs_to_iptype + '</option>');
            $("#belongs_to_iptype").select2('val', data.belongs_to_iptype_id, true);

            $("#belongs_to_iptype2").html('');
            $("#belongs_to_iptype2").append('<option value="' + data.belongs_to_iptype2_id + '">' + data.belongs_to_iptype2 + '</option>');
            $("#belongs_to_iptype2").select2('val', data.belongs_to_iptype2_id, true);

            if (data.in_pair_with!='0'){
                $("#in_pair_with").html('');
                $("#in_pair_with").append('<option value="' + data.in_pair_with + '">' + data.in_pair_with_ip + '</option>');
                $("#in_pair_with").select2('val', data.in_pair_with, true);
            }else{
                $("#in_pair_with").val('0').trigger('change');
            }

            $("#belongs_to_platform").html('');
            $("#belongs_to_platform").append('<option value="' + data.ip_pool_belongs_to_platform_id + '">' + data.ip_pool_belongs_to_platform + '</option>');
            $("#belongs_to_platform").select2('val', data.ip_pool_belongs_to_platform_id, true);

            $("#myModal").modal("show");


        },
        error: function(data){
            alert('你没有修改ip管理的权限');
        }
    });
};

function checkBeforeAdd(start_ip,en_ip,netmask,belongs_to_iptype){

    if (start_ip == ''){
        $('#lb-msg').text('起始ip不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (en_ip == '') {
        $('#lb-msg').text('结束ip不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (netmask == ''){
        $('#lb-msg').text('掩码不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (belongs_to_iptype == '0'){
        $('#lb-msg').text('请选择ip类型!');
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
    // test on move
    /*$(".modal-dialog").mousedown(function(e){ 
        $(this).css("cursor","move");//改变鼠标指针的形状 
        var offset = $(this).offset();//DIV在页面的位置 
        var x = e.pageX - offset.left;//获得鼠标指针离DIV元素左边界的距离 
        var y = e.pageY - offset.top;//获得鼠标指针离DIV元素上边界的距离 
        $(document).bind("mousemove",function(ev){ //绑定鼠标的移动事件，因为光标在DIV元素外面也要有效果，所以要用doucment的事件，而不用DIV元素的事件 
        
            $(".modal-dialog").stop();//加上这个之后 
            
            var _x = ev.pageX - x;//获得X轴方向移动的值 
            var _y = ev.pageY - y;//获得Y轴方向移动的值 
        
            $(".modal-dialog").animate({left:_x+"px",top:_y+"px"},10); 
        }); 

    }); 

    $(document).mouseup(function() { 
        $(".modal-dialog").css("cursor","default"); 
        $(this).unbind("mousemove"); 
    });*/





    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        'ordering': false,
        "ajax": "/assets/data_ip_pool",
        "columns": [
            {"data": null},
            {"data": 'ip_segment'},
            {"data": 'start_ip'},
            {"data": "en_ip"},
            {"data": "gateway"},
            {"data": "netmask"},
            {"data": "vlan"},
            {"data": "belongs_to_iptype"},
            {"data": "pool_status"},
            {"data": "pool_type"},
            {"data": "ip_pool_belongs_to_platform"},
            {
              "data": null,
              "orderable": false,
            }
        ],
        // "order": [[1, 'asc']],
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
                    'searchable': false,
                },
                {    
                    'targets': 7,
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },
                {
                    targets: 11,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.ip_segment + "\')", "type": "primary"},
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
        $("#myModalLabel").text("新增资源池");
        $("#modal-notify").hide();
        $("#show_ip_segment").hide();
        $("#ip_segment").val('');
        $("#start_ip").val('');
        $("#en_ip").val('');
        $("#gateway").val('');
        $("#netmask").val('');
        $("#netmask").val('');
        $("#vlan").val('');
        //$("#belongs_to_iptype").val('0').trigger('change');
        initSelect2('belongs_to_iptype', '0', '选择ip类型');
        initSelect2('belongs_to_iptype2', '0', '选择ip类型');
        $("#pool_status").val('1').trigger('change');
        $("#in_pair_with").val('0').trigger('change');
        //$("#belongs_to_platform").val('0').trigger('change');
        initSelect2('belongs_to_platform', '0', '选择平台');
        editFlag=false;
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
        var ip_segment = $("#ip_segment").val();
        var start_ip = $("#start_ip").val();
        var en_ip = $("#en_ip").val();
        var gateway = $("#gateway").val();
        var netmask = $("#netmask").val();
        var vlan = $("#vlan").val();
        var pool_status = $("#pool_status").select2('data')[0].id;
        var pool_type = $("#pool_type").select2('data')[0].id;
        var belongs_to_iptype = $("#belongs_to_iptype").select2('data')[0].id;
        var belongs_to_iptype2 = $("#belongs_to_iptype2").select2('data')[0].id;
        var in_pair_with = $("#in_pair_with").select2('data')[0].id;
        var ip_pool_belongs_to_platform = $("#belongs_to_platform").select2('data')[0].id;


        var inputIds = {
                'ip_segment': ip_segment,
                'start_ip': start_ip,
                'en_ip': en_ip,
                'gateway': gateway,
                'netmask': netmask,
                'vlan': vlan,
                'pool_status': pool_status,
                'pool_type': pool_type,
                'in_pair_with': in_pair_with,
                'belongs_to_iptype': belongs_to_iptype,
                'belongs_to_iptype2': belongs_to_iptype2,
                'ip_pool_belongs_to_platform': ip_pool_belongs_to_platform,
                "origin_data": origin_data,
            };
        
        if ( !checkBeforeAdd(start_ip,en_ip,netmask,belongs_to_iptype) ){
            return false;
        }

        if (editFlag){
            var urls = "/assets/edit_data_ip_pool/";
        }
        else{
            var urls = "/assets/add_data_ip_pool/";
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
                $('#lb-msg').text('你没有增加ip管理的权限');
                $('#modal-notify').show();
            }
        });
    });

    $("#bt-del").confirm({
        //text:"确定删除所选的资源池?",
        confirm: function(button){
            var selected = getSelectedTable('ip_segment');

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_ip_pool/",
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


    $("#reset").click(function(){
        $("#in_pair_with").html('');
        $("#in_pair_with").append('<option value="0">选择成对的段</option>');
        $("#in_pair_with").select2('val', "0", true);
    });

    $("#reset_platform").click(function(){
        initSelect2('belongs_to_platform', '0', '选择平台');
    });

} );
