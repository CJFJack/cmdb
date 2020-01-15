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