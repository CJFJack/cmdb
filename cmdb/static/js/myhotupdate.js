
var table;
var table2;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var socket;


$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURIComponent(results[1]) || 0;
    }
}


function init_ws(){
    var protocol = window.location.protocol;
    if ( protocol == 'http:' ) {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/hot_update/hot_server", null, {debug: true});

    socket.onmessage = function(e) {
        if ( e.data == 'update_table'){
            console.log('table.ajax.reload()');
            table.ajax.reload();
            table2.ajax.reload();
        }
    }

    socket.onopen = function() {
        socket.send("start ws connection");
    }

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}

function show_detail(id) {
    redirect_url = "/myworkflows/host_server_detail?id=" + id;
    window.location.href = redirect_url;
}


function show_myworkflow(id, update_type) {
    redirect_url = "/myworkflows/myworkflow_hotupdate?id=" + id + '&update_type=' + update_type;
    window.location.href = redirect_url;
}

function formatRepo (repo) {
    
    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};


$(document).ready(function() {

    init_ws();

    var rows_selected = [];
    table = $('#mytable').DataTable( {
        // "processing": true,
        "ordering": false,
        "serverSide": false,
        "info": false,
        "searching": false,
        "paging": false,
        "ajax": {
            "url": "/myworkflows/data_myhotupdate/",
            "type": "POST",
            "data": function(d){
                d.id = $.urlParam('id');
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": 'project'},  //1
            {"data": 'area_name'},  //1
            {"data": 'update_type'},  //1
            {"data": 'title'},  // 2
            {"data": 'uuid'},  // 2
            {"data": 'pair_code'},  // 2
            {"data": 'order'},  // 2
            {"data": "priority"},  // 3
            {"data": "status"},  // 4
            {
              "data": null,
              "orderable": false,
            }
        ],
        "order": [[1, 'asc']],
        columnDefs: [
                {
                    'targets': 0,
                    'visible': false,
                    'searchable': false
                },
                {
                    'targets': 9,
                    'searchable':false,
                    'orderable':false,
                    'className': 'dt-body-left',
                    'render': function (data, type, full, meta){
                        if ( data == '更新成功'){
                            return '<span class="label label-success">' + data + '</span>';
                        }else if ( data == '更新中' ){
                            return '<span class="label label-info">' + data + '</span>';
                        }else if (data == '更新失败'){
                            return '<span class="label label-danger">' + data + '</span>';
                        }else if (data == '待更新'){
                            return '<span class="label label-warning">' + data + '</span>';
                        }else{
                            return '<span class="label label-default">' + data + '</span>';
                        }
                    },
                },
                {
                    targets: 10,
                    render: function (a, b, c, d) {
                        if ( c.update_type == '后端' ) {
                            var context =
                            {
                                func: [
                                    {"name": "更新详细", "fn": "show_detail(\'" + c.id + "\')", "type": "info"},
                                ]
                            };
                        } else {
                            var context =
                            {
                                func: [
                                    // {"name": "更新详细", "fn": "show_detail(\'" + c.id + "\')", "type": "info"},
                                ]
                            };
                        }
                        var html = template(context);
                        return html;
                    }
                }
                
        ],
        "language": {
                "url": "/static/js/i18n/Chinese.json"
        },
    });

    var rows_selected2 = [];
    table2 = $('#mytable2').DataTable( {
        // "processing": true,
        "ordering": false,
        "serverSide": false,
        "info": false,
        "searching": false,
        "paging": false,
        "ajax": {
            "url": "/myworkflows/data_myhotupdate_block/",
            "type": "POST",
            "data": function(d){
                d.id = $.urlParam('id');
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": 'project'},  //1
            {"data": 'area_name'},  //1
            {"data": 'update_type'},  //1
            {"data": 'title'},  // 2
            {"data": 'uuid'},  // 2
            {"data": 'pair_code'},  // 2
            {"data": 'order'},  // 2
            {"data": "priority"},  // 3
            {"data": "status"},  // 4
        ],
        "order": [[1, 'asc']],
        columnDefs: [
                {
                    'targets': 0,
                    'visible': false,
                    'searchable': false
                },
                {
                    'targets': 9,
                    'searchable':false,
                    'orderable':false,
                    'className': 'dt-body-left',
                    'render': function (data, type, full, meta){
                        if ( data == '更新成功'){
                            return '<span class="label label-success">' + data + '</span>';
                        }else if ( data == '更新中' ){
                            return '<span class="label label-info">' + data + '</span>';
                        }else if (data == '更新失败'){
                            return '<span class="label label-danger">' + data + '</span>';
                        }else if (data == '待更新'){
                            return '<span class="label label-warning">' + data + '</span>';
                        }else{
                            return '<span class="label label-default">' + data + '</span>';
                        }
                    },
                },
                {
                    targets: 10,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "工单详细", "fn": "show_myworkflow(\'" + c.id + "\', \'" + c.update_type + "\')", "type": "info"},
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
    });



    $(':checkbox.toggle-visiable').on( 'click', function (e) {
        //e.preventDefault();
 
        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column( $(this).attr('value') );
        // table.ajax.reload();
        column.visible( is_checked );
    } );

    $('#bt-modal-notify').click( function () {
        $("#modal-notify").hide();
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

    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });

    $('input.column_filter').on( 'keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    } );

    $("#bt-reset").click( function(){
        // 重置高级搜索
        $("#filter_ctype").val('100').trigger('change');
        $("#filter_assets_number").val('');
        $("#filter_name").val('');
        $("#filter_brand").val('');
        $("#filter_specification").val('');
        $("#filter_using_department").val('');
        $("#filter_user").val('');
        $("#filter_user").val('');
        $("#filter_status").val('100').trigger('change');
        $("#filter_pos").val('0').trigger('change');
        $(".filter_select2").val('0').trigger('change');
        table.ajax.reload();

    } );

    $("#bt-refresh").click(function(event) {
        /* Act on the event */

        table.ajax.reload();
    });

    $('#bt-save').click( function(){

        var id = $("#id").val();
        var status = $("#status").select2('data')[0].id;
        var priority = $("#priority").select2('data')[0].id;
        var update_type = $("#update_type").val();

        var inputIds = {
          "id": id,
          "status": status,
          "priority": priority,
          "update_type": update_type,
        };

        var encoded=$.toJSON( inputIds )
        var pdata = encoded

        var urls = '/myworkflows/edit_hot_server_task/'

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
                if (editFlag){
                    $('#lb-msg').text('你没有修改基础资源权限');
                    $('#modal-notify').show();
                }else{
                    $('#lb-msg').text('你没有增加基础资源权限');
                    $('#modal-notify').show();
                }
            }
        });
    });


} );
