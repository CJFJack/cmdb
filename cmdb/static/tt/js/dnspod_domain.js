// 修改之前的数据
var origin_data;

var table;
var editFlag;
//预编译模板
// var tpl = $("#tpl").html();

var str = "确定删除选中的域名?";
var count=0;

//var template = Handlebars.compile(tpl);


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

        "initComplete": function () {
            var api = this.api();
            api.$("td:first-child").click( function () {
                //api.search( this.innerHTML ).draw();
                //console.log($(this).text());
                //console.log($(this).text());
                window.location.href = "/assets/dnspod_record/?domain_name=" + $(this).text();
            } );
        },


        "processing": true,
        "ordering": false,
        "autoWidth": true,
        "ajax": "/assets/data_dnspod_domain/",
        "columns": [
            {"data": 'domain_id', "visible": false},
            {"data": 'domain_name'},
        ],
        // "order": [[1, 'asc']],

        columnDefs: [
                {
                    'targets': 1,
                    "render": function(data, type, row){
                        return '<a href="#">' + data + '</a>';
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

    // initModalSelect2();

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

    //删除
    $("#bt-del").confirm({
        //text:"确定删除所选的服务?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_sdns/",
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
        $("#show_id").hide();
        $("#dnsname").val('');
        $("#ip_binding").val('').trigger("change");

        $("#myModalLabel").text('新增智能DNS');
        $("#modal-notify").hide();
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
        var dnsname = $("#dnsname").val();

        var ip_binding = $("#ip_binding").select2('data');
        var vip_ids = Array();
        for (i=0; i<ip_binding.length; i++){
            vip_ids.push(ip_binding[i].id);
        }

        var inputIds = {
            'id': id,
            'dnsname': dnsname,
            'vip_ids': vip_ids,
            "origin_data": origin_data,
        }

        if (!addBeforeCheck(dnsname)){
            return false;
        };
        
        if (editFlag){
            var urls = "/assets/edit_data_sdns/";
        }
        else{
            var urls = "/assets/add_data_sdns/";
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
                $('#lb-msg').text('你没有增加平台业务的权限');
                $('#modal-notify').show();
            }
        });
    });

    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });

});