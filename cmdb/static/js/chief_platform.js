// 修改之前的数据
var origin_data;

var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);


var str = "确定删除选中的主平台?";
var count=0;

function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_business_chief_platform/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改主平台");
            $("#modal-notify").hide();
            $("#show_id").hide();
            $("#id").val(data.id);
            $("#chief_platform_name").val(data.chief_platform_name);
            $("#company").val(data.company);
            $("#manager").val(data.manager); 
            $("#manager_tel").val(data.manager_tel);
            $("#developer").val(data.developer);        
            $("#developer_tel").val(data.developer_tel);
            $("#myModal").modal("show");
        },
        error: function(data){
            alert('你没有修改平台业务权限');
        }
    });
};


$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        //"serverSide": true,
        "ajax": "/assets/data_chief_platform",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "chief_platform_name"},
            {"data": "company"},
            {"data": "manager"},
            {"data": "manager_tel"},
            {"data": "developer"},
            {"data": "developer_tel"},
            {"data": null},
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
                    url: "/assets/del_data_chief_platform/",
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
        $("#myModalLabel").text("新增主平台");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#chief_platform_name").val('');
        $("#company").val('');
        $("#manager").val('');
        $("#manager_tel").val('');
        $("#developer").val('');
        $("#developer_tel").val('');
        editFlag=false;
        $("#myModal").modal("show");
    } );
    
    $('#bt-save').click( function(){

        var id = $("#id").val();
        var chief_platform_name = $("#chief_platform_name").val();
        var company = $("#company").val();
        var manager = $("#manager").val();
        var manager_tel = $("#manager_tel").val();
        var developer = $("#developer").val();
        var developer_tel = $("#developer_tel").val();
        
        if (chief_platform_name==''){
            $('#lb-msg').text('请输入主平台名称!');
            $('#modal-notify').show();
            return false;
        }

        if (company==''){
            $('#lb-msg').text('请输入公司名!');
            $('#modal-notify').show();
            return false;
        }

        var inputIds = {
            'id': id,
            'chief_platform_name': chief_platform_name,
            'company': company,
            'manager': manager,
            'manager_tel': manager_tel,
            'developer': developer,
            'developer_tel': developer_tel,
            "origin_data": origin_data,
        };

        
        if (editFlag){
            var urls = "/assets/edit_data_chief_platform/";
        }
        else{
            var urls = "/assets/add_data_chief_platform/";
        }

        
        var encoded=$.toJSON( inputIds )
        var pdata = encoded
        
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
