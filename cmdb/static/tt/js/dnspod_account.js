// 修改之前的数据
var origin_data;

var table;
var editFlag;
//预编译模板
var tpl = $("#tpl").html();

var str = "确定删除选中的DNS?";
var count=0;

var template = Handlebars.compile(tpl);


function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_dnspod_dnspod_account/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
                origin_data = data;
                $("#myModalLabel").text("修改信息");
                $("#modal-notify").hide();
                
                $("#id").val(data.id);
                $("#show_id").hide();

                $("#service_type").val(data.service_type);
                $("#service_detail").val(data.service_detail);

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

function addBeforeCheck(service_type, service_detail){
    if (service_type == ''){
        $('#lb-msg').text('请输入服务类型!');
        $('#modal-notify').show();
        return false;
    }

    if (service_detail == ''){
        $('#lb-msg').text('请输入服务详细!');
        $('#modal-notify').show();
        return false;
    }
    
    return true;
};



$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "autoWidth": true,
        "ajax": "/assets/data_dnspod_account/",
        "columns": [
            {"data": null},
            {"data": 'id'},
            {"data": 'service_type'},
            {"data": 'service_detail'},
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

    // initModalSelect2();

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
        //text:"确定删除所选的服务?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_sdns/",
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
        $("#show_id").hide();
        $("#dnsname").val('');
        $("#ip_binding").val('').trigger("change");

        $("#myModalLabel").text('新增智能DNS');
        $("#modal-notify").hide();
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
        // 增加、修改保存
        var id = $("#id").val();
        var service_type = $("#service_type").val();
        var service_detail = $("#service_detail").val();

        var inputIds = {
            'id': id,
            'service_type': service_type,
            'service_detail': service_detail,
        }

        if (!addBeforeCheck(service_type, service_detail)){
            return false;
        };
        
        if (editFlag){
            var urls = "/assets/edit_data_dnspod_account/"
        }
        else{
            var urls = "/assets/add_data_sdns/"
        };

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

});