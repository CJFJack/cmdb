// 修改之前的数据
var origin_data;

var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的系统模板配置?";
var count=0;


function checkBeforeAdd(templatename,ostype,os_detail_name, business_type){
    if (templatename == ''){
        $('#lb-msg').text('请输入模板名称!');
        $('#modal-notify').show();
        return false;
    }
    if (business_type == ''){
        $('#lb-msg').text('请输入业务类型!');
        $('#modal-notify').show();
        return false;
    }
    if (ostype == ''){
        $('#lb-msg').text('请输入操作系统类型!');
        $('#modal-notify').show();
        return false;
    }
    if (os_detail_name == ''){
        $('#lb-msg').text('请输入操作系统详细!');
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
        url: "/assets/get_business_ostype/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改虚拟机配置");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide()
            $("#templatename").val(data.templatename);         
            $("#ostype").val(data.ostype);          
            $("#os_detail_name").val(data.os_detail_name);        
            $("#business_type").val(data.business_type);        
            $("#cpu").val(data.template_cpu);          
            $("#mem").val(data.template_mem);
            $("#disk").val(data.template_disk);          
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
        "ajax": "/assets/data_vmconf/",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "templatename"},
            {"data": "ostype"},
            {"data": "os_detail_name"},
            {"data": "business_type"},
            {"data": 'template_cpu'},
            {"data": 'template_mem'},
            {"data": 'template_disk'},
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
                    targets: 9,
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
                    url: "/assets/del_data_vmconf/",
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

    // 增加button
    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增操作系统模板");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#templatename").val('');
        $("#ostype").val('');
        $("#os_detail_name").val('');
        $("#business_type").val('');
        $("#cpu").val('');
        $("#mem").val('');
        $("#disk").val('');
        editFlag=false;
        $("#myModal").modal("show");
    } );
    $('#file-save').click( function () {
        $("#Modal-file").modal("hide");
    } );
    // $('#bt-export').click( function () {
    //     window.location.href()
    // } );
    $('#bt-upload').click( function () {
        $("#Modal-file").modal("show");
        $("#upload-notify").hide();
    } );
    $('#bt-upload-notify').click( function () {
        $("#upload-notify").hide();
    } );
    $('#bt-modal-notify').click( function () {
        $("#modal-notify").hide();
    } );
    $('#bt-save').click( function(){
        
        var id = $("#id").val();
        var templatename = $('#templatename').val();
        var ostype = $('#ostype').val();
        var os_detail_name = $('#os_detail_name').val();
        var business_type = $('#business_type').val();
        var cpu = $('#cpu').val();
        var mem = $('#mem').val();
        var disk = $('#disk').val();
        
        var inputIds = {
            'id': id,
            'templatename': templatename,
            'ostype': ostype,
            'os_detail_name': os_detail_name,
            'business_type': business_type,
            'template_cpu': cpu,
            'template_mem': mem,
            'template_disk': disk,
            "origin_data": origin_data,
        };

        if (editFlag){
            var urls = "/assets/edit_data_ostype/";
        }else{
            var urls = "/assets/add_data_ostype/";
        }

        if (!checkBeforeAdd(templatename,ostype,os_detail_name,business_type)){
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
    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });


} );
