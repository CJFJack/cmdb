
var table;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var socket;

function initModalSelect2(){
    $("#status").select2();
    $("#priority").select2();
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


function init_ws(){
    socket = new WebSocket("ws://" + window.location.host + "/ws/hot_update/hot_client");

    socket.onmessage = function(e) {
        if ( e.data == 'update_table'){
            table.ajax.reload();
        }
    }

    socket.onopen = function() {
        socket.send("start ws connection");
    }

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}


function edit(id){
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;

    $.ajax({
        type: "POST",
        url: "/myworkflows/get_hot_client_task/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改前端热更新任务");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide();
            $("#project").val(data.project);
            $("#area_name").val(data.area_name);
            $("#title").val(data.title);
            $("#priority").val(data.priority_code).trigger('change');
            $("#status").val(data.status_code).trigger('change');
            $("#myModal").modal("show");
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
}


function execute(id){
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;

    $.ajax({
        type: "POST",
        url: "/myworkflows/execute_hot_client_task/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            if ( data.success ) {
                table.ajax.reload();
            } else {
                alert(data.msg);
                table.ajax.reload();
            }
        },
        error: function (xhr, status, error) {
            alert('执行失败');
            table.ajax.reload();
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


$(document).ready(function() {

    initModalSelect2();

    init_ws();

    var rows_selected = [];
    table = $('#mytable').DataTable( {
        // "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/myworkflows/data_hot_client_list/",
            "type": "POST",
            "data": function(d){
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": 'project'},  //1
            {"data": 'area_name'},  //1
            {"data": 'title'},  // 2
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
                    'targets': 5,
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
                    targets: 6,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                {"name": "执行", "fn": "execute(\'" + c.id + "\')", "type": "success"},
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

        var inputIds = {
          "id": id,
          "status": status,
          "priority": priority,
        };

        var encoded=$.toJSON( inputIds )
        var pdata = encoded

        var urls = '/myworkflows/edit_hot_client_task/'

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
