var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

function edit(type, series_id, property_id, server_type, cabinet_id, belong_cabinet) {
    
    editFlag = true;
    $("#editModalLabel").text("修改设备信息");
    $("#edit-name").val(type);
    $("#edit-ip").val(series_id);
    $("#edit-status").val(property_id);
    $("#edit-cpu").val(server_type);
    $("#edit-memory").val(cabinet_id);
    $("#edit-harddrive").val(belong_cabinet);
    $("#editModal").modal("show");
}

$(document).ready(function() {
    table = $('#projectable').DataTable( {
        "ajax": "/dashboard/project_data",
        "columns": [
            {"data": "bname"},
            {"data": "series_id"},
            {"data": "property_id"},
            {"data": "server_type"},
            {"data": "cabinet_id"},
            {"data": "belong_cabinet"},
            {"data": null}
        ],
        "order": [[0, 'asc']],
        columnDefs: [
                {
                    targets: 6,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.bname + "\', \'" + c.series_id + "\', \'" + c.property_id + "\', \'" + c.server_type + "\', \'" + c.cabinet_id + "\', \'" + c.belong_cabinet + "\')", "type": "primary"},
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
    // $('#projectable tbody').on('click', 'td.details-control', function () {
    //     var tr = $(this).closest('tr');
    //     var row = table.row( tr );
 
    //     if ( row.child.isShown() ) {
    //         // This row is already open - close it
    //         row.child.hide();
    //         tr.removeClass('shown');
    //     }
    //     else {
    //         // Open this row
    //         row.child( format(row.data()) ).show();
    //         tr.addClass('shown');
    //     }
    // } );

    // 多选
    $('#projectable tbody').on( 'click', 'tr', function () {
        $(this).toggleClass('selected');
    } );
    //删除
    $('#bt-del').click( function () {
        if (table.row('.selected')[0].length != 0){
            if(confirm("您确定要执行删除操作吗？")){
                table.row('.selected').remove().draw( false );
            }else{
                return false;
            }
        }
        else{
            alert('请选择服务器')
        }
    } );
    $('#bt-add').click( function () {
        editFlag=false;
        $("#myModal").modal("show");
    } );
    $('#bt-save').click( function(){
        if(editFlag){
            //发送修改数据
        };
        var inputIds=$('#modal-list input').map(function(i,n){
            return $(n).val();
        }).get();
        
        $("#myModal").modal("hide");
        
    });
    $('#bt-esave').click( function(){
        $("#editModal").modal("hide");        
    });
} );