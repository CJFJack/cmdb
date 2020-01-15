// 修改之前的数据
var origin_data;
// 全局的tname，用来判断在哪个表中
var table_name;

var table;
var editFlag;
var deviceFlag;
//预编译模板
var tpl = $("#tpl").html();

var str = "确定删除?";
var count=0;

var template = Handlebars.compile(tpl);
var select2TargetIp;
var select2Belongs_to_platform;
var select2Belongs_to_iptype;
var condition = ''

function initModalSelect2(){
    // 初始化select2

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

    $select2Belongs_to_iptype = $('#belongs_to_iptype').select2( {
        ajax: {
            url: '/assets/list_iptype/',
            dataType: 'json',
            type: 'POST',
            data: function(term, page){
                return {
                    'ip_type': 'VIP',
                    //'addition_id': selected_addtion_iptype
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
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });


    $select2TargetIp = $('#target_ip').select2( {
        ajax: {
            url: '/assets/list_all_ip/',
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
                            type: item.type,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        placeholder: '选择目标IP',
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        multiple: true,
        //templateResult: formatRepo, // omitted for brevity, see the source of this page
        //templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
        dropdownAutoWidth: true,
    });

    
    // let's add event change to condition
    $select2Belongs_to_platform;
    $select2Belongs_to_platform.on("select2:select", function (e){ log("select2:select", e); });


    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};

function log(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        var platform = $('#belongs_to_platform').select2('data')[0].id;
        condition = {"platform": platform};
        $select2Belongs_to_host = $('#belongs_to_host').select2( {
            ajax: {
                url: '/assets/list_hosts/',
                dataType: 'json',
                type: 'POST',
                delay: 250,
                data: condition,
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
        $("#belongs_to_host").val('').trigger('change');
        $select2Belongs_to_service = $('#belongs_to_service').select2( {
            ajax: {
                url: '/assets/list_service/',
                dataType: 'json',
                type: 'POST',
                delay: 250,
                data: condition,
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
            placeholder: '选择服务',
            multiple: true,
            dropdownAutoWidth: true,
            minimumResultsForSearch: Infinity,
            escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
            // minimumInputLength: 1,
            templateResult: formatRepo, // omitted for brevity, see the source of this page
            templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
        });
        $("#belongs_to_service").val('').trigger('change');
    }
};

function log2(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        var host = $("#belongs_to_host").select2('data')[0].id;
        condition = {"host": host}
        $select2Belongs_to_service = $('#belongs_to_service').select2( {
            ajax: {
                url: '/assets/list_service/',
                dataType: 'json',
                type: 'POST',
                delay: 250,
                data: condition,
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
            placeholder: '选择服务',
            multiple: true,
            dropdownAutoWidth: true,
            minimumResultsForSearch: Infinity,
            escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
            // minimumInputLength: 1,
            templateResult: formatRepo, // omitted for brevity, see the source of this page
            templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
        });
        $("#belongs_to_service").val('').trigger('change');

    }
};



function edit(tname, id) {
    editFlag = true;
    var data = {
        'tname': tname,
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
     $.ajax({
        type: "POST",
        url: "/assets/get_ip_public_ip/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
                origin_data = data;
                table_name = tname;
                $("#myModalLabel").text("修改公网或负载IP");
                $("#modal-notify").hide();
                $("#show_id").hide();
                $("#id").val(data.id);
                initSelect2('belongs_to_iptype', '0', '选择网络区域');
                $("#ip").val(data.ip);
                initSelect2('belongs_to_platform', data.belongs_to_platform_id.toString(), data.belongs_to_platform);
                $('input:radio[name=relation]').filter('[value=' + data.relation + ']').prop('checked',true);

                var target_info = data.target_info;
                $("#target_ip").html('');
                $("#target_ip").append('<option value="' + target_info.target_id + '">' + target_info.target_ip + '</option>')
                $("#target_ip").select2('val',target_info.target_id,true);
                // 这里给选中的select2添加一个type的属性
                $("#target_ip").select2('data')[0].type = target_info.target_type;

                $("#port").val(data.port);
                $("#remarks").val(data.remarks);

                $("#myModal").modal("show");
        },
        error: function(data){
            alert('你没有修改IP管理权限');
        }
    });
};

function checkBeforeAdd(ip,ip2,belongs_to_platform,target_id,port){
    if (! (ip || ip2) ){
        $('#lb-msg').text('请选择公网负载ip!');
        $('#modal-notify').show();
        return false;
    }
    
    if (belongs_to_platform == '0'){
        $('#lb-msg').text('请选择平台!');
        $('#modal-notify').show();
        return false;
    }
    if (target_id.length == 0) {
        $('#lb-msg').text('请选择目标ip!');
        $('#modal-notify').show();
        return false;
    }
    if (port == ''){
        $('#lb-msg').text('请先选择端口!');
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
        "ajax": "/assets/data_public_ip",
        "columns": [
            {"data": null},
            {"data": 'tname'},
            {"data": 'id'},
            {"data": 'belongs_to_platform'},
            {"data": 'ip'},
            {"data": 'relation'},
            {"data": 'target_ip'},
            {"data": 'port'},
            {"data": 'remarks'},
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
                    'targets': [1,2],
                    'visible': false,
                    'searchable': false
                },
                {
                    targets: 9,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.tname + "\', \'" + c.id + "\')", "type": "primary"},
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
              count = getSelectedTable('ip').length;
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

    $("#selected-all").click( function (){
        if (condition.host){
            var host_id = {
                'host': $("#belongs_to_host").select2('data')[0].id,
            }
            var encoded=$.toJSON( host_id );
            var pdata = encoded;
            $.ajax({
                type: "POST",
                url: "/assets/list_service/",
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    $("#belongs_to_service").val('').trigger('change');
                    $select2Belongs_to_device =  $("#belongs_to_service").select2({
                        data: data
                    });
                    var service_id = Array()
                    for (var i=0;i<data.length;i++){
                        service_id.push(data[i].id)
                    }
                    $("#belongs_to_service").val(service_id).trigger('change');
                }
            });
        }
        else{
            $('#lb-msg').text('要使用全选,请先选择host主机');
            $('#modal-notify').show();
            return false;
        }
    });

    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增公网与负载IP");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#ip").val('');
        $("#ip2").val('');
        initSelect2('belongs_to_platform', '0', '选择平台');
        initSelect2('belongs_to_iptype', '0', '选择网络区域');
        $('input:radio[name=relation]').filter('[value=映射]').prop('checked',true);
        $("#target_ip").val('').trigger("change");
        $("#port").val('');
        $("#remarks").val('');
        editFlag=false;
        $("#myModal").modal("show");
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
        var id = $("#id").val();
        var ip = $("#ip").val();
        var ip2 = $("#ip2").val();
        var belongs_to_platform = $("#belongs_to_platform").select2('data')[0].id;
        var relation = $('input[name=relation]:checked').val();

        var target_ip = $("#target_ip").select2('data');
        var target_id = Array();
        for (i=0; i<target_ip.length; i++){
            target_id.push([target_ip[i].type, target_ip[i].id]);
        }

        var port = $("#port").val();
        var remarks = $("#remarks").val();

        if (!checkBeforeAdd(ip,ip2,belongs_to_platform,target_id,port)){
            return false;
        };

        var inputIds = {
                'table_name': table_name,
                'id': id,
                'ip': ip,
                'ip2': ip2,
                'belongs_to_platform': belongs_to_platform,
                'relation': relation,
                'target_id': target_id,
                'port': port,
                'remarks': remarks,
                'origin_data': origin_data,
            };

        if (editFlag){
            var urls = "/assets/edit_data_public_ip/";
        }else{
            var urls = "/assets/add_data_public_ip/";
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

    //删除
    $("#bt-del").confirm({
        //text:"确定删除所选的vip?",
        confirm: function(button){
            var selected = new Array();

            table.rows('.selected').data().toArray().forEach(function(info,i){
                //console.log(selector.id);
                selected.push([info.id, info.tname]);
            });

            //  [[8, "vip_public_ip"], [9, "vip_public_ip"]]
            // console.log(selected);

            //return false;

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_public_ip_direct/",
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
        if ($("#belongs_to_iptype").select2('data')[0].id == '0'){
            return false;
        }else{
            var typename = $("#belongs_to_iptype").select2('data')[0].text;
            // Requeir ip from Server!
            var data = {
                'typename': typename,
                'is_public': 'true',
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
                        if ( data['is_in_pairs'] ){
                            var ipinfo = $.parseJSON(data.data);
                            $("#ip").val(ipinfo.ip[0]);
                            $("#ip2").val(ipinfo.ip[1]);
                        }else{
                            $("#ip").val(data.ip)[0];
                        }
                    }else{
                        $('#lb-msg').text(data['msg']);
                        $('#modal-notify').show();
                    }
                },

            });
        }
    });

    $("#reset_ip").click(function(){
        initSelect2('belongs_to_iptype', '0', '选择网络区域');
        $("#ip").val('');
        $("#ip2").val('');
    });


} );
