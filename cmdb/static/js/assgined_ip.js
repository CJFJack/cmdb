// 修改之前的数据
var origin_data;
var table;
var editFlag;
var deviceFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);
var select2Bleongs_to_iptype;
var condition = ''

function initModalSelect2(){
    // 初始化select2
    $select2Bleongs_to_iptype = $("#belongs_to_iptype").select2({
        ajax: {
            url: '/assets/list_iptype/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function(params){
                return {
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



function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_ip_assgined_ip/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改物理ip");
            $("#modal-notify").hide();
            $("#id").val(id);
            $("#show_id").hide();
            $("#ip").val(data.ip);
            $("#vlan").val(data.vlan);
            initSelect2("belongs_to_iptype", data.belongs_to_iptype_id, data.belongs_to_iptype);
            $("#myModal").modal("show");
        },
        error: function(data){
            alert('你没有修改ip管理的权限');
        }
    });
};

function checkBeforeAdd(vip_belongs_to_iptype,vlan,vip,belongs_to_service_id){
    if (vip_belongs_to_iptype == '0'){
        $('#lb-msg').text('请选择ip类型!');
        $('#modal-notify').show();
        return false;
    }
    
    if (vlan == ''){
        $('#lb-msg').text('vlan不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (vip == '') {
        $('#lb-msg').text('vip!');
        $('#modal-notify').show();
        return false;
    }
    if (belongs_to_service_id.length == 0){
        $('#lb-msg').text('请先选择host主机!');
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
        "ajax": "/assets/data_assgined_ip",
        "columns": [
            {"data": null},
            {"data": 'id'},
            {"data": 'ip'},
            {"data": 'vlan'},
            {"data": "belongs_to_iptype"},
            {
              "data": null,
              "orderable": false,
            }
        ],
        //"order": [[1, 'asc']],
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
                    targets: 5,
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

    $('#chb-all').on('click', function(e){
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function(i,n){
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked){
              $row.addClass('selected');
            }else{
              $row.removeClass('selected');
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
        $("#myModalLabel").text("新增Vip");
        $("#modal-notify").hide();
        $("#vip_belongs_to_iptype").val("0").trigger("change");
        $("#vlan").val('');
        $("#vip").val('');
        $("#belongs_to_platform").val('0').trigger("change");
        $("#belongs_to_host").val('0').trigger("change");
        $("#belongs_to_service").val('').trigger("change");
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
        var vlan = $("#vlan").val();
        var belongs_to_iptype = $("#belongs_to_iptype").select2('data')[0].id;
        if (!ip){
            $('#lb-msg').text('ip不能为空');
            $('#modal-notify').show();
            return false;
        }
        var urls = "/assets/edit_data_assgined_ip/";
        var inputIds = {
                'id': id,
                'ip': ip,
                'vlan': vlan,
                'belongs_to_iptype': belongs_to_iptype,
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
        });
    });
    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });


} );
