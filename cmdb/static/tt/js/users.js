
var str = "确定删除用户?";
var count=0;

//预编译模板
var tpl = $("#tpl").html();

var template = Handlebars.compile(tpl);
var select2AddGroup;


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
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/users/get_user/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            $("#myModalLabel").text("修改用户信息");
            $("#modal-notify").hide();
            $("#id").val(id);
            $("#show_user_id").hide()
            $(".adjust").remove();
            $("#username").val(data.username).attr('disabled','disabled');
            $("#real_name").val(data.real_name);
            
            // !-- Add groups,multiple select!
            var group_info = $.parseJSON(data.group_info);
            $("#add_group").html('');
            var values = Array();
            group_info.forEach(function(value, i){
                $("#add_group").append('<option value="' + value[1] + '">' + value[0] + '</option>');
                values.push(value[1]);
                addBr();
            });
            $("#add_group").select2('val',values,true);
            // -- End

            if (data.is_superuser){
                $('input:radio[name="is_superuser"]').filter('[value="1"]').prop('checked', true);
            }else{
                $('input:radio[name="is_superuser"]').filter('[value="0"]').prop('checked', true);
            }

            
            $("#email").val(data.telphone);

            

            $("#myModal").modal("show");
        },
    });

};

function initModalSelect2(){
    // 初始化select2

    $select2AddGroup = $("#add_group").select2({
        ajax: {
            url: '/users/list_group/',
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
        placeholder: '选择分组',
        multiple: true,
        minimumResultsForSearch: Infinity,
    });

    $select2AddGroup;
    $select2AddGroup.on("select2:select", function(e){ adjustWithSelect2("select2:select",e); });
    $select2AddGroup.on("select2:unselect", function(e){ adjustWithSelect2("select2:unselect",e); });

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};


function addBeforeCheck(username,real_name,email){
    if (username == ''){
        $('#lb-msg').text('请输入用户名!');
        $('#modal-notify').show();
        return false;
    }

    if (real_name == ''){
        $('#lb-msg').text('请输入真实名!');
        $('#modal-notify').show();
        return false;
    }

    if (email == ''){
        $('#lb-msg').text('请输入电话!');
        $('#modal-notify').show();
        return false;
    }

    return true;
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
            'url': '/users/data_user/',
        },
        "columns": [
            {"data": null},
            {"data": 'id'},
            {"data": 'username'},
            {"data": 'real_name'},
            {"data": 'groups'},
            {"data": 'is_superuser'},
            {"data": 'telphone'},
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
                    targets: 7,
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

    initModalSelect2();

    $('#bt-add').click( function () {
        $("#myModalLabel").text("选择用户");
        $("#modal-notify").hide();
        $("#show_user_id").hide()
        $("#username").val('').attr('disabled', false);
        $("#real_name").val('');
        $('input:radio[name=is_superuser]').filter('[value=0]').prop('checked',true);
        $("#add_group").val('').trigger('change');
        $("#email").val('');
        $(".adjust").remove();
        editFlag=false;
        $("#myModal").modal("show");
    } );
    
    $('#bt-save').click( function(){
        var id = $("#id").val();
        var username = $("#username").val();
        var real_name = $("#real_name").val();

        var listGroupId = new Array();
        $("#add_group").select2('data').forEach(function(info,i){ listGroupId.push(info.id) });

        var is_superuser = $('input[name=is_superuser]:checked').val();
        var email = $("#email").val();
        

        if (!addBeforeCheck(username,real_name,email)){
            return false;
        };

        var inputIds = {
                'id': id,
                'username': username,
                'real_name': real_name,
                'listGroupId': listGroupId,
                'is_superuser': is_superuser,
                'email': email,
            };

        if (editFlag){
            var urls = "/users/edit_user/";
        }else{
            var urls = "/users/add_user/"
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
            }

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( inputIds );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/users/del_user/",
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
