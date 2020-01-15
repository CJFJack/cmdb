/*function format ( d ) {
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
}*/
var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

function edit(name, address, contacts, contacts_tel, broad_band, line) {
    editFlag = true;
    $("#myModalLabel").text("修改机房信息");
    $("#modal-notify").hide();
    $("#roomid").hide();
    $("#roomname").val(name).attr("disabled",'true');
    $("#address").val(address).attr("disabled",'true');
    $("#contacts").val(contacts);
    $("#contacts_tel").val(contacts_tel);
    $("#broad_band").val(broad_band);
    $("#line").val(line);
    $("#myModal").modal("show");
}

$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        //"serverSide": true,
        'ordering': false,
        "ajax": "/assets/data_room",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "roomname"},
            {"data": "address"},
            {"data": "contacts"},
            {"data": "contacts_tel"},
            {"data": "broad_band"},
            {"data": "line"},
        ],
        "order": [[2, 'asc']],
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
                    'targets': 1,
                    'visible': false,
                    'searchable': false
                },
                {
                    targets: 8,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.roomname + "\', \'" + c.address + "\', \'" + c.contacts + "\', \'" + c.contacts_tel + "\', \'" + c.broad_band + "\', \'" + c.line + "\')", "type": "primary"},
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

    /*$('#start_time').Zebra_DatePicker({
        pair: $('#end_time')
    });*/
    /*$('#end_time').Zebra_DatePicker({
        direction: 1,
    });*/
    // 查看更多信息
    /*$('#mytable tbody').on('click', 'td.details-control', function () {
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
    } );*/

    // 多选
    // $('#mytable tbody').on( 'click', 'tr', function () {
    //     $(this).toggleClass('selected');
    // } );
    //删除
    /*$('#bt-del').click( function () {
        var selected = [];
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function(i,n){
            var $row = $(this).closest('tr');
            if (n.checked){
                selected.push($row)
            }
        });
        if (selected.length == ''){
            alert('请选择')
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
                    url: "/assets/data_del_idc",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        
                        if (data['data']) {
                            table.ajax.reload();
                        }else{
                            alert(data['msg'])
                            table.ajax.reload();
                        };
                    }
                });
            }else{
                return false;
            }
        }
    } );*/
    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增机房信息");
        $("#modal-notify").hide();
        $("#roomid").hide();
        $("#roomname").val('').removeAttr("disabled");
        $("#address").val('');
        $("#contacts").val('');
        $("#contacts_tel").val('');
        $("#broad_band").val('');
        $("#line").val('');
        editFlag=false;
        $("#myModal").modal("show");
    } );
    /*$('#submit-file-formsss').on('submit', function(e){
        
        e.preventDefault();
        var pdata = new FormData($('#submit-file-form').get(0))
        $.ajax({
            url: '/assets/upload_idc', //this is the submit URL
            type: 'POST', //or POST
            data: pdata,
            success: function(data){
                if (data['data']){
                    $('#upload-notify').addClass("alert-success")
                    $('#upload-notify').show()
                    $('#lb-msg-upload').text('上传成功')
                }
                else{
                    $('#upload-notify').addClass("alert-danger")
                    $('#upload-notify').show()
                    $('#lb-msg-upload').text(data['msg'])
                }
            }
        });
    } );*/
    // $('#bt-input').click( function () {
    //     $("#Modal-file").modal("show");
    // } );
    /*$('#bt-upload').click( function () {
        $("#Modal-file").modal("show");
        $("#upload-notify").hide();
    } );*/
    /*$('#bt-upload-notify').click( function () {
        $("#upload-notify").hide();
    } );*/
    /*$('#bt-modal-notify').click( function () {
        $("#modal-notify").hide();
        $("#upload-notify").hide();
    } );*/
    $('#bt-save').click( function(){
        // var inputIds=$('#modal-list input').map(function(i,n){
        //     return $(n).val();
        // }).get();
        var inputIds = {
          "roomname": $('#roomname').val(),
          "address": $('#address').val(),
          "contacts": $('#contacts').val(),
          "contacts_tel": $('#contacts_tel').val(),
          "broad_band": $('#broad_band').val(),
          "line": $('#line').val(),
        };
        var urls="/assets/add_data_room/";
        var encoded=$.toJSON( inputIds )
        var pdata = encoded
        if(editFlag){
            urls="/assets/data_edit_idc"
        };
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
            }
        });
    });
} );
