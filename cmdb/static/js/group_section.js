
var str = "确定删除改组用户?";
var count=0;

//预编译模板
var tpl = $("#tpl").html();

var template = Handlebars.compile(tpl);
var select2AddUser;


function initModalSelect2(){
    // 初始化select2

    $select2Leader = $("#leader").select2({
        ajax: {
            url: '/assets/list_user/',
            dataType: 'json',
            type: 'POST',
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
            cache: false,
        },
        // minimumResultsForSearch: Infinity,
    });

    $select2Allocate = $("#allocation").select2({
        ajax: {
            url: '/assets/list_project_group/',
            dataType: 'json',
            type: 'POST',
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
            cache: false,
        },
        // minimumResultsForSearch: Infinity,
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
        url: "/users/get_data_group_section/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            if (data.success){
                $("#myModalLabel").text("修改管理分组");
                $("#modal-notify").hide();
                $("#id").val(data.data.id);
                $("#show_id").hide()
                $("#name").val(data.data.name);
                initSelect2('leader', data.data.leader_id, data.data.leader_name);

                $("#allocation").html('');
                var values = new Array();
                data.data.allocation.forEach(function(e, i){
                    $("#allocation").append('<option value="' + e.id + '">' + e.name + '</option>');
                    values.push(e.id);
                });
                $("#allocation").select2('val', values);

                $("#myModal").modal("show");
            } else {
                alert(data.data);
            }
        },
    });
};

function formatRepo (repo) {
    
    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};


$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURIComponent(results[1]) || 0;
    }
}


$(document).ready(function() {
    var rows_selected = [];
    var group_id = $("#group_id").val();
    table = $('#mytable').DataTable( {
        "processing": true,
        "ordering": false,
        "ajax": {
            'type': 'POST',
            'url': '/users/data_group_section/',
            'data': function( d ){
                d.group_id = $.urlParam('group_id');
            }
        },
        "columns": [
            {"data": null},
            {"data": 'id'},
            {"data": 'group'},
            {"data": 'name'},
            {"data": 'leader'},
            {"data": 'users'},
            {"data": 'allocation'},
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
                    'targets': 4,
                    "render": function(data, type, row){
                        return '<a href="/users/user_list/?username=' + data + '">' + data + '</a>'
                    },
                },
                {    
                    'targets': 5,
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },
                {    
                    'targets': 6,
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },
                {
                    targets: 7,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "success"},
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
        $("#show_id").hide();
        initSelect2("leader", '0', '选择负责人')
        $("#name").val('');
        $("#allocation").html('')
        $("#allocation").val('').trigger('change')
        editFlag=false;
        $("#myModal").modal("show");
    } );
    
    $('#bt-save').click( function(){
        var id = $("#id").val();
        var group_id = $.urlParam('group_id');
        var name = $("#name").val();

        var leader = $("#leader").val();

        var allocation = $("#allocation").val()

        if ( name == '' ) {
            $('#lb-msg').text('请输入分组名称');
            $('#modal-notify').show();
            return false;
        }

        var inputIds = {
            'id': id,
            'group_id': group_id,
            'name': name,
            'leader': leader,
            'allocation': allocation,
            'editFlag': editFlag,
        }

        var encoded=$.toJSON( inputIds );
        var pdata = encoded;

        var urls = '/users/add_or_edit_group_section/';

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
            }
        });
    });

    $("#bt-del").confirm({
        //text:"确定删除所选的vip?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/users/del_group_section/",
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

    $("#reset_allocation").click(function(event) {
        /* Act on the event */
        $("#allocation").html('')
        $("#allocation").val('').trigger('change')
    });

} );
