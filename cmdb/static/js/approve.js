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
var wrap = $("#wrap").html();
//预编译模板
var template = Handlebars.compile(tpl);
var template2 = Handlebars.compile(wrap);

function edit(type, series_id, property_id, server_type, cabinet_id, belong_cabinet, belong_room, belong_project, accident_status, user, owner, location, purchase_date, eol_date, manufacturer, status, note) {
    editFlag = true;
    $("#type").val(type).attr("disabled",'true');
    $("#series_id").val(series_id);
    $("#property_id").val(property_id);
    $("#server_type").val(server_type);
    $("#cabinet_id").val(cabinet_id);
    $("#belong_cabinet").val(belong_cabinet);
    $("#belong_room").val(belong_room);
    $("#belong_project").val(belong_project);
    $("#myModal").modal("show");
};

function back(type, series_id, property_id, server_type, cabinet_id, belong_cabinet, belong_room, belong_project, accident_status, user, owner, location, purchase_date, eol_date, manufacturer, status, note) {
    editFlag = false;
    alert('撤回成功')
};

$(document).on('hidden.bs.modal', function (e) {
    document.location.reload();
});

function detail(wf) {
    $.ajax({
          type: "POST",
          url: "/workflow/detail",
          data: wf, 
          success: function (data) {
            if (data['success']){
              if (data['form_type'] == "申请流程"){
                $('#belong_room').val(data['belong_room']);
                $('#name').val(data['name']);
                if (data.hasOwnProperty('for_project')){
                  $('#project').val(data['for_project'].text);
                }
                $('#server_name').val(data['server_name']);
                $('#network_bandwidth').val(data['network_bandwidth']);
                $('#start_time').val(data['start_time']);
                $('#harddrive').val(data['harddrive']);
                $('#number').val(data['number']);
                $('#proposer').val(data['proposer']);
                $('#reason').val(data['reason']);
                $('#memory').val(data['memory']);
                $('#cpu').val(data['cpu']);
                $('#resource_type').val(data['resource_type']);
                $('#detail-approve').removeClass('hide');
                for (var i=0;i<data['servers'].length;i++)
                {
                    var inputbox = '<input type="text" style="width:100%" class="form-control" value="'+data['servers'][i]+'">'
                    $("#div-servers-app").append(inputbox);
                };
                for (var i=0;i<data['options'].length;i++)
                {
                  
                  var option = "<li class=\"form-group\"><label class=\"col-md-3 control-label\" for=\"option\">审批意见</label><div class=\"col-md-7\"><textarea class=\"form-control\" disabled=\"true\" type=\"text\">"+data['options'][i][0]+"</textarea></div></li>"+"<li class=\"form-group\"><label class=\"col-md-3 control-label\" for=\"reason\">审批状态</label><div class=\"col-md-7\"><input class=\"form-control\" disabled=\"true\" type=\"text\"value=\""+data['options'][i][1]+"\"></div></li>"+"<li class=\"form-group\"><label class=\"col-md-3 control-label\" for=\"reason\">审批通过时间</label><div class=\"col-md-7\"><input class=\"form-control\" disabled=\"true\" type=\"text\"value=\""+data['options'][i][2]+"\"></div></li>"
                  $('#detail-approve').append(option)
                };
                $('#detailModal').modal('show');
              };
              if (data['form_type'] == "退还流程"){
                $("#return-name").val(data['name']);
                $("#return-proposer").val(data['proposer']);
                $("#return-start_time").val(data['start_time']);
                // $("#return_server").val(data['return_server']);
                for (var i=0;i<data['return_server'].length;i++)
                {
                    var inputbox = '<input type="text" disabled="true" class="form-control" value="'+data['return_server'][i]+'">'
                    $("#div-servers").append(inputbox);
                };
                $("#r_project").val(data['project_text']);
                $('#detail-return').toggleClass('hide');
                for (var i=0;i<data['options'].length;i++)
                {
                  
                  var option = "<li class=\"form-group\"><label class=\"col-md-3 control-label\" for=\"option\">审批意见</label><div class=\"col-md-7\"><textarea class=\"form-control\" disabled=\"true\" type=\"text\">"+data['options'][i][0]+"</textarea></div></li>"+"<li class=\"form-group\"><label class=\"col-md-3 control-label\" for=\"reason\">审批状态</label><div class=\"col-md-7\"><input class=\"form-control\" disabled=\"true\" type=\"text\"value=\""+data['options'][i][1]+"\"></div></li>"+"<li class=\"form-group\"><label class=\"col-md-3 control-label\" for=\"reason\">审批通过时间</label><div class=\"col-md-7\"><input class=\"form-control\" disabled=\"true\" type=\"text\"value=\""+data['options'][i][2]+"\"></div></li>"
                  $('#detail-return').append(option)
                };
                $('#detailModal').modal('show');
              };
            }else{
              alert(data['msg']);
            }
          }
        });
};

$(document).ready(function() {
    table = $('#mytable').DataTable( {
        "ajax": "/workflow/table_approveflow",
        "columns": [
            // {"data": "wf_name"},
            {"data": "form_type"},
            {"data": "proposer"},
            {"data": "approver"},
            {"data": "status"},
            {"data": "reach_time"},
            {"data": "finish_time"},
            {"data": "project"},
            {"data": "number"},
            {"data": "servers"},
            {"data": "ip"},
            {"data": "name"},
            {"data": null},
        ],
        "order": [[5, 'desc']],
        "language": {
               "url": "/static/js/i18n/Chinese.json"
        },
        columnDefs: [
                {
                    targets: 11,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "详细", "fn": "detail(\'" + c.wf_name + "\')", "type": "primary"},
                            ]
                        };
                        var html = template(context);
                        return html;
                    }
                },
                {
                    targets: 10,
                    render: function (a, b, c, d) {
                        console.log(a,b,c,d);
                        var context =
                        {
                            func: [
                                {"values": a},
                            ]
                        };
                        var html = template2(context);
                        return html;
                    }
                }
        ],
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
    // $('#mytable tbody').on( 'click', 'tr', function () {
    //     $(this).toggleClass('selected');
    // } );
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