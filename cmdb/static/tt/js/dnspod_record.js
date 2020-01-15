// 修改之前的数据
var origin_data;

var table;
var editFlag;
var deviceFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的记录?";
var count=0;

var $select2Belongs_to_platform;
var $select2record_type;
var $select2record_line;


function initModalSelect2(){
    // 初始化select2

    $select2Belongs_to_platform = $('#belongs_to_PlatForm').select2( {
        ajax: {
            url: '/assets/list_platform/',
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
                            company: item.company,
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
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2record_type = $("#record_type").select2();
    $select2record_line = $("#record_line").select2();
   
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
        url: "/assets/get_dnspod_dnspod_record/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改记录信息");
            $("#modal-notify").hide();
            $("#show_id").hide();
            $("#id").val(id);
            initSelect2('belongs_to_PlatForm', data.platform_id, data.platform);

            $("#bank_domain").val(data.bank_domain);
            $("#smart_dns").val(data.smart_dns);
            $("#record_id").val(data.record_id);
            $("#show_record_id").hide();
            $("#sub_domain").val(data.sub_domain);
            // initSelect2('record_type', data.record_type, data.record_type);
            $("#record_type").val(data.record_type).trigger('change');
            $("#record_line").val(data.record_line).trigger('change');
            // initSelect2('record_line', data.record_line, data.record_line);
            $("#value").val(data.value);
            $("#ttl").val(data.ttl);
            $('input:radio[name=open_monitor]').filter('[value=' + data.monitor_status + ']').prop('checked',true);

            $("#myModal").modal("show");
        },
        error: function(data){
            alert('你没有修改基础资源权限');
        }
    });

};

function checkBeforeAdd(sub_domain, value, ttl){
    if (sub_domain == ''){
        $('#lb-msg').text('记录名不能为空!');
        $('#modal-notify').show();
        return false;
    }

    if (value == '') {
        $('#lb-msg').text('记录ip不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (ttl == ''){
        $('#lb-msg').text('ttl不能为空!');
        $('#modal-notify').show();
        return false;
    }
    return true;
};

function formatRepo (repo) {
    
    var markup = '<div class="clearfix"><div class="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};


// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });


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
    table = $('#mytable').DataTable( {
        "processing": true,
        "ordering": false,
        "ajax": {
            'type': 'POST',
            'url': '/assets/dnspod_record/',
            'data': function( d ){
                d.domain_name = $.urlParam('domain_name');
            },
        },
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": 'platform'},
            {"data": 'bank_domain'},
            {"data": "smart_dns"},
            {"data": "record_id"},
            {"data": "sub_domain"},
            {"data": "record_type"},
            {"data": "record_line"},
            {"data": "value"},
            {"data": "ttl"},
            {"data": "monitor_status"},
            {
              "data": null,
              "orderable": false,
            },
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
                    'targets': [1, 5],
                    'visible': false,
                    'searchable': false
                },
                {
                    targets: 12,
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
    //$resourceType.on("select2:select", function (e) { autofill("select2:select", e); });
    //show or hide column
    /*$('input.global_filter').on( 'keyup click', function () {
        filterGlobal();
    } );*/

    /*$('input.column_filter').on( 'keyup click', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );*/
    /*$('select.column_filter').on('change', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );*/
    /*$('#filter_start').Zebra_DatePicker({
        // pair: $('#filter_end'),
    });*/
    /*$('#filter_end').Zebra_DatePicker({
        // direction: 1,
    });*/


    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增记录");
        $("#modal-notify").hide();
        $("#show_id").hide();
        initSelect2('belongs_to_PlatForm', '0', '选择平台');
        $("#bank_domain").val('');
        $("#smart_dns").val('');
        $("#show_record_id").hide();
        $("#record_id").val('');
        $("#sub_domain").val('');
        $("#value").val('');
        $("#ttl").val('');
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
        var id = $("#id").val();
        var platform = $("#belongs_to_PlatForm").select2('data')[0].id;
        var bank_domain = $("#bank_domain").val();
        var smart_dns = $("#smart_dns").val();
        var record_id = $("#record_id").val();
        var sub_domain = $("#sub_domain").val();
        var record_type = $("#record_type").select2('data')[0].text;
        var record_line = $("#record_line").select2('data')[0].text;
        var value = $("#value").val();
        var ttl = $("#ttl").val();
        var open_monitor = $('input[name=open_monitor]:checked').val();    // true or false
        var domain_name = $.urlParam('domain_name');
        

        if (editFlag){
            var urls = "/assets/edit_data_domain_record/";
        }else{
            var urls = "/assets/add_data_domain_record/";
        }

        var inputIds = {
                'id': id,
                'platform': platform,
                'bank_domain': bank_domain,
                'smart_dns': smart_dns,
                'record_id': record_id,
                'sub_domain': sub_domain,
                'record_type': record_type,
                'record_line': record_line,
                'value': value,
                'ttl': ttl,
                'open_monitor': open_monitor,
                'domain': domain_name,
            };
        
        if ( !checkBeforeAdd(sub_domain, value, ttl) ){
            return false;
        }

        var encoded=$.toJSON( inputIds );
        var pdata = encoded;

        // console.log(inputIds);
        // return false;

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
                $('#lb-msg').text('你没有增加基础资源权限');
                $('#modal-notify').show();
            }
        });
    });


    $("#bt-del").confirm({
        //text:"确定删除所选的主机?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );8
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_domain_record/",
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

    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });

    $("#bt-sync").click(function(){
        //同步按钮
        $.ajax({
            type: "POST",
            url: "/assets/sync_domain_record/",
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                
                if (data['data']) {
                    alert('数据同步完成');
                    table.ajax.reload();
                }else{
                    alert(data['msg']);
                };
            }
        });
        
    });

} );
