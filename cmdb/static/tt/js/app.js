// 修改之前的数据
var origin_data;

var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的应用类型?";
var count=0;

function addBeforeCheck(app_type,app_detail_type){
    if (app_type == ''){
        $('#lb-msg').text('app类型不能为空!');
        $('#modal-notify').show();
        return false;
    }

    if (app_detail_type == ''){
        $('#lb-msg').text('app分类不能为空!');
        $('#modal-notify').show();
        return false;
    }

    return true;
}

function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_business_apptype/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改机房信息");
            $("#modal-notify").hide();
            $("#apptype_id").val(data.id);
            $("#show_apptype_id").hide();          
            $("#app_type").val(data.app_type);         
            $("#app_detail_type").val(data.app_detail_type);          
            $("#myModal").modal("show");
        },
        error: function(data){
            alert('你没有修改平台应用权限');
        }
    });
}

function formatRepo (repo) {
    
    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};


// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });


$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ajax": "/assets/data_app",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": 'app_type'},
            {"data": 'app_detail_type'},
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
                    'targets': 1,
                    'visible': false,
                    'searchable': false
                },
                {
                    targets: 4,
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
                    url: "/assets/del_data_app/",
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

    // 增加button
    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增应用类型");
        $("#modal-notify").hide();
        $("#show_apptype_id").hide();
        $("#app_type").val('');
        $("#app_detail_type").val('');
        editFlag=false;
        $("#myModal").modal("show");
    } );

    $('#bt-save').click( function(){
        // 增加、修改保存
        var apptype_id = $("#apptype_id").val();
        var app_type = $("#app_type").val();
        var app_detail_type = $("#app_detail_type").val();
        
        var inputIds = {
            'apptype_id': apptype_id,
            'app_type': app_type,
            'app_detail_type': app_detail_type,
            "origin_data": origin_data,
        };
        
        if (editFlag){
            var urls = "/assets/edit_data_apptype/";
        }
        else{
            var urls = "/assets/add_data_apptype/";
        }

        if (!addBeforeCheck(app_type,app_detail_type)){
            return false;
        }

        var encoded=$.toJSON( inputIds );
        var pdata = encoded;
        
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
                $('#lb-msg').text('你没有增加平台业务的权限');
                $('#modal-notify').show();
            }
        });
    });


} );
