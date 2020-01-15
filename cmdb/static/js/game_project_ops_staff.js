
var str = "确定删除分组?";
var count=0;

//预编译模板
var tpl = $("#tpl").html();

var template = Handlebars.compile(tpl);

var $select2Project;
var $select2RelatedUsers;

function initModalSelect2(){
    // 初始化select2

    $select2RelatedUsers = $("#related_user").select2({
        ajax: {
            url: '/assets/list_ops_user/',
            dataType: 'json',
            type: 'POST',
            /*data: function(term, page){
                return {
                    'ip_type': 'VIP',
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
        placeholder: '选择运维对接人员',
        multiple: true,
        minimumResultsForSearch: Infinity,
        //escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        //templateResult: formatRepo, // omitted for brevity, see the source of this page
        //templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });  

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};



function group_of_users(id) {
    // 分组的用户
    window.location.href = "/users/group_info/?group_id=" + id;
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
        url: "/assets/get_game_project_related_user/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            $("#id").val(data.id);
            $("#show_id").hide();

            $("#project").val(data.project_name);

            // 重新填充select2
            $("#related_user").val('').trigger('change');
            $("#related_user").html('');

            var values = new Array();
            data.related_user.forEach(function(e, i){
                $("#related_user").append('<option value="' + e.id + '">' + e.username + '</option>');
                values.push(e.id);
            });
            $("#related_user").select2('val', values);

            $("#modal-notify").hide();
            $("#myModal").modal("show");
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



$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ordering": false,
        "ajax": '/assets/data_game_project_ops_staff/',
        "columns": [
            {"data": null},
            {"data": 'id'},
            {"data": 'project'},
            {"data": 'related_user'},
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
    });

    initModalSelect2();

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

    /*$('#bt-add').click( function () {
        $("#myModalLabel").text("新增部门");
        $("#modal-notify").hide();
        $("#id").val('');
        $("#show_id").hide();
        $("#name").val('');
        initSelect2("group_leader", '0', '选择负责人');
        $('input:radio[name=is_public]').filter('[value=false]').prop('checked',true);
        //$("#add_user").val('').trigger('change');
        editFlag=false;
        $("#myModal").modal("show");
    } );*/
    
    $('#bt-save').click( function(){
        var id = $("#id").val();
        var related_user = $("#related_user").val();    // ["id1", "id2", "id3"]

        var inputIds = {
                'id': id,
                'related_user': related_user,
                'editFlag': editFlag,
            };
        var urls = "/assets/add_or_edit_game_project_related_user/";

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

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/users/del_group/",
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
