
var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

// 修改之前的数据
var origin_data;

var str = "确定删除选中的供应商?";
var count=0;


function initModelSelect2() {
    $select2Applicant = $("#leader").select2({
        ajax: {
            url: '/assets/list_user/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                    };
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
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}


function checkBeforeAdd(name, code){
    if (name == ''){
        $('#lb-msg').text('请输入公司名!');
        $('#modal-notify').show();
        return false;
    }
    if (code == ''){
        $('#lb-msg').text('请输入公司代号!');
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
        url: "/it_assets/get_company_code/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改供应商");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide();
            $("#name").val(data.name);
            $("#code").val(data.code);
            $("#myModal").modal("show");
            initSelect2("leader", data.leader_id, data.leader);
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


/*function initModalSelect2(){
    $select2_status = $("#status").select2({
        minimumResultsForSearch: Infinity,
    });
};*/

$(document).ready(function() {

    initModelSelect2();

    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        //"serverSide": true,
        "ordering": false,
        "ajax": "/it_assets/data_company_code/",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "name"},
            {"data": "code"},
            {"data": "leader"},
            {
              "data": null,
              "orderable": false,
            }
        ],
        // "order": [[2, 'asc']],
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
    } );

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
                    url: "/it_assets/del_data_company_code/",
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
                    },
                    error: function (xhr, status, error) {
                        if (xhr.status == '403') {
                            alert('权限拒绝');
                        } else {
                            alert('内部错误');
                        }
                    }
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
        $("#myModalLabel").text("新增公司代号");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#name").val('');
        $("#code").val('');
        initSelect2('leader', '0', '请选择领导');
        editFlag=false;
        $("#myModal").modal("show");
    } );
    
    $('#bt-save').click( function(){

        var id = $("#id").val();
        var name = $("#name").val();
        var code = $("#code").val();
        var leader = $("#leader").val();

        var inputIds = {
            "id": id,
            "name": name,
            "code": code,
            "leader": leader,
            "editFlag": editFlag,
        };

        var encoded=$.toJSON( inputIds )
        var pdata = encoded

        urls = '/it_assets/add_or_edit_company_code/';

        if (!checkBeforeAdd(name, code)){
            return false;
        }

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
            }
        });
    });
} );
