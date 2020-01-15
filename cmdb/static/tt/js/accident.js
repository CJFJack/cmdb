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
var $select2Accident_type;
var $select2Dispose;
var $select2Sendback_hardware;
//预编译模板
var template = Handlebars.compile(tpl);

function formatRepo (repo) {
    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';
    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};

// function matchStart (term, text) {
//   if (text.toUpperCase().indexOf(term.toUpperCase()) == 0) {
//     return true;
//   }

//   return false;
// }

// $.fn.select2.amd.require(['select2/compat/matcher'], function (oldMatcher) {
//   $("#server").select2({
//     matcher: oldMatcher(matchStart)
//   })
// });

function initModalSelect2(){
    $select2Accident_type = $('#accident_type').select2({
        minimumResultsForSearch: Infinity,
    });
    $select2Dispose = $('#dispose').select2({
        minimumResultsForSearch: Infinity,
    });
    $select2Sendback_hardware = $('#sendback_hardware').select2({
        minimumResultsForSearch: Infinity,
    });
    $select2Server = $('#server').select2({
        ajax: {
            url: '/assets/list_devices',
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
                var serverList = $('#server').select2('data');
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
        // minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
};

function clearModalSelect2(){
    $select2Accident_type.select2("destroy");
    $select2Dispose.select2("destroy");
    $select2Sendback_hardware.select2("destroy");
    $select2Server.select2("destroy");
};

function addSelection(server){
    var data = server.split(',')
    for (var i = 0; i < data.length; i++) {
        $select2Server.append('<option value="'+data[i]+'">'+data[i]+'</option>');
    };
    
};

function edit(accident_number, occur_time, recover_time, accident_type, accident_reason, dispose, sendback_hardware, linkman, server, note) {
    editFlag = true;
    $("#myModalLabel").text("修改故障信息");
    $("#server").attr('disabled','true');
    $("#li_accident_number").removeClass("hide");
    $("#accident_number").val(accident_number).attr("disabled",'true');
    $("#occur_time").val(occur_time);
    $("#recover_time").val(recover_time);
    $("#accident_type").val(accident_type).trigger('change');
    $("#accident_reason").val(accident_reason);
    $("#dispose").val(dispose).trigger('change');
    $("#sendback_hardware").val(sendback_hardware).trigger('change');
    $("#linkman").val(linkman);
    $select2Server.html('');
    addSelection(server);
    values = server.split(',')
    $("#server").select2('val',values);
    $("#note").val(note);
    $("#modal-notify").hide();
    $("#myModal").modal("show");
}

// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });

$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "ajax": "/accident/data_tables",
        "columns": [
            {"data": null},
            {"data": "accident_number"},
            {"data": "occur_time"},
            {"data": "recover_time"},
            {"data": "accident_type"},
            {"data": "accident_reason"},
            {"data": "dispose"},
            {"data": "sendback_hardware"},
            {"data": "linkman"},
            {"data": "server"},
            {"data": "note"},
            {
                "data": null,
                "orderable": false,
            }
        ],
        "order": [[1, 'asc']],
        columnDefs: [
                {
                    'targets': 0,
                    'searchable':false,
                    'orderable':false,
                    'className': 'dt-body-center',
                    'render': function (data, type, full, meta){
                     return '<input type="checkbox">';
                    },
                },
                {
                    targets: 11,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.accident_number + "\', \'" + c.occur_time + "\', \'" + c.recover_time + "\', \'" + c.accident_type + "\', \'" + c.accident_reason + "\', \'" + c.dispose + "\', \'" + c.sendback_hardware + "\', \'" + c.linkman + "\', \'" + c.server + "\', \'" + c.note + "\')", "type": "primary"},
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
        // 'rowCallback': function(row, data, dataIndex){
        //     // If row ID is in list of selected row IDs
        //     if($.inArray(data[0], rows_selected) !== -1){
        //     $(row).find('input[type="checkbox"]').prop('checked', true);
        //     $(row).addClass('selected');
        //     }
        // },
    } );
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
        } else {
            $row.removeClass('selected');
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    // Handle click on table cells
    // $('#mytable tbody').on('click', 'td', function(e){
    //     $(this).parent().find('input[type="checkbox"]').trigger('click');
    // });

    $('#chb-all').on('click', function(e){
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function(i,n){
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked){
              $row.addClass('selected');
            }else{
              $row.removeClass('selected');
            }
        });

    });
    $('#occur_time').Zebra_DatePicker({
      pair: $('#recover_time')
    });
    $('#recover_time').Zebra_DatePicker({});
    initModalSelect2();
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
        var selected = [];
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function(i,n){
            var $row = $(this).closest('tr');
            if (n.checked){
                selected.push($row)
            }
        });
        if (selected.length == ''){
            alert('请选择服务器')
        }
        else{
            if(confirm("您确定要执行删除操作吗？")){
                var length=selected.length;
                var raw=[];
                for (var i=0; i<length; i++){
                    raw[i] = table.row(selected[i]).data()
                };
                var encoded=$.toJSON( raw );
                var pdata = encoded
                
                $.ajax({
                    type: "POST",
                    url: "/accident/data_del",
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
            }else{
                return false;
            }
        }
    } );
    $('#bt-add').click( function () {
        editFlag=false;
        $select2Server.html('');
        $select2Server.val(null).trigger('change');
        $("#server").removeAttr('disabled');
        $("#myModalLabel").text("增加故障信息");
        $("#li_accident_number").addClass("hide");
        $("#accident_number").val('');
        $("#occur_time").val('');
        $("#recover_time").val('');
        $("#accident_reason").val('');
        $("#linkman").val('');
        $("#server").val('');
        $("#note").val('');
        $("#modal-notify").hide();
        $("#myModal").modal("show");
    } );
    $('#file-save').click( function () {
        $("#Modal-file").modal("hide");
    } );
    $('#bt-input').click( function () {
        $("#Modal-file").modal("show");
    } );
    $('#bt-modal-notify').click( function () {
        $("#modal-notify").hide();
    } );
    $('#bt-save').click( function(){
        // var inputIds=$('#modal-list select,input').map(function(i,n){
        //     return $(n).val();
        // }).get();
        var serverList = $('#server').select2('data').map(function(i,n){
            return i.text;
        });
        
        var inputIds={
            "accident_number": $('#accident_number').val(),
            "occur_time": $('#occur_time').val(),
            "recover_time": $('#recover_time').val(),
            "accident_type": $('#accident_type').select2('data')[0].text,
            "accident_reason": $('#accident_reason').val(),
            "dispose": $('#dispose').select2('data')[0].text,
            "sendback_hardware": $('#sendback_hardware').select2('data')[0].text,
            "linkman": $('#linkman').val(),
            "server": serverList,
            "note": $('#note').val(),
        };
        var urls="/accident/data_add";
        var encoded=$.toJSON( inputIds );
        var pdata = encoded;
        if(editFlag){
            urls="/accident/data_edit"
        };
        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                
                if (data['data']) {
                    $("#myModal").modal("hide");
                    table.ajax.reload();
                }else{
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                };
            }
        });
    });
} );
