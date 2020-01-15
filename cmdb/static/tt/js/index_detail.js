
var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
//var template = Handlebars.compile(tpl);


function filterGlobal () {
    $('#mytable').DataTable().search(
        $('#global_filter').val(),
        $('#global_regex').prop('checked'),
        $('#global_smart').prop('checked')
    ).draw();
}
 
function filterColumn ( i ) {
    $('#mytable').DataTable().column( i ).search(
        $('#col'+i+'_filter').val(),
        $('#col'+i+'_regex').prop('checked'),
        $('#col'+i+'_smart').prop('checked')
    ).draw();
}

function initCheckBox(){
    // 请求当前用户的默认展示选项
    $.ajax({
        type: "POST",
        url: "/assets/get_config_index/",
        contentType: "application/json; charset=utf-8",
        success: function(data){
            choosen = data.data    // list
            var len = choosen.length;
            for (var i=0; i<len; i++) {
                // checkbox选中
                $(':checkbox.toggle-visiable[value='+ choosen[i] +']').prop('checked', true);
                // 展示datatables的colmun
                column = table.column(choosen[i]);
                column.visible(true);
            }

        }
    });
};


function filterGlobal () {
    $('#mytable').DataTable().search(
        $('#global_filter').val(),
        $('#global_regex').prop('checked'),
        $('#global_smart').prop('checked')
    ).draw();
}
 
function filterColumn ( i ) {
    $('#mytable').DataTable().column( i ).search(
        $('#col'+i+'_filter').val(),
        $('#col'+i+'_regex').prop('checked'),
        $('#col'+i+'_smart').prop('checked')
    ).draw();
}

$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURIComponent(results[1]) || 0;
    }
}

$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {

        "processing": true,
        'ordering': false,
        "ajax": {
            'type': 'POST',
            'url': '/assets/platform_detail/',
            'data': function( d ){
                d.platform_name = $.urlParam('platform_name');
            }
        },
        "columns": [
            //{"data": null},
            {"data": "id"},
            {"data": "platform_name"},
            {"data": 'hostname'},
            {"data": 'assigned_ip_info.ip'},
            {"data": 'assigned_ip_info.vlan'},
            {"data": 'assigned_ip_info.netmask'},
            {"data": 'assigned_ip_info.gateway'},
            {"data": 'assigned_ip_info.iptype'},
            {"data": 'assigned_ip_info.network_zone'},
            {"data": 'vip_info.ip'},
            {"data": 'vip_info.vlan'},
            {"data": 'vip_info.netmask'},
            {"data": 'vip_info.gateway'},
            {"data": 'vip_info.iptype'},
            {"data": 'vip_info.network_zone'},
            {"data": 'public_or_load_ip'},
            {"data": 'apptype'},
            {"data": 'applications'},
            {"data": 'templatename'},
            {"data": 'ostype'},
            {"data": 'config'},
            {"data": 'status'},
            /*{
              "data": null,
              "orderable": false,
            }*/
        ],


        "order": [[1, 'asc']],
        columnDefs: [
                {
                    'targets': 0,
                    'visible': false,
                    'searchable': false
                },
                {
                    'targets': [3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],
                    "render": function(data, type, row){
                        if (data){
                            return data.split(",").join("<br/>");
                        }else{
                            return ''
                        }
                    },
                },
                {
                    'targets': [3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
                    'visible': false,
                },
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

    table2 = $('#mytable2').DataTable( {
        "processing": true,
        "ajax": {
            'type': 'GET',
            'url': '/assets/data_network_policy/',
            'data': function( d ){
                d.platform_name = $.urlParam('platform_name');
            }
        },
        "columns": [
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
        ],
        "order": [[1, 'asc']],
        columnDefs: [
                {
                    'targets': 1,
                    'visible': false,
                    'searchable': false
                },
        ],
        "language": {
                "url": "/static/js/i18n/Chinese.json"
        },
    });

    $(':checkbox.toggle-visiable').prop('checked', false);

    initCheckBox();

    $(':checkbox.toggle-visiable').on( 'click', function (e) {
        //e.preventDefault();
 
        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column( $(this).attr('value') );
        // table.ajax.reload();
        column.visible( is_checked );
    } );
    
    

    
    //$resourceType.on("select2:select", function (e) { autofill("select2:select", e); });
    //show or hide column
    
    $('input.global_filter').on( 'keyup click', function () {
        filterGlobal();
    } );

    $('input.column_filter').on( 'keyup click', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );
    $('select.column_filter').on('change', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );
    
    $('#bt-add').click( function () {
        $.ajax({
            type: "POST",
            url: "/assets/get_config_index/",
            contentType: "application/json; charset=utf-8",
            success: function(data){
                $("#myModalLabel").text("我的默认配置");
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                choosen = data.data    // list
                var len = choosen.length;
                for (var i=0; i<len; i++) {
                    // checkbox选中
                    $(':checkbox.config[value='+ choosen[i] +']').prop('checked', true);
                    // 展示datatables的colmun
                    column = table.column(choosen[i]);
                    column.visible(true);
                }
            }
        });
    });

    $('#bt-save').click( function () {
        var choosen = new Array();
        $(':checkbox.config').each(function(el){
            if ($(this).is(':checked')){
                // console.log( $(this).prop('value') );
                choosen.push($(this).prop('value'));
            }
        });
        // console.log(choosen);
        var inputIds = {
                'choosen': choosen,
            };
        var urls = '/assets/add_config_index/';
        var encoded=$.toJSON( inputIds );
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                
                if (data['data']) {
                    // table.ajax.reload();
                    location.reload();
                    // $("#myModal").modal("hide");
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

    $('input.global_filter').on( 'keyup click', function () {
        filterGlobal();
    } );

    $('input.column_filter').on( 'keyup click', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );


} );
