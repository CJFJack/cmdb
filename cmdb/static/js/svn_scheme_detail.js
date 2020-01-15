
var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

// 修改之前的数据
var origin_data;

var str = "确定删除选中的方案明细?";
var count=0;

var $select2Project;
var $select2_status;

var svn_scheme_id;

$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURIComponent(results[1]) || 0;
    }
}


function checkBeforeAdd(svn_repo){
    if (svn_repo == '0'){
        $('#lb-msg').text('请选择仓库!');
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
        url: "/myworkflows/get_svn_scheme_detail/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改方案明细");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide();
            $("#svn_path").val(data.svn_path);
            $("#svn_perm").val(data.svn_perm).trigger('change');
            initSelect2('svn_repo', data.svn_repo_id, data.svn_repo);
            $("#myModal").modal("show");
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

function svn_scheme_detail(id){
    var url = "/myworkflows/svn_scheme_detail/?id=" + id;
    window.location.href = url;
};


function initModalSelect2(){

    $select2Project = $('#svn_repo').select2( {
        ajax: {
            url: '/myworkflows/list_svn_repo/',
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
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $("#svn_perm").select2({
        minimumResultsForSearch: Infinity,
    });
};

$(document).ready(function() {

    svn_scheme_id = $.urlParam('id');

    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        'ordering': false,
        //"serverSide": true,
        "ajax": {
            'type': 'POST',
            'url': '/myworkflows/data_svn_scheme_detail/',
            'data': function( d ){
                d.id = svn_scheme_id;
            }
        },
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "svn_scheme"},
            {"data": "svn_repo"},
            {"data": "svn_path"},
            {"data": "svn_perm"},
            {
              "data": null,
              "orderable": false,
            }
        ],
        "order": [[2, 'asc']],
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
                    targets: 6,
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

    initModalSelect2()

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
                    url: "/myworkflows/del_svn_scheme_detail/",
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

    /*$('#bt-del').click( function () {
        var selected = new Array();
        table.rows('.selected').data().toArray().forEach(function(info,i){
            selected.push(info.roomid);
        });

        if (selected.length == 0){
            alert('请选择');
            return false;
        }
        else{
            $(this).confirm({
                text:"确定删除所选的" +selected.length + "机房?",

                confirm: function(button){
                    var encoded=$.toJSON( selected );
                    var pdata = encoded
                    $.ajax({
                        type: "POST",
                        url: "/assets/del_data_room/",
                        contentType: "application/json; charset=utf-8",
                        data: pdata,
                        success: function (data) {
                            
                            if (data['data']) {
                                table.ajax.reload();
                            }else{
                                alert(data['msg'])
                                table.ajax.reload();
                            };
                        }
                    });
                },

                cancel: function(button){

                },
                confirmButton: "确定",
                cancelButton: "取消",
            });
        }
    } );*/

    // 添加
    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增方案明细");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#svn_path").val('');
        $("#svn_perm").val('0').trigger('change');
        initSelect2('svn_repo', '0', '选择仓库');
        editFlag=false;
        $("#myModal").modal("show");
    } );
    
    $('#bt-save').click( function(){

        var id = $("#id").val();
        var svn_path = $.trim($("#svn_path").val());

         if ( !/^\//.test(svn_path) ){
            $('#lb-msg').text('仓库内子路径要以/开头');
            $('#modal-notify').show();
            return false;
        }

        var svn_repo = $("#svn_repo").select2('data')[0].id;
        var svn_perm = $("#svn_perm").select2('data')[0].id;

        var inputIds = {
            "id": id,
            "svn_path": svn_path,
            "svn_repo": svn_repo,
            "svn_perm": svn_perm,
            "svn_scheme_id": svn_scheme_id,
            "editFlag": editFlag,
        };

        var encoded=$.toJSON( inputIds )
        var pdata = encoded

        urls = '/myworkflows/add_or_edit_svn_scheme_detail/';

        if (!checkBeforeAdd(svn_repo)){
            return false;
        }

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
} );
