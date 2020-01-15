function format ( d ) {
        // `d` is the original data object for the row
        return '<table cellpadding="5" cellspacing="1" border="1" style="padding-left:50px;">'+
            '<tr>'+
                '<td>使用者:</td>'+
                '<td>购入时间:</td>'+
                '<td>过保时间:</td>'+
                '<td>品牌:</td>'+
                '<td>状态:</td>'+
                '<td>机柜位置:</td>'+
                '<td>备注:</td>'+
            '</tr>'+
            '<tr>'+
                '<td>'+d.owner+'</td>'+
                '<td>'+d.purchase_date+'</td>'+
                '<td>'+d.eol_date+'</td>'+
                '<td>'+d.manufacturer+'</td>'+
                '<td>'+d.status+'</td>'+
                '<td>'+d.location+'</td>'+
                '<td>'+d.note+'</td>'+
            '</tr>'+
        '</table>';
}
var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

function filterGlobal () {
    $('#mytable').DataTable().search(
        $('#global_filter').val(),
        $('#global_regex').prop('checked'),
        $('#global_smart').prop('checked')
    ).draw();
};

function filterColumn ( i ) {
    $('#mytable').DataTable().column( i ).search(
        $('#col'+i+'_filter').val(),
        $('#col'+i+'_regex').prop('checked'),
        $('#col'+i+'_smart').prop('checked')
    ).draw();
};

function edit(type, series_id, property_id, server_type, cabinet_id, belong_cabinet, belong_project) {
    editFlag = true;
    $("#myModalLabel").text("修改设备信息");
    $("#user").val(type).attr("disabled",'true');
    $("#operate_time").val(series_id);
    $("#operate_obj").val(property_id);
    $("#operate_type").val(server_type);
    $("#result").val(cabinet_id);
    $("#belong_cabinet").val(belong_cabinet);
    $("#belong_project").val(belong_project);
    $("#myModal").modal("show");
};

// function parseDateValue(rawDate,dataTable) {
//     if (dataTable){
//         var dateAndTimeArray= rawDate.split(" ");
//         var dateArray = dateAndTimeArray[0].split("/");
//         var parsedDate= dateArray[0] + dateArray[1] + dateArray[2];
//     }else{
//         var dateArray= rawDate.split("-");
//         var parsedDate= dateArray[0] + dateArray[1] + dateArray[2];
//     };
//     return parsedDate;
// };

// $.fn.dataTable.ext.search.push(
//     function( settings, data, dataIndex ) {
//         var start_time = parseDateValue( $('#start_time').val(), false);
//         var end_time = parseDateValue( $('#end_time').val(), false);
//         var evalDate = parseDateValue( data[1], true); // use data for the age column
//         if ( ( isNaN( start_time ) && isNaN( end_time ) ) ||
//              ( isNaN( start_time ) && evalDate < end_time ) ||
//              ( start_time <= evalDate   && isNaN( end_time ) ) ||
//              ( start_time <= evalDate   && evalDate < end_time ) )
//         {
//             return true;
//         }
//         return false;
//     }
// );



$(document).ready(function() {
    table = $('#mytable').DataTable( {
        "processing": true,
        "serverSide": true,
        // "ajax": $.fn.dataTable.pipeline( {
        //     url: '/logs/show',
        //     pages: 5 // number of pages to cache
        // } ),
        // "ajax": "/logs/show",
        "ajax": {
            "url": "/logs/show",
            "data": function (d) {
                d.search_stime = $("#filter_start").val();
                d.search_etime = $("#filter_end").val();
                d.delete_stime = $("#start_time").val();
                d.delete_etime = $("#end_time").val()
            }
        },
        "columns": [
            {"data": "user"},
            {"data": "operate_time"},
            {"data": "operate_obj"},
            {"data": "operate_type"},
            {"data": "result"},
            {"data": "note"},
        ],
        "order": [[1, 'desc']],
        "language": {
                "url": "/static/js/i18n/Chinese.json"
        },
    } );
    $('input.global_filter').on( 'keyup click', function () {
        filterGlobal();
    } );

    $('input.column_filter').on( 'keyup click', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );

    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增设备信息");
        $("#type").removeAttr("disabled");
        $("#type").val('');
        $("#series_id").val('');
        $("#property_id").val('');
        $("#server_type").val('');
        $("#cabinet_id").val('');
        $("#belong_cabinet").val('');
        $("#belong_room").val('');
        $("#belong_project").val('');
        editFlag=false;
        $("#myModal").modal("show");
    } );
    $('#file-save').click( function () {
        $("#Modal-file").modal("hide");
    } );
    $('#bt-input').click( function () {
        $("#Modal-file").modal("show");
    } );
    $('#bt-search').click(function(){
        $('#filter_start').val('');
        $('#filter_end').val('');
        $('#div-search').toggleClass('hide');
    });
    $('#bt-showdel').click(function(){
        $('#start_time').val('');
        $('#end_time').val('');
        $('#div-del').toggleClass('hide');
        table.ajax.reload();
    });
    $('#start_time').Zebra_DatePicker({
        pair: $('#end_time'),
    });
    $('#end_time').Zebra_DatePicker({
        direction: 1,
    });
    $('#filter_start').Zebra_DatePicker({
        pair: $('#filter_end'),
    });
    $('#filter_end').Zebra_DatePicker({
        direction: 1,
    });
    
    $('#start_time,#filter_start,#filter_end,#end_time').blur(function () {
        table.ajax.reload();
    } );
    // $('#start_time, #end_time').change(function () {
    //     console.log($('#start_time, #end_time'))
    //     var time = {'start_time': $('#start_time').val(),'end_time': $('#end_time').val()}
    //     $.ajax({
    //         type: "POST",
    //         url: "/logs/search",
    //         contentType: "application/json; charset=utf-8",
    //         data: $.toJSON(time),
    //         success: function (data) {
    //             if (data['data']) {
    //                 table.ajax.reload();
    //             }else{
    //                 alert(data['msg'])
    //             };
    //         }
    //     });
    // });

    $('#bt-save').click( function(){
        var inputIds=$('#modal-list input').map(function(i,n){
            return $(n).val();
        }).get();
        if(editFlag){
            var data = table.rows().data()
            for (x in data)
            {
                if (data[x]['type'] == inputIds[0]){
                    var row=x-1
                    $('#mytable').dataTable().fnDeleteRow(row);
                    $("#myModal").modal("hide");
                }
            }
        }
        $.ajax({
            type: "POST",
            url: "/dashboard/device_add",
            data: inputIds,
            success: function (data) {
                // table.ajax.reload();
                table.row.add(data).draw();
                $("#myModal").modal("hide");
                // $("#myModalLabel").text("新增");
                // clear();
                
            }
        });
    });

    $('#bt-del').click(function(){
        var raw={
                "start_time": $("#start_time").val(),
                "end_time": $('#end_time').val()
            };
        if(confirm("您确定要删除:开始时间("+$("#start_time").val()+"),结束时间("+$('#end_time').val()+")的日志？")){
            var pdata=$.toJSON( raw );
            $.ajax({
                type: "POST",
                url: "/logs/delete",
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    
                    if (data['data']) {
                        table.ajax.reload();
                    }else{
                        alert(data['msg'])
                    };
                }
            });
        };
    });
} );
