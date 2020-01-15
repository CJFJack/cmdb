
var str = "确定删除改组用户?";
var count=0;

//var template = Handlebars.compile(tpl);
var select2AddUser;


function initModalSelect2(){
    // 初始化select2

    $select2AddUser = $("#add_user").select2({
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
        placeholder: '选择用户',
        multiple: true,
        minimumResultsForSearch: Infinity,
    });

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

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
        "ajax": {
            'type': 'POST',
            'url': '/users/data_group_info/',
            'data': function( d ){
                d.group_id = $.urlParam('group_id');
            }
        },
        "columns": [
            {"data": null},
            {"data": 'id'},
            {"data": 'username'},
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
        $("#add_user").val('').trigger('change');
        editFlag=false;
        $("#myModal").modal("show");
    } );
    
    $('#bt-save').click( function(){
        var group_id = $.urlParam('group_id');

        var listUserId = new Array();
        var selectedUsers = $("#add_user").select2('data');

        selectedUsers.forEach(function(info, i){ listUserId.push(info.id) });

        var inputIds = {
            'group_id': group_id,
            'listUserId': listUserId
        }

        var encoded=$.toJSON( inputIds );
        var pdata = encoded;

        var urls = '/users/add_group_user/';

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

    //删除
    $("#bt-del").confirm({
        //text:"确定删除所选的vip?",
        confirm: function(button){
            var selected = getSelectedTable();

            var inputIds = {
                'listUserId': selected,
                'group_id': $.urlParam('group_id'),
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
