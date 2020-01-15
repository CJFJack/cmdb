// 修改之前的数据
var origin_data;

var table;
var editFlag;
//预编译模板
var tpl = $("#tpl").html();

var str = "确定删除选中的主机域组?";
var count=0;

var template = Handlebars.compile(tpl);
var $select2Attach_domain_grouop;
var $select2Hostname;


function initModalSelect2(){

    $select2Attach_domain_grouop = $('#domain_groups').select2( {
        ajax: {
            url: '/assets/list_domain_group/',
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
        placeholder: '选择域组',
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        multiple: true,
        //templateResult: formatRepo, // omitted for brevity, see the source of this page
        //templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
        dropdownAutoWidth: true,
    });

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};


};


function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    // 重新生成uuid
    uuid = generateUUID();
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_resource_domain_group/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
                origin_data = data;
                $("#myModalLabel").text("修改主机域组");
                $("#modal-notify").hide();
                $("#id").val(data.id);
                $("#show_id").hide();

                $("#hostname").val(data.hostname);


                // !-- Add domain_groups,multiple select!
                var domain_group_info = $.parseJSON(data.domain_group_info);
                $("#domain_groups").html('');
                var values = Array();
                domain_group_info.forEach(function(info, i){
                    $("#domain_groups").append('<option value="' + info[0] + '">' + info[1] + '</option>');
                    values.push(info[0]);
                });
                $("#domain_groups").select2('val',values,true);

                // -- End

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

function addBeforeCheck(belongs_to_apptype,application_name,host_ids){
    if (belongs_to_apptype == '0'){
        $('#lb-msg').text('请选择应用类型!');
        $('#modal-notify').show();
        return false;
    }
    if (host_ids.length == 0){
        $('#lb-msg').text('请选择host!');
        $('#modal-notify').show();
        return false;
    }
    
    if (!application_name){
        $('#lb-msg').text('应用名不能为空!');
        $('#modal-notify').show();
        return false;
    }
    return true;
};

// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });


$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "autoWidth": false,
        "ajax": "/assets/data_domain_group/",
        "ordering": false,
        "columns": [
            {"data": "id"},
            {"data": "hostname"},
            {"data": 'ip'},
            {"data": 'group_name'},
            {
              "data": null,
              "orderable": false,
            }
        ],
        "order": [[0, 'asc']],
        columnDefs: [
                {
                    'targets': 0,
                    'visible': false,
                    'searchable': false
                },
                {    
                    'targets': [2, 3],
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
        var hostname_id = $("#hostname").val();

        var domain_groups = $("#domain_groups").select2('data');
        var domain_group_ids = Array();
        for (i=0; i<domain_groups.length; i++){
            domain_group_ids.push(domain_groups[i].id);
        }

        /*if (domain_group_ids.length == 0) {
            $('#lb-msg').text('请选择域组!');
            $('#modal-notify').show();
            return false;
        }*/

        var inputIds = {
            'id': id,
            'hostname_id': hostname_id,
            'domain_group_ids': domain_group_ids,
        }

        //return false;
        
        if (editFlag){
            var urls = "/assets/edit_data_domain_group/";
        }
        else{
            var urls = "/assets/add_data_domain_group/";
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
                $('#lb-msg').text('你没有增加基础资源的权限');
                $('#modal-notify').show();
            }
        });
    });

    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });

});