
var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
//var template = Handlebars.compile(tpl);

function filterGlobal () {
    $('#mytable').DataTable().search(
        $('#global_filter').val(),
        $('#global_regex').prop('checked'),
        $('#global_smart').prop('checked')
    ).draw();
}
 
function filterColumn ( i ) {
    $('#mytable').DataTable().column( i ).search(
        $('#col'+i+'_filter').val(),
        $('#col'+i+'_regex').prop('checked'),
        $('#col'+i+'_smart').prop('checked')
    ).draw();
}


$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {

        "initComplete": function () {
            var api = this.api();
            api.$("td:first-child").click( function () {
                //api.search( this.innerHTML ).draw();
                //console.log($(this).text());
                window.location.href = "/assets/platform_detail/?platform_name=" + $(this).text();
            } );
        },

        "processing": true,
        "ajax": "/assets/data_index/",
        "ordering": false,
        "columns": [
            //{"data": null},
            {"data": "id"},
            {"data": "platform_name"},
            {"data": 'hostname'},
            {"data": 'network_zone'},
            {"data": 'vip'},
            {"data": 'assigned_ip'},
            {"data": 'public_or_load_ip'},
            {"data": 'apptype'},
            {"data": 'applications'},
            {"data": 'ostype', "visible": false},
            {"data": 'status'},
            /*{
              "data": null,
              "orderable": false,
            }*/
        ],


        "order": [[1, 'asc']],
        columnDefs: [
                {
                    'targets': 0,
                    'visible': false,
                    'searchable': false
                },
                {
                    'targets': [1],
                    "render": function(data, type, row){
                        return '<a href="#">' + data + '</a>';
                    },
                },
                {    
                    'targets': [3,4,5,6,7,8],
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },
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

    $('a.toggle-vis').on( 'click', function (e) {
        e.preventDefault();
 
        // Get the column API object
        var column = table.column( $(this).attr('data-column') );
        console.log(column);
 
        // Toggle the visibility
        column.visible( ! column.visible() );

        // Change the is_display content
        if (column.visible()){
            $(this)[0].children[0].textContent = '隐藏';
        }else{
            $(this)[0].children[0].textContent = '显示';
        }
    } );
    
    $('#chb-all').on('click', function(e){
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function(i,n){
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked){
              $row.addClass('selected');
            }else{
              $row.removeClass('selected');
            }
        });
    });

    
    //$resourceType.on("select2:select", function (e) { autofill("select2:select", e); });
    //show or hide column
    $('a.abc').on( 'click', function (e) {

        if ($(this).find('input').attr('checked')){
            $(this).find('input').attr('checked',false);
        }
        else{
            $(this).find('input').attr('checked',true);
        };
        // e.preventDefault();
        // Get the column API object
        var column = table.column( $(this).attr('data-column') );
        // Toggle the visibility
        column.visible( ! column.visible() );
    } );
    $('input.global_filter').on( 'keyup click', function () {
        filterGlobal();
    } );

    $('input.column_filter').on( 'keyup click', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );

    /*$('select.column_filter').on('change', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );*/
    
    // 查看更多信息
    $('#mytable tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );

        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( format(row.data()) ).show();
            tr.addClass('shown');
        }
    } );

    // 多选
    // $('#mytable tbody').on( 'click', 'tr', function () {
    //     $(this).toggleClass('selected');
    // } );
    //删除
    $('#bt-del').click( function () {
        var selected = [];
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function(i,n){
            var $row = $(this).closest('tr');
            if (n.checked){
                selected.push($row)
            }
        });
        if (selected.length == ''){
            alert('请选择服务器')
        }
        else{
            if(confirm("您确定要执行删除操作吗？")){
                var length=selected.length;
                var raw=[];
                for (var i=0; i<length; i++){
                    raw[i] = table.row(selected[i]).data()
                };
                var encoded=$.toJSON( raw );
                var pdata = encoded
                
                $.ajax({
                    type: "POST",
                    url: "/assets/data_del_devices",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        
                        if (data['data']) {
                            table.ajax.reload();
                        }else{
                            alert(data['msg'])
                        };
                    }
                });
            }else{
                return false;
            }
        }
    } );
    // 添加modal显示
    // 增加button
    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增平台信息");
        $("#modal-notify").hide();
        $("#platform_name").val('');
        $("#manager").val('');
        $("#manager_tel").val('');
        $("#developer").val('');
        $("#developer_tel").val('');
        editFlag=false;
        $("#myModal").modal("show");
    } );
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
        var platform_name = $("#platform_name").val();
        var manager = $("#manager").val();
        var manager_tel = $("#manager_tel").val();
        var developer = $("#developer").val();
        var developer_tel = $("#developer_tel").val();
        
        var inputIds = {
            'platform_name': platform_name,
            'manager': manager,
            'manager_tel': manager_tel,
            'developer': developer,
            'developer_tel': developer_tel,
        };

        if (!addBeforeCheck(platform_name,manager,manager_tel,developer,developer_tel)){
            return false;
        }
        
        if (editFlag){
            var urls = "/assets/edit_data_platform/";
        }
        else{
            var urls = "/assets/add_data_platform/";
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
                }else{
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                };
            }
        });
    });
    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });


} );
