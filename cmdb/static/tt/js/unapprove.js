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
var selected_flowname
function edit(name, prenode, proposer, reason, time, nextnode,type) {
    selected_flowname = name;
    if (type == '退还流程'){
        $('#c_servers').addClass('hide');
    };
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
            for (var i=0;i<data['options'].length;i++)
            {
              
              var option = "<li class=\"form-group\"><label class=\"col-md-3 control-label\" for=\"option\">审批意见</label><div class=\"col-md-7\"><textarea class=\"form-control\" disabled=\"true\" type=\"text\">"+data['options'][i][0]+"</textarea></div></li>"+"<li class=\"form-group\"><label class=\"col-md-3 control-label\" for=\"reason\">审批状态</label><div class=\"col-md-7\"><input class=\"form-control\" disabled=\"true\" type=\"text\"value=\""+data['options'][i][1]+"\"></div></li>"
              $('#detail-approve').append(option)
            };
            $('#detailModal').modal('show');
          }
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
              
              var option = "<li class=\"form-group\"><label class=\"col-md-3 control-label\" for=\"option\">审批意见</label><div class=\"col-md-7\"><textarea class=\"form-control\" disabled=\"true\" type=\"text\">"+data['options'][i][0]+"</textarea></div></li>"+"<li class=\"form-group\"><label class=\"col-md-3 control-label\" for=\"reason\">审批状态</label><div class=\"col-md-7\"><input class=\"form-control\" disabled=\"true\" type=\"text\"value=\""+data['options'][i][1]+"\"></div></li>"
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

function formatRepo (repo) {
    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';
    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};

$select2Server = $('#servers').select2({
    ajax: {
        url: '/assets/list_approve',
        dataType: 'json',
        delay: 250,
        data: function (params) {
            return params
        },
        processResults: function (data, params) {
            // parse the results into the format expected by Select2
            // since we are using custom formatting functions we do not need to
            // alter the remote JSON data, except to indicate that infinite
            // scrolling can be used
            params.page = params.page || 1;
            // var selectedData = $.map(serverList, function(item,i){
            //     return {
            //         id: i+1,
            //         text: item
            //     }
            // });
            
            var ret = $.map(data, function(item){
                return {
                    id: item.id,
                    text: item.text
                }
            });
            return {
                results: ret
              // pagination: {
              //     more: (params.page * 30) < data.total_count
              // };
            }
        },
       
        cache: true,
    },
    minimumResultsForSearch: Infinity,
    escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
    // minimumInputLength: 1,
    templateResult: formatRepo, // omitted for brevity, see the source of this page
    templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
});

$(document).ready(function() {
    table = $('#mytable').DataTable( {
        "ajax": "/workflow/table_unapproveflow",
        "columns": [
            // {"data": "name"},
            {"data": "form_type"},
            {"data": "prenode"},
            {"data": "proposer"},
            {"data": "reason"},
            {"data": "time"},
            {"data": "nextnode"},
            {"data": "project"},
            {"data": "number"},
            {"data": "servers"},
            {"data": null}
        ],
        "order": [[4, 'desc']],
        columnDefs: [
                {
                    targets: 9,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "审批", "fn": "edit(\'" + c.name + "\', \'" + c.prenode + "\', \'" + c.proposer + "\', \'" + c.reason + "\', \'" + c.time + "\', \'" + c.nextnode + "\', \'" + c.form_type + "\')", "type": "primary"},
                                {"name": "详细", "fn": "detail(\'" + c.name + "\')", "type": "primary"},
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
        var servers = '';
        if ($('#servers').select2('data') != ''){
            servers = $('#servers').select2('data').map(function(i,n){
                return i.text;
            });
        }
        var data={
            'workflow_name': selected_flowname,
            'option': $('#notes').val(),
            'pass': $('input[type="radio"]:checked').val(),
            'servers': servers,
        }
        var pdata = $.toJSON( data );
        $.ajax({
            type: "POST",
            url: "/workflow/transition_done",
            contentType: "application/json; charset=utf-8",
            data: pdata, 
            success: function (data) {
                if (data['success']){
                    table.ajax.reload();
                    $("#myModal").modal("hide");
                }else{
                    alert(data['msg'])
                };
            }
        });
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
                table.ajax.reload();
                // table.row.add(data).draw();
                $("#myModal").modal("hide");
                // $("#myModalLabel").text("新增");
                // clear();
                // 
            }
        });
    });
} );