
var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

// 修改之前的数据
var origin_data;

var str = "确定删除选中的机房?";
var count=0;

function checkBeforeAdd(roomname,roomid, address,contacts,contacts_tel,broad_band,line){
    if (roomname == ''){
        $('#lb-msg').text('请输入机房名!');
        $('#modal-notify').show();
        return false;
    }

    if (roomid == ''){
        $('#lb-msg').text('请输入机房序列号!');
        $('#modal-notify').show();
        return false;
    }else{
        if (roomid.length > 1){
            $('#lb-msg').text('机房序列号只能有一个长度');
            $('#modal-notify').show();
            return false;
        }
    }

    if (address == ''){
        $('#lb-msg').text('请输入地址!');
        $('#modal-notify').show();
        return false;
    }

    if (contacts == ''){
        $('#lb-msg').text('请输入联系人!');
        $('#modal-notify').show();
        return false;
    }

    if (contacts_tel == ''){
        $('#lb-msg').text('请输入联系人电话!');
        $('#modal-notify').show();
        return false;
    }

    if (broad_band == ''){
        $('#lb-msg').text('请输入宽带!');
        $('#modal-notify').show();
        return false;
    }

    if (line == ''){
        $('#lb-msg').text('请输入线路!');
        $('#modal-notify').show();
        return false;
    }

    return true;
};

function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_resource_room/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改机房信息");
            $("#modal-notify").hide();
            $("#roomid").val(data.id);
            $("#show_roomid").hide();
            //console.log(roomid);
            $("#roomname").val(data.roomname);
            $("#room_id").val(data.roomid);
            $("#address").val(data.address);
            $("#contacts").val(data.contacts);
            $("#contacts_tel").val(data.contacts_tel);
            $("#broad_band").val(data.broad_band);
            $("#line").val(data.line);
            $("#remarks").val(data.remarks);
            $("#myModal").modal("show");
        },
        error: function(data){
            alert('你没有修改基础资源权限');
        }
    });
};


$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        //"serverSide": true,
        "ajax": "/assets/data_room",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "roomname"},
            {"data": "roomid"},
            {"data": "address"},
            {"data": "contacts"},
            {"data": "contacts_tel"},
            {"data": "broad_band"},
            {"data": "line"},
            {"data": "remarks"},
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
                    targets: 10,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
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
            makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            makeTitle(str, --count);
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
              count = getSelectedTable().length;
              makeTitle(str, count);
            }else{
              $row.removeClass('selected');
              count = 0;
              makeTitle(str, count);
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
    $("#bt-del").confirm({
        //text:"确定删除所选的机房?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_room/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        
                        if (data['data']) {
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        }else{
                            alert(data['msg'])
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        };
                    }
                });
            }
        },

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    /*$('#bt-del').click( function () {
        var selected = new Array();
        table.rows('.selected').data().toArray().forEach(function(info,i){
            selected.push(info.roomid);
        });

        if (selected.length == 0){
            alert('请选择');
            return false;
        }
        else{
            $(this).confirm({
                text:"确定删除所选的" +selected.length + "机房?",

                confirm: function(button){
                    var encoded=$.toJSON( selected );
                    var pdata = encoded
                    $.ajax({
                        type: "POST",
                        url: "/assets/del_data_room/",
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
                },

                cancel: function(button){

                },
                confirmButton: "确定",
                cancelButton: "取消",
            });
        }
    } );*/

    // 添加
    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增机房信息");
        $("#modal-notify").hide();
        $("#show_roomid").hide();
        $("#roomname").val('').removeAttr("disabled");
        $("#room_id").val('');
        $("#address").val('').removeAttr("disabled");
        $("#contacts").val('');
        $("#contacts_tel").val('');
        $("#broad_band").val('');
        $("#line").val('');
        $("#remakrs").val('');
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

        var id = $("#roomid").val();
        var roomname = $('#roomname').val();
        var roomid = $('#room_id').val();
        var address = $('#address').val();
        var contacts = $('#contacts').val();
        var contacts_tel = $('#contacts_tel').val();
        var broad_band = $('#broad_band').val();
        var line = $('#line').val();
        var remarks = $('#remarks').val();

        var inputIds = {
          "id": id,
          "roomname": roomname,
          "roomid": roomid,
          "address": address,
          "contacts": contacts,
          "contacts_tel": contacts_tel,
          "broad_band": broad_band,
          "line": line,
          "remarks": remarks,
          "origin_data": origin_data,
        };

        var encoded=$.toJSON( inputIds )
        var pdata = encoded

        if (editFlag){
            var urls = "/assets/edit_data_room/";
        }else{
            var urls = "/assets/add_data_room/";
        }

        if (!checkBeforeAdd(roomname,roomid, address,contacts,contacts_tel,broad_band,line)){
            return false;
        }

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
