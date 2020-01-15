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

function edit(type, series_id, property_id, server_type, cabinet_id, belong_cabinet, belong_room, belong_project, accident_status, user, owner, location, purchase_date, eol_date, manufacturer, status, note) {
    // editFlag = true;
    // $("#myModalLabel").text("修改设备信息");
    // $("#type").val(type).attr("disabled",'true');
    // $("#series_id").val(series_id);
    // $("#property_id").val(property_id);
    // $("#server_type").val(server_type);
    // $("#cabinet_id").val(cabinet_id);
    // $("#belong_cabinet").val(belong_cabinet);
    // $("#belong_room").val(belong_room);
    // $("#belong_project").val(belong_project);
    // $("#myModal").modal("show");
    window.location.href='/dashboard/flow_edit'
}

function back(type, series_id, property_id, server_type, cabinet_id, belong_cabinet, belong_room, belong_project, accident_status, user, owner, location, purchase_date, eol_date, manufacturer, status, note) {
    editFlag = false;
    alert('撤回成功')
}

$(document).ready(function() {
    table = $('#mytable').DataTable( {
        "ajax": "/dashboard/table_device",
        "columns": [
            {"data": "type"},
            {"data": "form_type"},
            {"data": "series_id"},
            {"data": "property_id"},
            {"data": "server_type"},
            {"data": "cabinet_id"},
            {"data": "belong_cabinet"},
            {"data": "belong_room"},
            {"data": "belong_project"},
            {"data": null}
        ],
        "order": [[0, 'desc']],
        columnDefs: [
                {
                    targets: 9,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.type + "\', \'" + c.series_id + "\', \'" + c.property_id + "\', \'" + c.server_type + "\', \'" + c.cabinet_id + "\', \'" + c.belong_cabinet + "\', \'" + c.belong_room + "\', \'" + c.belong_project + "\')", "type": "primary"},
                                {"name": "撤回", "fn": "back(\'" + c.type + "\', \'" + c.series_id + "\', \'" + c.property_id + "\', \'" + c.server_type + "\', \'" + c.cabinet_id + "\', \'" + c.belong_cabinet + "\', \'" + c.belong_room + "\', \'" + c.belong_project + "\')", "type": "primary"},
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
    } );
     
    // 查看更多信息
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

    // 多选
    $('#mytable tbody').on( 'click', 'tr', function () {
        $(this).toggleClass('selected');
    } );
    //删除
    $('#bt-del').click( function () {
        if (table.row('.selected')[0].length == ''){
            alert('请选择')
        }
        else{
            if(confirm("您确定要执行删除操作吗？")){
                table.row('.selected').remove().draw( false );
            }else{
                return false;
            }
        }        
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
} );