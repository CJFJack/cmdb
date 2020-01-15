
var select2Group;

function initModalSelect2(){
    // 初始化select2
    $select2Group = $("#group").select2({
        ajax: {
            url: '/users/list_group/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            
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
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2Group;
    $select2Group.on("select2:select", function (e){ log("select2:select", e); });

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};

function log(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        var group_id = $("#group").select2('data')[0].id;

        pdata = {
            'group_id': group_id,
        }
        var encoded=$.toJSON( pdata );
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/users/get_group_permission/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                //console.log(data);

                // dischecked all
                $('input[type=checkbox]').map(function(){ $(this).prop('checked',false); })

                // add checked
                //data.forEach(function(info, i){ console.log(typeof $(this)); });
                data.forEach(function(info, i){ $("#"+info).prop('checked',true); });
            }
        });
    }
};


function getChecked(){
    var listChecked = new Array();
    $('input[type=checkbox]:checked').map(function(){ listChecked.push($(this).attr('id'));  });
    return listChecked;
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
        "ajax": "/assets/data_vip",
        "columns": [
            {"data": null},
            {"data": 'ip'},
            {"data": 'vlan'},
            {"data": "vip_belongs_to_iptype"},
            /*{
              "data": null,
              "orderable": false,
            }*/
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
                /*{
                    'targets': 1,
                    'visible': false,
                    'searchable': false
                },*/
                /*{
                    targets: 4,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\',\'" + c.hostname + "\', \'" + c.belongs_to_PlatForm + "\',\'" + c.network_area + "\',\'" + c.host_cpu + "\',\'" + c.host_mem + "\',\'" + c.host_disk + "\',\'" + c.belongs_to_ostype + "\',\'" + c.vcenter + "\',\'" + c.host_status + "\',\'" + c.host_remarks + "\',\'" + c.server_id + "\')", "type": "primary"},
                            ]
                        };
                        var html = template(context);
                        return html;
                    }
                }*/
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

    initModalSelect2();

     

    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增分组");
        $("#modal-notify").hide();
        $("#group_name").val('');
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
                 //alert(data.msg);
                 $("#myModal").modal("hide");
                }
                else{
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
            }
        });
    });

    $("#group_permission_save").click(function(){
        var group_id = $("#group").select2('data')[0].id;
        if (group_id=='0'){
            alert('请选择分组');
            return false;
        }

        var listChecked = getChecked();


        group_permission = {
            'group_id': group_id,
            'listChecked': listChecked,
        }
        var encoded=$.toJSON( group_permission );
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/users/save_group_permission/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data['data']){
                    alert('保存成功!');
                }
                else{
                    alert(data.msg);
                }
            }
        });

    });


    $("#group_info").click(function(){
        var group_id = $("#group").select2('data')[0].id;
        if (group_id=='0'){
            return false;
        }
        window.location.href = "/users/group_info/?group_id=" + group_id;
    });


} );
