// 修改之前的数据
var origin_data;

var table;
var editFlag;
//预编译模板
var tpl = $("#tpl").html();

var str = "确定删除选中的平台?";
var count=0;

var template = Handlebars.compile(tpl);
var $select2BelongsToChief;

function initModalSelect2(){
  $select2BelongsToChief = $('#belongs_to_chief').select2( {
      ajax: {
          url: '/assets/list_chief_platform/',
          dataType: 'json',
          type: 'POST',
          delay: 250,
          /*data: function (params) {
              var selected = $('#belongs_to_room').select2('data');
              if (selected != '') {
                  params = {'data': selected[0].text}
              }else {
                  params = ''
              };
              return $.toJSON(params)
          },*/
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
    templateResult: formatRepo, // omitted for brevity, see the source of this page
    templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
  });

  $select2PoolStatus = $("#pool_status").select2({
        minimumResultsForSearch: Infinity,
    });
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
        url: "/assets/get_business_platform/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            origin_data = data;
            $("#myModalLabel").text("修改平台信息");
            $("#modal-notify").hide();
            $("#show_id").hide();
            $("#id").val(data.id);
            $("#belongs_to_chief").html('');
            $("#belongs_to_chief").append('<option value="' + data.belongs_to_chief_id + '">' + data.belongs_to_chief_name + '</option>');
            $("#belongs_to_chief").select2('val',data.belongs_to_chief_id,true);   
            $("#platform_name").val(data.platform_name);
            $("#company").val(data.company);      
            $("#manager").val(data.manager);         
            $("#manager_tel").val(data.manager_tel);         
            $("#developer").val(data.developer);                
            $("#developer_tel").val(data.developer_tel);      
            $("#status").val(data.status);
            $("#myModal").modal("show");
        },
        error: function(data){
            alert('你没有修改平台应用权限');
        }
    });
}

function addBeforeCheck(platform_name){
    if (platform_name == ''){
        $('#lb-msg').text('平台名不能为空!');
        $('#modal-notify').show();
        return false;
    }

    if (company == ''){
        $('#lb-msg').text('公司名不能为空!');
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


$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ajax": "/assets/data_platform/",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "belongs_to_chief_platform_name"},
            {"data": "platform_name"},
            {"data": "company"},
            {"data": 'manager'},
            {"data": 'manager_tel'},
            {"data": 'developer'},
            {"data": 'developer_tel'},
            {"data": 'status'},
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
                    targets: 10,
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


    // 多选
    // $('#mytable tbody').on( 'click', 'tr', function () {
    //     $(this).toggleClass('selected');
    // } );
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
                    url: "/assets/del_data_platform/",
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
    
    // 增加button
    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增平台信息");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#belongs_to_chief").html('');
        $("#belongs_to_chief").append('<option value="0">选择主平台</option>');
        $("#belongs_to_chief").select2('val','0',true);
        $("#platform_name").val('');
        $("#company").val('');
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
        var id = $("#id").val();
        var belongs_to_chief = $("#belongs_to_chief").select2('data')[0].id;
        var platform_name = $("#platform_name").val();
        var company = $("#company").val();
        var manager = $("#manager").val();
        var manager_tel = $("#manager_tel").val();
        var developer = $("#developer").val();
        var developer_tel = $("#developer_tel").val();
        var status = $("#status").val();
        
        var inputIds = {
            'id': id,
            'belongs_to_chief': belongs_to_chief,
            'platform_name': platform_name,
            'company': company,
            'manager': manager,
            'manager_tel': manager_tel,
            'developer': developer,
            'developer_tel': developer_tel,
            "origin_data": origin_data,
            "status": status,
        };

        if (!addBeforeCheck(platform_name, company)){
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
            },
            error: function (data) {
                $('#lb-msg').text('你没有增加平台业务的权限');
                $('#modal-notify').show();
            }
        });
    });
    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });


} );
