
var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

// 修改之前的数据
var origin_data;

var str = "确定删除选中的svn仓库吗?";
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
        url: "/myworkflows/get_svn_repo/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改SVN仓库");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide();
            //console.log(roomid);
            $("#repo_name").val(data.name);
            $("#myModal").modal("show");
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
};


$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        //"serverSide": true,
        "ordering": false,
        "ajax": "/myworkflows/data_svn_repo",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "name"},
            {
              "data": null,
              "orderable": false,
            }
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
                    targets: 3,
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
                    url: "/myworkflows/del_svn_repo/",
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
                        }
                    },
                });
            }
        },

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    // 添加
    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增svn仓库");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#id").val('');
        $("#repo_name").val('');
        editFlag=false;
        $("#myModal").modal("show");
    } );
    
    $('#bt-save').click( function(){

        var id = $("#id").val();
        var repo_name = $('#repo_name').val();

        if (repo_name == ''){
            $('#lb-msg').text('请输入仓库名!');
            $('#modal-notify').show();
            return false;
        }

        var inputIds = {
          "id": id,
          "name": repo_name,
          "editFlag": editFlag,
        };

        var encoded=$.toJSON( inputIds )
        var pdata = encoded

        var urls = '/myworkflows/add_or_edit_repo/'

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                
                if (data['data']) {
                    table.ajax.reload(null, false);
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
