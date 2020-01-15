
var table;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var socket;

var bar;

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


// datatable children row
function format ( d ) {
    // `d` is the original data object for the row
    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
        '<tr>'+
            '<td>更新结果:</td>'+
            '<td>'+d.update_data_data+'</td>'+
        '</tr>'+
        '<tr>'+
            '<td>erl结果:</td>'+
            '<td>'+d.erl_data_data+'</td>'+
        '</tr>'+
    '</table>';
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
    var id = $.urlParam('id');
    var protocol = window.location.protocol;
    if ( protocol == 'http:' ) {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/hot_server_detail/" + id, null, {debug: true});
    // var wsurl = new ReconnectingWebSocket("ws://" + window.location.host + "/ws/hot_server_detail/" + id);
    // socket = new WebSocket(wsurl);

    socket.onmessage = function(e) {
        var data = $.parseJSON(e.data);
        console.log(data)
        /*
            data 的数据格式
            message: 'ready' or 'update' or 'finished'
            status:"1"
            ...
        */

        var status = data.status

        if ( data.message == 'finished' ) {
            var total = data.total;
            var finished = data.finished;
            var succeed = data.succeed;
            var failed = data.failed;
            $("#show_result").html("总数:" + total + " 已完成:" + finished + " 成功:" + succeed + " 失败:" + failed);
            if ( status == '2' ) {
                $("#show_result_panel").attr('class', 'panel panel-red');
                $("#show_result_success").html("糟糕,有失败的更新,搜索失败查看详情")
            } else {
                $("#show_result_success").html("更新完成");
            }
            bar.animate(1);
        } else if ( data.message == 'ready' ) {
            $("#show_result").html('');
            $("#show_result_success").html("等待更新中...");
            bar.animate(0);
        } else {
            var total = data.total;
            var finished = data.finished;

            $("#show_result").html("总数:" + total + " 已完成:" + finished);
            $("#show_result_success").html("正在更新中...");
            bar.animate(finished/total);
        }
    }

    socket.onopen = function() {
        socket.send("start ws connection");
    }

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}


function init_progress() {
    var settings = {
            strokeWidth: 4,
            easing: 'easeInOut',
            duration: 1400,
            color: '#FCB03C',
            trailColor: '#eee',
            trailWidth: 1,
            svgStyle: {width: '100%', height: '100%'},
            /*text: {
                style: {
                    // Text color.
                    // Default: same as stroke color (options.color)
                    color: '#999',
                    position: 'absolute',
                    right: '0',
                    top: '30px',
                    padding: 0,
                    margin: 0,
                    transform: null
                },
            },*/
            autoStyleContainer: false,
            from: {color: '#FFEA82'},
            to: {color: '#ED6A5A'},
            step: (state, bar) => {
                bar.setText(Math.round(bar.value() * 100) + ' %');
            }
        };

    bar = new ProgressBar.Line('#container', settings);
}


function formatRepo (repo) {
    
    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};


$(document).ready(function() {

    var rows_selected = [];
    table = $('#mytable').DataTable( {
        // "processing": true,
        "ordering": false,
        // "serverSide": true,
        "ajax": {
            "url": "/myworkflows/data_host_server_detail/",
            "type": "POST",
            "data": function(d){
                d.hot_server_id = $.urlParam('id');
            }
        },
        "columns": [
            {
                "className": 'details-control',
                "orderable": false,
                "data": null,
                "defaultContent": '',
            },
            {"data": "gtype"},  // 1
            {"data": 'pf_name'},  //2
            {"data": 'srv_name'},  //3
            {"data": 'srv_id'},  // 4
            {"data": "ip"},  // 5
            // {"data": "update_data_data"},
            {"data": "update_data_status"},  // 6
            // {"data": "erl_data_data"},
            {"data": "erl_data_status"},  // 7
            {"data": "update_data_status"},  // 8
            {"data": "erl_data_status"},  // 9
        ],
        "order": [[2, 'asc']],
        columnDefs: [
                /*{    
                    'targets': [5, 7],
                    "render": function(data, type, row){
                        return data.split("\n\n").join("<br/>");
                    },
                },*/
                {
                    'targets': [6, 7],
                    'searchable':false,
                    'orderable':false,
                    'className': 'dt-body-left',
                    'render': function (data, type, full, meta){
                        if ( data == '成功'){
                            return '<span class="label label-success">' + data + '</span>';
                        } else if ( data == '失败' ) {
                            return '<span class="label label-danger">' + data + '</span>';
                        } else if ( data == '待更新' ) {
                            return '<span class="label label-primary">' + data + '</span>';
                        } else{
                            return '<span class="label label-default">' + data + '</span>';
                        }
                    },
                },
                {
                    'targets': [8, 9],
                    'visible':false,
                },
                
        ],
        "language": {
                "url": "/static/js/i18n/Chinese.json"
        },
    });

    init_progress();
    init_ws();

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

    
    // datatable children row on click
    // Add event listener for opening and closing details
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

    

    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });

    $('input.column_filter').on( 'keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    } );

    $("#bt-reset").click( function(){
        // 重置高级搜索
        table.ajax.reload();

    } );

    $("#bt-refresh").click(function(event) {
        /* Act on the event */
        table.ajax.reload();
    });

    $("#bt-failed").click(function(event) {
        /* Act on the event */
        table.search('失败').draw();
    });

    $("#bt-success").click(function(event) {
        /* Act on the event */
        table.search('成功').draw();
    });

    $("#bt-clear").click(function(event) {
        /* Act on the event */
        table.search('').draw();
    });


} );
