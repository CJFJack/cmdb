// 修改之前的数据
var origin_data;

var table;
var editFlag;
var deviceFlag;

//预编译模板
var tpl = $("#tpl").html();
var template = Handlebars.compile(tpl);

var str = "确定删除选中的ip类型?";
var count=0;

var select2Belongs_to_room;

function initModalSelect2(){
    // 初始化select2
    $select2Belongs_to_room = $('#belongs_to_room').select2( {
        ajax: {
            url: '/assets/list_room/',
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
        url: "/assets/get_ip_iptype/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改ip类型");
            $("#modal-notify").hide();
            $("#iptype_id").val(data.id);
            $("#show_iptype_id").hide();
            $("#typename").val(data.typename);
            $("#network_area").val(data.network_area);
            $("#network_zone").val(data.network_zone);
            $("#start").val(data.start);
            $("#end").val(data.end);
            $("#order").val(data.order);
            $('input:radio[name=order]').filter('[value=' + data.order + ']').prop('checked',true);
            //$("#ip_type").val(data.ip_type);
            $('input:radio[name=ip_type]').filter('[value=' + data.ip_type + ']').prop('checked',true);
            //$("#in_pairs").val(data.in_pairs);
            $('input:radio[name=in_pairs]').filter('[value=' + data.in_pairs + ']').prop('checked',true);

            //$("#belongs_to_room").html('');
            $("#belongs_to_room").append('<option value="' + data.ip_belongs_to_room_id + '">' + data.ip_belongs_to_room + '</option>')
            $("#belongs_to_room").select2('val',data.ip_belongs_to_room_id,true);

            $("#myModal").modal("show");
        },
        error: function(data){
            alert('你没有修改ip管理的权限');
        }
    });


};

function checkBeforeAdd(typename,network_area,network_zone,start,end,order,ip_type,in_pairs,ip_belongs_to_room){
    if (typename == ''){
        $('#lb-msg').text('typename不能为空!');
        $('#modal-notify').show();
        return false;
    }
    
    if (network_area == ''){
        $('#lb-msg').text('network_area不能为空!');
        $('#modal-notify').show();
        return false;
    }

    if (network_zone == ''){
        $('#lb-msg').text('请输入网络类型!');
        $('#modal-notify').show();
        return false;
    }

    if (start == '') {
        $('#lb-msg').text('起始位不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (end == '') {
        $('#lb-msg').text('结束位不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (order == '') {
        $('#lb-msg').text('请选择顺序!');
        $('#modal-notify').show();
        return false;
    }
    if (ip_type == '') {
        $('#lb-msg').text('ip_type不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (in_pairs == '') {
        $('#lb-msg').text('in_pairs不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (ip_belongs_to_room == '0'){
        $('#lb-msg').text('请先选择机房!');
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
        "ordering": false,
        "ajax": "/assets/data_iptype",
        "columns": [
            {"data": null},
            {"data": 'id'},
            {"data": 'typename'},
            {"data": 'network_area'},
            {"data": 'network_zone'},
            {"data": 'start'},
            {"data": 'end'},
            {"data": 'order'},
            {"data": 'ip_type'},
            {"data": 'in_pairs'},
            {"data": "ip_belongs_to_room"},
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
                    targets: 11,
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

    initModalSelect2();

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

    $("#selected-all").click( function (){
        if (condition.host){
            var host_id = {
                'host': $("#belongs_to_host").select2('data')[0].id,
            }
            var encoded=$.toJSON( host_id );
            var pdata = encoded;
            $.ajax({
                type: "POST",
                url: "/assets/list_service/",
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    $("#belongs_to_service").val('').trigger('change');
                    $select2Belongs_to_device =  $("#belongs_to_service").select2({
                        data: data
                    });
                    var service_id = Array()
                    for (var i=0;i<data.length;i++){
                        service_id.push(data[i].id)
                    }
                    $("#belongs_to_service").val(service_id).trigger('change');
                }
            });
        }
        else{
            $('#lb-msg').text('要使用全选,请先选择host主机');
            $('#modal-notify').show();
            return false;
        }
    });

    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增IP类型");
        $("#modal-notify").hide();

        $("#show_iptype_id").hide();
        $("#typename").val('');
        $("#network_area").val('');
        $("#network_zone").val('');
        $("#start").val('');
        $("#end").val('');

        $('input:radio[name=order]').filter('[value=0]').prop('checked',true);

        $('input:radio[name=ip_type]').filter('[value=VM]').prop('checked',true);

        $('input:radio[name=in_pairs]').filter('[value=0]').prop('checked',true);

        $("#belongs_to_room").val('0').trigger('change');


        editFlag=false;
        $("#myModal").modal("show");
    } );
    $('#file-save').click( function () {
        $("#Modal-file").modal("hide");
    } );

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
        var id = $("#iptype_id").val();
        var typename = $("#typename").val();
        var network_area = $("#network_area").val();
        var network_zone = $("#network_zone").val();
        var start = $("#start").val();
        var end = $("#end").val();
        var order = $('input[name=order]:checked').val();    // 0 or 1
        var ip_type = $('input[name=ip_type]:checked').val();    // VM,PM,VIP
        var in_pairs = $('input[name=in_pairs]:checked').val();    // 0 or 1
        var ip_belongs_to_room = $("#belongs_to_room").select2('data')[0].id;


        var inputIds = {
                'id': id,
                'typename': typename,
                'network_area': network_area,
                'network_zone': network_zone,
                'start': start,
                'end': end,
                'order': order,
                'ip_type': ip_type,
                'in_pairs': in_pairs,
                'ip_belongs_to_room': ip_belongs_to_room,
                "origin_data": origin_data,
            };

        if (editFlag){
            var urls = "/assets/edit_data_iptype/";
        }
        else{
            var urls = "/assets/add_data_iptype/";
        }
        

        if ( !checkBeforeAdd(typename,network_area,network_zone,start,end,order,ip_type,in_pairs,ip_belongs_to_room) ){
            return false;
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
            },
            error: function (data) {
                $('#lb-msg').text('你没有增加ip管理的权限');
                $('#modal-notify').show();
            }
        });
    });
    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
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

    $("#bt-del").confirm({
        //text:"确定删除所选的物理设备?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_iptype/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        
                        if (data['data']) {
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        }else{
                            alert(data['msg']);
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
