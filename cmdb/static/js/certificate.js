// 修改之前的数据
var origin_data;


var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的证书?";
var count=0;



function formatRepo (repo) {
    // if (repo.loading) return repo.text;

    // var markup = '<div class="clearfix">' +
    // '<div class="col-sm-1">' +
    // '<img src="' + repo.owner.avatar_url + '" style="max-width: 100%" />' +
    // '</div>' +
    // '<div clas="col-sm-10">' +
    // '<div class="clearfix">' +
    // '<div class="col-sm-6">' + repo.full_name + '</div>' +
    // '<div class="col-sm-3"><i class="fa fa-code-fork"></i> ' + repo.forks_count + '</div>' +
    // '<div class="col-sm-2"><i class="fa fa-star"></i> ' + repo.stargazers_count + '</div>' +
    // '</div>';

    // if (repo.description) {
    //   markup += '<div>' + repo.description + '</div>';
    // }

    // markup += '</div></div>';
    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};


function saveBeforeCheck(certificate_name, expire_date, person_in_charge){
    if (certificate_name == ''){
        $('#lb-msg').text('证书名不能为空!');
        $('#modal-notify').show();
        return false;
    }

    if (expire_date == ''){
        $('#lb-msg').text('到期时间不能为空!');
        $('#modal-notify').show();
        return false;
    }

    if (person_in_charge == ''){
        $('#lb-msg').text('负责人不能为空!');
        $('#modal-notify').show();
        return false;
    }

    return true;

};

function edit(id) {

    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_business_certificate/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            editFlag = true;
            origin_data = data;
            $("#myModalLabel").text("修改机柜信息");
            $("#modal-notify").hide();
            $("#id").val(id);
            $("#show_id").hide();

            $("#certificate_name").val(data.certificate_name);
            $("#expire_date").val(data.expire_date);
            $("#person_in_charge").val(data.person_in_charge);
            $("#myModal").modal("show");
        }
    });
}

$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ajax": "/assets/data_certificate",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": 'certificate_name'},
            {"data": "expire_date"},
            {"data": "person_in_charge"},
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
                    targets: 5,
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

    $('#expire_date').Zebra_DatePicker({
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


    
    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增机柜信息");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#certificate_name").val('');
        $("#expire_date").val('');
        $("#person_in_charge").val('');
        editFlag=false;
        $("#myModal").modal("show");
    } );
    $('#file-save').click( function () {
        $("#Modal-file").modal("hide");
    } );
    // $('#bt-input').click( function () {
    //     $("#Modal-file").modal("show");
    // } );
    $('#bt-modal-notify').click( function () {
        $("#modal-notify").hide();
    } );
    $('#bt-save').click( function(){

        var id=$("#id").val();
        var certificate_name = $("#certificate_name").val();
        var expire_date = $("#expire_date").val();
        var person_in_charge = $("#person_in_charge").val();

        if (!saveBeforeCheck(certificate_name, expire_date, person_in_charge)){
            return false;
        }

        var inputIds = {
            'id': id,
            'certificate_name': certificate_name,
            'expire_date': expire_date,
            'person_in_charge': person_in_charge,
            "origin_data": origin_data,
        };

        if (editFlag){
            var urls="/assets/edit_data_certificate/";
        }else{
            var urls="/assets/add_data_certificate/";
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
                $('#lb-msg').text('你没有增加基础资源权限');
                $('#modal-notify').show();
            }
        });
    });

    // 删除
    $("#bt-del").confirm({
        //text:"确定删除所选的机柜?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_certificate/",
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
});
