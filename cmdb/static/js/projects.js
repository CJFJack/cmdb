var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);
var addSelect2 = '';
var addSelect3 = '';
var dataSet = [];
var uuid = 'table';


function edit(series_number, series_name,status, belong_mechine_room, belong_cabinets, ip, cpu,memory,disk,note) {
    editFlag = true;
    $('#modal-notify').hide();
    // $("#editModalLabel").text("修改设备信息");
    $("#edit-series_number").val(series_number);
    $("#edit-series_name").val(series_name);
    $("#edit-status").val(status);
    $("#edit-belong_mechine_room").val(belong_mechine_room);
    $("#edit-belong_cabinets").val(belong_cabinets);
    $("#edit-ip").val(ip);
    $("#edit-cpu").val(cpu);
    $("#edit-memory").val(memory);
    $("#edit-disk").val(disk);
    $("#edit-note").val(note);
    $("#editModal").modal("show");
};

$(document).ready(function() {
    table = $('#projectable').DataTable( {
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/project/get_project",
            "contentType": "application/json; charset=utf-8",
            "data": function ( d ) {
                d.uuid = uuid;
                d.type = "table";
            }
        },
        "columns": [
            {"data": "series_number"},
            {"data": "name"},
            {"data": "status"},
            {"data": "belong_mechine_room"},
            {"data": "belong_cabinets"},
            {"data": "net_ip"},
            {"data": "cpu"},
            {"data": "memory"},
            {"data": "disk"},
            {"data": "note"},
            {
                "data": null,
                "orderable": false,
            }
        ],
        "order": [[0, 'asc']],
        'columnDefs': [
                {
                    targets: 10,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.series_number + "\', \'" + c.name + "\',\'" + c.status + "\', \'" + c.belong_mechine_room + "\', \'" + c.belong_cabinets + "\', \'" + c.net_ip + "\', \'" + c.cpu + "\', \'" + c.memory + "\', \'" + c.disk + "\', \'" + c.note + "\')", "type": "primary"},
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

    

    function show_device(args){
        uuid = args;
        table.ajax.reload();
    }

    function show (name, evt) {
        if (!evt) {
            var args = "{}";
        } else {
            var args = JSON.stringify(evt.params, function (key, value) {
                if (value && value.nodeName) return "[DOM node]";
                if (value instanceof $.Event) return "[$.Event]";
                return value;
            });
            show_device(args);
        }

    };

    function log (name, evt, className) {
        if (name == 'select2:select' || name == 'select2:select2'){
            var select22 = document.getElementById('select22');
            var select23 = document.getElementById('select23');
            if (!evt) {
                var args = "{}";
            } else {
                var args = JSON.stringify(evt.params, function (key, value) {
                    if (value && value.nodeName) return "[DOM node]";
                    if (value instanceof $.Event) return "[$.Event]";
                    return value;
                });
                // show_device(args);
                $.ajax({
                    type: "POST",
                    url: "/project/get_project",
                    contentType: "application/json; charset=utf-8",
                    data: args, 
                    success: function (data) {
                        if (data['data']) {
                            uuid = args;
                            table.ajax.reload();
                        }else{
                            if ( className == "3" ) {
                                addSelect3='<select id="select23" class="js-select3-ajax"><option selected="selected">选择名称</option></select>';
                            }else{
                                addSelect2='<select id="select22" class="js-select2-ajax"><option selected="selected">选择名称</option></select>';
                            };
                            if (addSelect2 != '' && className != "3"){
                                if (select22 == null){
                                    $('#div-select2').append(addSelect2);
                                };
                                $('.js-select2-ajax').select2( {
                                    ajax: {
                                        url: "/project/get_project",
                                        dataType: 'json',
                                        type: 'POST',
                                        delay: 250,
                                        data: args,
                                        processResults: function (data, params) {
                                            // parse the results into the format expected by Select2
                                            // since we are using custom formatting functions we do not need to
                                            // alter the remote JSON data, except to indicate that infinite
                                            // scrolling can be used
                                            params.page = params.page || 1;
                                            if (data['data']){
                                                show_device(args)
                                            }else{
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
                                            }
                                        },
                                        cache: true,
                                    },
                                    minimumResultsForSearch: Infinity,
                                    escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
                                    // minimumInputLength: 1,
                                    templateResult: formatRepo, // omitted for brevity, see the source of this page
                                    templateSelection: formatRepoSelection // omitted for brevity, see the source of this page
                                });
                                $('.js-select2-ajax').on("select2:select", function (e) { log("select2:select2", e, "3"); });
                                $('.js-select2-ajax').on("select2:open", function (e) { log("select2:open2", e, "3"); });
                            };
                            if (addSelect3 != '' && className == '3'){
                                if (select23 == null){
                                    $('#div-select3').append(addSelect3);
                                };
                                $('.js-select3-ajax').select2( {
                                    ajax: {
                                        url: "/project/get_project",
                                        dataType: 'json',
                                        type: 'POST',
                                        delay: 250,
                                        data: args,
                                        processResults: function (data, params) {
                                            // parse the results into the format expected by Select2
                                            // since we are using custom formatting functions we do not need to
                                            // alter the remote JSON data, except to indicate that infinite
                                            // scrolling can be used
                                            params.page = params.page || 1;
                                            console.log(data);
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
                                        cache: true,
                                    },
                                    minimumResultsForSearch: Infinity,
                                    escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
                                    // minimumInputLength: 1,
                                    templateResult: formatRepo, // omitted for brevity, see the source of this page
                                    templateSelection: formatRepoSelection // omitted for brevity, see the source of this page
                                });
                                $('.js-select3-ajax').on("select2:select", function (e) { show("select2:select3", e); });
                            };
                        }; //end
                    }
                });
            }
        }else{
            if (name=='select2:open'){
                $('#div-select2').html("");
                $('#div-select3').html("");
            }
            if (name=='select2:open2'){
                $('#div-select3').html("");
            }
        }

    };

    var $select2 = $('.js-data-example-ajax').select2( {
        ajax: {
            url: "/project/get_project",
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return params
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
            cache: true,
        },
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

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

    
    $select2;
    $select2.on("select2:select", function (e) { log("select2:select", e); });
    $select2.on("select2:open", function (e) { log("select2:open", e); });
    
    
    // 查看更多信息
    // $('#projectable tbody').on('click', 'td.details-control', function () {
    //     var tr = $(this).closest('tr');
    //     var row = table.row( tr );
 
    //     if ( row.child.isShown() ) {
    //         // This row is already open - close it
    //         row.child.hide();
    //         tr.removeClass('shown');
    //     }
    //     else {
    //         // Open this row
    //         row.child( format(row.data()) ).show();
    //         tr.addClass('shown');
    //     }
    // } );

    // 多选
    //$('#projectable tbody').on( 'click', 'tr', function () {
    //    $(this).toggleClass('selected');
    //} );
    //删除
    $('#bt-del').click( function () {
        if (table.row('.selected')[0].length != 0){
            if(confirm("您确定要执行删除操作吗？")){
                table.row('.selected').remove().draw( false );
            }else{
                return false;
            }
        }
        else{
            alert('请选择服务器')
        }
    } );
    $('#bt-add').click( function () {
        editFlag=false;
        $("#myModal").modal("show");
    } );
    $('#bt-modal-notify').click( function () {
        $("#modal-notify").hide();
    } );
    $('#bt-save').click( function(){
        $('#modal-notify').hide();
        // var inputIds=$('#modal-list input').map(function(i,n){
        //     return $(n).val();
        // }).get();
        var inputIds={
            "series_number": $("#edit-series_number").val(),
            "name" : $("#edit-series_name").val(),
            "status": $("#edit-status").val(),
            "note": $("#edit-note").val(),
        };
        
        var urls="/assets/data_add_devices";
        var encoded=$.toJSON( inputIds );
        var pdata = encoded;
        if(editFlag){
            urls="/assets/data_edit_devices"
        };
        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                
                if (data['data']) {
                    table.ajax.reload();
                    $("#editModal").modal("hide");
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }else{
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                };
            }
        });

        $("#myModal").modal("hide");
        
    });
    $('#bt-esave').click( function(){
        $("#editModal").modal("hide");        
    });
} );