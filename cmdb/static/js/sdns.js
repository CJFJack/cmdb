// 修改之前的数据
var origin_data;

var table;
var editFlag;
//预编译模板
var tpl = $("#tpl").html();

var str = "确定删除选中的DNS?";
var count=0;

var template = Handlebars.compile(tpl);

var $select2IpBinding;



function initModalSelect2(){
    // 初始化select2

    $select2IpBinding = $('#ip_binding').select2( {
        ajax: {
            url: '/assets/list_vip/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function(params, page){
                return {
                    'ip_type': 'VIP',
                    q: params.term,
                    //'addition_id': selected_addtion_iptype
                }
            },
            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function(item){
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: true,
        },
        placeholder: '绑定vip',
        multiple: true,
    });

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};


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
        url: "/assets/get_business_sdns/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
                origin_data = data;
                $("#myModalLabel").text("修改智能DNS");
                $("#modal-notify").hide();
                
                $("#id").val(data.id);
                $("#show_id").hide();

                $("#dnsname").val(data.dnsname);


                
                var vip_info = $.parseJSON(data.vip_info);
                $("#ip_binding").html('');
                // 记录vip的id
                var values = Array();
                vip_info.forEach(function(value, i){
                    $("#ip_binding").append('<option value="' + value[1] + '">' + value[0] + '</option>');
                    values.push(value[1]);
                });
                $("#ip_binding").select2('val',values,true);

                

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

function addBeforeCheck(dnsname){
    if (dnsname == ''){
        $('#lb-msg').text('请输入DNS名称!');
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
        "ajax": "/assets/data_sdns/",
        "columns": [
            {"data": null},
            {"data": 'id'},
            {"data": 'dnsname'},
            {"data": 'ip_binding'},
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
                    'targets': 3,
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },
                {
                    targets: 4,
                    "width": "8%",
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\', \'" + c.application_name + "\')", "type": "primary"},
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

    initModalSelect2();

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
        var dnsname = $("#dnsname").val();

        var ip_binding = $("#ip_binding").select2('data');
        var vip_ids = Array();
        for (i=0; i<ip_binding.length; i++){
            vip_ids.push(ip_binding[i].id)
        }

        var inputIds = {
            'id': id,
            'dnsname': dnsname,
            'vip_ids': vip_ids,
            "origin_data": origin_data,
        }

        if (!addBeforeCheck(dnsname)){
            return false;
        };
        
        if (editFlag){
            var urls = "/assets/edit_data_sdns/"
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