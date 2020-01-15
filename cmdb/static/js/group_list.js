
var str = "确定删除分组?";
var count=0;

// 公司组织架构数据
var group_org;

//预编译模板
var tpl = $("#tpl").html();

var template = Handlebars.compile(tpl);

var $select2GroupLeader;


function initModalSelect2(){
    // 初始化select2

    $select2GroupLeader = $('#group_leader').select2( {
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

    $select2ParentGroup = $('#parent_group').select2( {
        ajax: {
            url: '/assets/list_group/',
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

    $select2Company = $('#company').select2( {
        ajax: {
            url: '/it_assets/list_company_code/',
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
                            code: item.code,
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

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};



function group_of_users(id) {
    // 分组的用户
    window.location.href = "/users/group_info/?group_id=" + id;
};


function section(id) {
    // 分组的用户
    window.location.href = "/users/group_section/?group_id=" + id;
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
        url: "/users/get_data_group/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            if (data.success){
                $("#myModalLabel").text("修改部门信息");
                $("#modal-notify").hide();
                $("#id").val(data.data.id);
                $("#show_id").hide()
                $("#name").val(data.data.name);
                initSelect2('group_leader', data.data.group_leader_id, data.data.group_leader_name);
                initSelect2('parent_group', data.data.parent_group_id, data.data.parent_group_name);
                initSelect2('company', data.data.company_id, data.data.company_name);
                if (data.data.is_public){
                    $('input:radio[name="is_public"]').filter('[value="true"]').prop('checked', true);
                }else{
                    $('input:radio[name="is_public"]').filter('[value="false"]').prop('checked', true);
                }
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

function pre_filter_name() {
    var name = $.urlParam('name');
    if ( name != null ) {
        table.search(name).draw()
    }
}

$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ordering": false,
        "ajax": {
            'type': 'GET',
            'url': '/users/data_group_list/',
        },
        "columns": [
            {"data": null},
            {"data": 'id'},
            {"data": 'company'},
            {"data": 'name'},
            {"data": 'parent_name'},
            {"data": 'group_leader'},
            {"data": 'projects'},
            {"data": 'is_public'},
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
                    'targets': 5,
                    "render": function(data, type, row){
                        return '<a href="/users/user_list/?username=' + data + '">' + data + '</a>'
                    },
                },
                {    
                    'targets': 6,
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },
                {
                    targets: 8,
                    render: function (a, b, c, d) {
                        if ( $("#is_superuser").val() == 'True' ) {
                            var context =
                            {
                                func: [
                                    {"name": "部门用户", "fn": "group_of_users(\'" + c.id + "\')", "type": "primary"},
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "success"},
                                    {"name": "管理分组", "fn": "section(\'" + c.id + "\')", "type": "default"},
                                ]
                            };
                        } else {
                            var context =
                            {
                                func: [
                                    {"name": "部门用户", "fn": "group_of_users(\'" + c.id + "\')", "type": "primary"},
                                    {"name": "管理分组", "fn": "section(\'" + c.id + "\')", "type": "default"},
                                ]
                            };
                        }
                        var html = template(context);
                        return html;
                    }
                }
        ],
        "language": {
                "url": "/static/js/i18n/Chinese.json"
        },
        "createdRow": function(row, data, index) {
            // console.log(data.parent_name);
            if ( data.parent_name != "" ){
                $('td', row).eq(3).addClass('highlight')
            }
            
        }
    });

    pre_filter_name();

    initModalSelect2();

    if ( $("#upper_group_leader").val() == 'False' ){ table.columns( 8 ).visible(false) }

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

    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增部门");
        $("#modal-notify").hide();
        $("#id").val('');
        $("#show_id").hide();
        $("#name").val('');
        initSelect2("group_leader", '0', '选择负责人');
        initSelect2("parent_group", '0', '无');
        $('input:radio[name=is_public]').filter('[value=false]').prop('checked',true);
        //$("#add_user").val('').trigger('change');
        editFlag=false;
        $("#myModal").modal("show");
    } );

    $("#bt-org").click(function(event) {
        /* Act on the event */
        // var params = { sortable: true };
        /*$("#demo1").treeMultiselect({
                        hideSidePanel: true,
                        freeze: true,
                        searchable: true,
                        startCollapsed: true,
                    });
        $("#Modal-file").modal("show");
        return false;*/
        $(".tree-multiselect").remove()
        if (group_org == undefined) {
            $.ajax({
                type: "GET",
                url: '/users/get_group_org/',
                contentType: "application/json; charset=utf-8",
                beforeSend: function(){
                    $("#Modal-file").modal("show");
                    $("#before_group_org").show();
                },
                success: function (data) {
                    // group_org = data
                    $("#demo1").html('')
                    data.forEach(function(e, i){
                        if ( e.linkurl ) {
                            var str = "<option value=" + e.leaf + " data-section=" + e.leaf_to_root + " data-linkurl=" + e.linkurl + '>' + e.leaf + "</option>"
                            console.log(str)
                            $("#demo1").append("<option value=" + e.leaf + " data-section=" + e.leaf_to_root + " data-linkurl=" + e.linkurl + '>' + e.leaf + "</option>")
                        } else {
                            $("#demo1").append('<option value=' + e.leaf + ' data-section=' + e.leaf_to_root + '>' + e.leaf + '</option>')
                        }
                    })
                    $("#demo1").treeMultiselect({
                        hideSidePanel: true,
                        freeze: true,
                        searchable: true,
                        startCollapsed: true,
                    });
                    $("#before_group_org").hide();
                }
            });
        } else {
            $("#Modal-file").modal("show");
        }
    });
    
    $('#bt-save').click( function(){
        var id = $("#id").val();
        var name = $("#name").val();

        if (name == ''){
            $('#lb-msg').text('请输入分组名称');
            $('#modal-notify').show();
            return false;
        }

        var group_leader = $("#group_leader").select2('data')[0].id;
        if (group_leader == '0'){
            $('#lb-msg').text('选择负责人');
            $('#modal-notify').show();
            return false;
        }

        var parent_group = $("#parent_group").val();
        var company = $("#company").val();

        // 如果没有父部门，需要选择公司
        if (parent_group == '0') {
            if ( company == '0' ) {
                $('#lb-msg').text('一级部门需要选择公司');
                $('#modal-notify').show();
                return false;
            }
        }

        var is_public = $('input[name=is_public]:checked').val();


        var inputIds = {
                'id': id,
                'name': name,
                'parent_group': parent_group,
                'group_leader': group_leader,
                'is_public': is_public,
                'editFlag': editFlag,
                'company': company,
            };
        var urls = "/users/add_or_edit_group/";

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

    $("#reset_parent_group").click(function(event) {
        /* Act on the event */
        initSelect2("parent_group", 0, '无')
    });

} );
