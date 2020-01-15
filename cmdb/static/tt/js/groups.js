
var str = "确定删除分组?";
var count=0;

//预编译模板
var tpl = $("#tpl").html();

var template = Handlebars.compile(tpl);
var select2AddUser;


function addBr(){
    // Add one <br class='adjust'> after a element id
    $("#show_ip_type").after("<br class='adjust'>");
};

function rmBr(){
    // Remove one <br class="adjust">
    $(".adjust")[0].remove();
};

function adjustWithSelect2(name, evt, className){
    //adjust with select2 multiple select
    if (name == "select2:select" || name == "select2:select2"){
        //var selectedCount = $("#attache_hosts").select2('data').length;
        addBr();
    }
    if (name == "select2:unselect"){
        rmBr();
    }
};


function edit(id) {
    window.location.href = "/users/group_info/?group_id=" + id;
};

function initModalSelect2(){
    // 初始化select2

    $select2AddUser = $("#add_user").select2({
        ajax: {
            url: '/users/list_users/',
            dataType: 'json',
            type: 'POST',
            //data: {'ip_type': 'PM','addition_id': selected_addtion_iptype},
            /*data: function(term, page){
                return {
                    'group_id': $("#group_id").val(),
                }
            },*/
            delay: 250,
            processResults: function (data, params) {
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
        placeholder: '选择用户',
        multiple: true,
        minimumResultsForSearch: Infinity,
    });

    $select2AddUser;
    $select2AddUser.on("select2:select", function(e){ adjustWithSelect2("select2:select",e); });
    $select2AddUser.on("select2:unselect", function(e){ adjustWithSelect2("select2:unselect",e); });

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};


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
        "ajax": {
            'type': 'GET',
            'url': '/users/data_groups_info/',
        },
        "columns": [
            {"data": null},
            {"data": 'id'},
            {"data": 'name'},
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
                    targets: 3,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "查看分组信息", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
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

    initModalSelect2();

    

    

    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增分组");
        $("#modal-notify").hide();
        $("#group_name").val('');
        //$("#add_user").val('').trigger('change');
        editFlag=false;
        $("#myModal").modal("show");
    } );
    
    $('#bt-save').click( function(){
        var group_name = $("#group_name").val();

        if (group_name == ''){
            $('#lb-msg').text('请输入分组名称');
            $('#modal-notify').show();
            return false;
        }

        var inputIds = {
                'group_name': group_name,
            };
        var urls = "/users/add_group/";

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
                }
                else{
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
            }
        });
    });

    //删除
    $("#bt-del").confirm({
        //text:"确定删除所选的vip?",
        confirm: function(button){
            var selected = getSelectedTable();

            var inputIds = {
                'listUserId': selected,
                'group_id': $("#group_id").val(),
            }

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( inputIds );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/users/del_group_user/",
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



} );
