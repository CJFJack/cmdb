
var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的机柜?";
var count=0;

function initModalSelect2(){
  $select2Belong_mechine_room = $('#belongs_to_room').select2( {
      ajax: {
          url: '/assets/list_room',
          dataType: 'json',
          type: 'GET',
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
};

/*function addSelection(belong_mechine_room, belong_idc){
    $select2Belong_mechine_room.append('<option value="'+belong_mechine_room+'">'+belong_mechine_room+'</option>').val(belong_mechine_room).trigger('change');;
    $select2Belong_idc.append('<option value="'+belong_idc+'">'+belong_idc+'</option>').val(belong_idc).trigger('change');;
};*/

function formatRepo (repo) {
    // if (repo.loading) return repo.text;

    // var markup = '<div class="clearfix">' +
    // '<div class="col-sm-1">' +
    // '<img src="' + repo.owner.avatar_url + '" style="max-width: 100%" />' +
    // '</div>' +
    // '<div clas="col-sm-10">' +
    // '<div class="clearfix">' +
    // '<div class="col-sm-6">' + repo.full_name + '</div>' +
    // '<div class="col-sm-3"><i class="fa fa-code-fork"></i> ' + repo.forks_count + '</div>' +
    // '<div class="col-sm-2"><i class="fa fa-star"></i> ' + repo.stargazers_count + '</div>' +
    // '</div>';

    // if (repo.description) {
    //   markup += '<div>' + repo.description + '</div>';
    // }

    // markup += '</div></div>';
    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};

function edit(cabinet_id) {

    var data = {
        'id': cabinet_id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_cabinet/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            editFlag = true;
            $("#myModalLabel").text("修改机柜信息");
            $("#modal-notify").hide();
            $("#cabinet_id").val(cabinet_id);
            $("#show_cabinet_id").hide();
            $("#show_device_count").hide();

            $("#belongs_to_room").html('');
            $("#belongs_to_room").append('<option value="' + data.belongs_to_room_id + '">' + data.belongs_to_room + '</option>');
            $("#belongs_to_room").select2('val',data.belongs_to_room_id,true);
            $("#cabinetname").val(data.cabinetname)
            $("#myModal").modal("show");
        }
    });
}

$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ajax": "/assets/data_cabinet",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": 'belongs_to_room'},
            {"data": "cabinetname"},
            {"data": "device_count"},
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
                    targets: 5,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\', \'" + c.belongs_to_room + "\', \'" + c.cabinetname + "\',\'" + c.device_count + "\')", "type": "primary"},
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

    initModalSelect2();

    // 多选
    // $('#mytable tbody').on( 'click', 'tr', function () {
    //     $(this).toggleClass('selected');
    // } );

    /*$('#submit-file-formsss').on('submit', function(e){
        
        e.preventDefault();
        $.ajax({
            url: '/assets/upload_cabinet', //this is the submit URL
            type: 'POST', //or POST
            data: $('#submit-file-form').serialize(),
            success: function(data){
                if (data['data']){
                    $('#upload-notify').addClass("alert-success")
                    $('#upload-notify').show()
                    $('#lb-msg-upload').text('上传成功')
                }
                else{
                    $('#upload-notify').addClass("alert-danger")
                    $('#upload-notify').show()
                    $('#lb-msg-upload').text(data['msg'])
                }
            }
        });
    } );*/
    /*$('#bt-upload').click( function () {
        $("#Modal-file").modal("show");
        $("#upload-notify").hide();
    } );*/
    /*$('#bt-upload-notify').click( function () {
        $("#upload-notify").hide();
    } );*/
    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增机柜信息");
        $("#modal-notify").hide();
        $("#show_cabinet_id").hide();
        $("#show_roomname").hide();
        $("#belongs_to_room").removeAttr('disabled');
        $("#cabinetname").val('').removeAttr('disabled');
        $("#show_device_count").hide();
        editFlag=false;
        $("#myModal").modal("show");
    } );
    $('#file-save').click( function () {
        $("#Modal-file").modal("hide");
    } );
    // $('#bt-input').click( function () {
    //     $("#Modal-file").modal("show");
    // } );
    $('#bt-modal-notify').click( function () {
        $("#modal-notify").hide();
    } );
    $('#bt-save').click( function(){
        // var inputIds=$('#modal-list input').map(function(i,n){
        //     return $(n).val();
        // }).get();
        if(editFlag){
            urls="/assets/edit_data_cabinet/"
            var cabinet_id = $("#cabinet_id").val();
            var cabinetname = $("#cabinetname").val();
            if (!cabinetname) {
                alert('机柜名不能为空!');
            }
            var belongs_to_room = $("#belongs_to_room").select2('data')[0].id;
            var inputIds = {
                'cabinet_id': cabinet_id,
                'cabinetname': cabinetname,
                'belongs_to_room': belongs_to_room,
            }
        }else{
            urls="/assets/add_data_cabinet/";
            var belongs_to_room_id = $('#belongs_to_room').select2('data')[0].id;
            var new_cabinetname = $("#cabinetname").val();
            if (belongs_to_room_id == "0"){
                alert('请选择机房!');
                return false;
            }
            if (!$("#cabinetname").val()) {
                alert('请输入机柜名称!');
                return false;
            }
            var inputIds = {
                "belongs_to_room_id": belongs_to_room_id,
                "cabinetname": new_cabinetname,
            };

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
            }
        });
    });

    // 删除
    $("#bt-del").confirm({
        //text:"确定删除所选的机柜?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_cabinet/",
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
});
