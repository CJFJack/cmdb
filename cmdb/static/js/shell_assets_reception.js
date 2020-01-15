// 修改之前的数据
var origin_data;

var table;
var editFlag;
var deviceFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的资产?";
var count = 0;

var $select2Status;
var $select2Pos;

function filterColumn(i) {
    $('#mytable').DataTable().column(i).search(
        $('#col' + i + '_filter').val(),
        $('#col' + i + '_regex').prop('checked'),
        $('#col' + i + '_smart').prop('checked')
    ).draw();
}


function formatRepo(repo) {

    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection(repo) {
    return repo.text || repo.id;
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
        url: "/it_assets/get_assets_reception/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data;
            $("#myModalLabelEdit").text("修改列管资产");
            $("#modal-notify-edit").hide();
            $("#id").val(id);
            $("#show_id").hide();

            // Fill data

            initSelect2('supplier', data.supplier_id, data.supplier);
            initSelect2('pos', data.pos_id, data.pos);
            initSelect2('user', data.user, data.user);
            initSelect2('company', data.company_id, data.company);
            //initSelect2('new_organization', data.belongs_to_new_organization, data.belongs_to_new_organization);
            $("#new_organization").val(data.belongs_to_new_organization);
            $("#brand").val(data.brand);
            $("#specification").val(data.specification);
            $("#remark").val(data.remark);

            $("#myModalEdit").modal("show");
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });

};


function assets_change_history(id) {
    editFlag = true;
    var data = {
        'id': id,
    };

    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/it_assets/get_assets_change_history/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data;
            $("#myModalLabelHistory").text("查看资产变更记录");
            origin_data = data.data;
            let record = '';
            $("#myModalLabelHistory").text("查看资产变更记录");
            for (let i = 0; i < origin_data.length; i++) {
                let log = origin_data[i];
                if (log['event'] != '主机配件变更') {
                    let etime = '<p class="text-danger"><strong>' + log['etime'] + '</strong></p>';
                    let log_user = '<span>' + '<span class="text-info">录入人：</span>' + log['log_user'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let user = '<span>' + '<span class="text-info">保管人：</span>' + log['user'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let action = '<span class="text-success">' + log['event'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let number = '<span>' + '<span class="text-info">数量：</span>' + log['number'] + '个' + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<br/><br/>';
                    record = record + etime + log_user + user + action + number;
                }
                if (log['event'] == '主机配件变更') {
                    let etime = '<p class="text-danger"><strong>' + log['etime'] + '</strong></p>';
                    let log_user = '<span>' + '<span class="text-info">操作人：</span>' + log['log_user'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let ctype = '<span class="text-success">' + log['ctype'] + '修改' + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let pre_configuration = '<span>' + log['pre_configuration'] + '&nbsp;&nbsp;&nbsp;&nbsp;' + '\>>>>>' + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let current_configuration = '<span>' + log['current_configuration'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<br/><br/>';
                    record = record + etime + log_user + ctype + pre_configuration + current_configuration;
                }
            }
            $("#myModalHistoryContent").html(record)
            $("#myModalHistory").modal("show");
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });

};


// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });

function initModalSelect2() {

    $select2Ctype = $("#filter_ctype").select2({
        minimumResultsForSearch: Infinity,
    });

    $(".filter_select2").select2({
        // minimumResultsForSearch: Infinity,
    }).on("select2:select", function (e) {
        table.ajax.reload();
    });

    $select2Ctype.on("select2:select", function (e) {
        log("select2:select", e);
    });

    $select2Status = $("#filter_status").select2({
        minimumResultsForSearch: Infinity,
    });
    $select2Status.on("select2:select", function (e) {
        log("select2:select", e);
    });

    $select2Pos = $("#filter_pos").select2({
        ajax: {
            url: '/it_assets/list_pos/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
                    results: $.map(data, function (item) {
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
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    $select2Pos.on("select2:select", function (e) {
        log("select2:select", e);
    });

    $select2Supplier = $("#supplier").select2({
        ajax: {
            url: '/it_assets/list_supplier/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
                    results: $.map(data, function (item) {
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
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2Company = $("#company").select2({
        ajax: {
            url: '/it_assets/list_company_code/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                }
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
    });

    $select2User = $("#user").select2({
        ajax: {
            url: '/it_assets/list_all_users/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
                    results: $.map(data, function (item) {
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
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    // $select2NewOrganization = $("#new_organization").select2({
    //     ajax: {
    //         url: '/it_assets/list_new_organization/',
    //         dataType: 'json',
    //         type: 'POST',
    //         delay: 0,
    //         data: function (params) {
    //             return {
    //                 q: params.term, // search term
    //                 page: params.page
    //             };
    //         },
    //
    //         processResults: function (data, params) {
    //             // parse the results into the format expected by Select2
    //             // since we are using custom formatting functions we do not need to
    //             // alter the remote JSON data, except to indicate that infinite
    //             // scrolling can be used
    //             params.page = params.page || 1;
    //             return {
    //                 results: $.map(data, function (item) {
    //                     return {
    //                         id: item.id,
    //                         text: item.text,
    //                     }
    //                 })
    //                 // pagination: {
    //                 //     more: (params.page * 30) < data.total_count
    //                 // };
    //             }
    //         },
    //         cache: false,
    //     },
    //     //minimumResultsForSearch: Infinity,
    //     escapeMarkup: function (markup) {
    //         return markup;
    //     }, // let our custom formatter work
    //     // minimumInputLength: 1,
    //     // templateResult: formatRepo, // omitted for brevity, see the source of this page
    //     // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    // });

    $select2Pos2 = $("#pos").select2({
        ajax: {
            url: '/it_assets/list_pos/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
                    results: $.map(data, function (item) {
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
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}


function log(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        table.ajax.reload();

    }
}

$(document).ready(function () {

    initModalSelect2();

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/it_assets/data_shell_assets_reception/",
            "type": "POST",
            "data": function (d) {
                d.filter_ctype = $("#filter_ctype").select2('data')[0].id;
                d.filter_assets_number = $("#filter_assets_number").val();
                d.filter_name = $("#filter_name").select2('data')[0].text;
                d.filter_company = $("#filter_company").select2('data')[0].id;
                d.filter_brand = $("#filter_brand").val();
                d.filter_specification = $("#filter_specification").val();
                d.filter_new_organization = $("#filter_new_organization").select2('data')[0].text;
                d.filter_user = $("#filter_user").select2('data')[0].text;
                d.filter_status = $("#filter_status").select2('data')[0].id;
                d.filter_pos = $("#filter_pos").select2('data')[0].id;
                d.filter_supplier = $("#filter_supplier").select2('data')[0].id;
                d.filter_remark = $("#filter_remark").val();
            }
        },
        "columns": [
            {"data": null}, //0
            {"data": "id"},  // 1
            {"data": 'ctype'},  //2
            {"data": 'company'},  //3
            {"data": 'assets_number'},  // 4
            {"data": "name"},  // 5
            {"data": "brand"},  // 6
            {"data": "specification"},  // 7
            {"data": "new_organization"},  // 8
            {"data": "user"},  // 9
            {"data": "status"},  // 10
            {"data": "pos"},  // 11
            {"data": "supplier"},  // 12
            {"data": "remark"},  // 13
            {
                "data": null,
                "orderable": false,
            }
        ],
        "order": [[1, 'asc']],
        columnDefs: [
            {
                'targets': 0,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-center',
                'render': function (data, type, full, meta) {
                    return '<input type="checkbox">';
                },
            },
            {
                'targets': [1, 2],
                'visible': false,
                'searchable': false
            },
            {
                targets: 13,
                width: "10%",
                render: function (data, type, row, meta) {
                    let num = 8;
                    if (data.length > num) {
                        return '<span class="tooltip-demo"><span data-toggle="tooltip" data-placement="right" title="' + data + '">' + data.substring(1, num) + '......' + '</span></span>'
                    }
                    else {
                        return '<span>' + data + '</span>'
                    }
                }
            },
            /*{
                'targets': [4,6,7,8,9],
                "render": function(data, type, row){
                    return data.split(",").join("<br/>");
                },
            },*/
            {
                targets: 14,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                {"name": "资产变更记录", "fn": "assets_change_history(\'" + c.id + "\')", "type": "success"},
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
        initComplete: function () {
            // tooltip demo
            $('.tooltip-demo').tooltip({
                selector: "[data-toggle=tooltip]",
                container: "body"
            })
        }
    });


    // 翻页后也要重新初始化提示插件
    $('#mytable').on('draw.dt', function () {
        // tooltip demo
        $('.tooltip-demo').tooltip({
            selector: "[data-toggle=tooltip]",
            container: "body"
        })
    });


    $(':checkbox.toggle-visiable').on('click', function (e) {
        //e.preventDefault();

        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        // table.ajax.reload();
        column.visible(is_checked);
    });

    $('#bt-modal-notify').click(function () {
        $("#modal-notify").hide();
    });

    $('#chb-all').on('click', function (e) {
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked) {
                $row.addClass('selected');
                count = getSelectedTable().length;
                //makeTitle(str, count);
            } else {
                $row.removeClass('selected');
                count = 0;
                //makeTitle(str, count);
            }
        });
    });

    // Handle click on checkbox
    $('#mytable tbody').on('click', 'input[type="checkbox"]', function (e) {
        var $row = $(this).closest('tr');

        var data = table.row($row).data();
        var index = $.inArray(data[0], rows_selected);

        if (this.checked && index === -1) {
            rows_selected.push(data[0]);
        } else if (!this.checked && index !== -1) {
            rows_selected.splice(index, 1);
        }

        if (this.checked) {
            $row.addClass('selected');
            //makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            //makeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $("#bt-save").click(function (event) {
        /* Act on the event */

        var id = $("#id").val();
        var supplier = $("#supplier").select2('data')[0].id;
        var pos = $("#pos").select2('data')[0].id;
        var user = $("#user").select2('data')[0].text;
        //var new_organization = $("#new_organization").select2('data')[0].text;
        var brand = $("#brand").val();
        var specification = $("#specification").val();
        var remark = $("#remark").val();
        var company = $("#company").select2('data')[0].id;

        var inputIds = {
            'id': id,
            'supplier': supplier,
            'pos': pos,
            'user': user,
            //'new_organization': new_organization,
            'brand': brand,
            'specification': specification,
            'remark': remark,
            'company': company,
        };

        var urls = "/it_assets/edit_assets_reception/";

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {

                if (data['data']) {
                    table.ajax.reload(null, false);
                    $("#myModalEdit").modal("hide");
                } else {
                    $('#lb-msg-edit').text(data['msg']);
                    $('#modal-notify-edit').show();
                }
                ;
            }
        });
    });

    $('input.column_filter').on('keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    });

    $("#bt-reset").click(function () {
        // 重置高级搜索
        $("#filter_ctype").val('100').trigger('change');
        $("#filter_assets_number").val('');
        $("#filter_name").val('');
        $("#filter_brand").val('');
        $("#filter_specification").val('');
        $("#filter_new_organization").val('');
        $("#filter_user").val('');
        $("#filter_status").val('100').trigger('change');
        $("#filter_pos").val('0').trigger('change');
        $("#filter_remark").val('');
        $(".filter_select2").val('0').trigger('change');
        table.ajax.reload();

    });

    // 生成打印单
    $("#bt-print").confirm({
        text: "确定生成打印单?",
        confirm: function (button) {

            var selected = getSelectedTable();
            var inputs = {
                'selected': selected,
                'type': 'assets',
            };

            if (selected.length == 0) {
                alert('请勾选需要生成打印单的资产');
            } else {
                var encoded = $.toJSON(inputs);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/it_assets/create_application_form/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (result) {
                        var assets_id_list = result['assets_id_list'];
                        $.ajax({
                            type: "POST",
                            url: "/it_assets/assets_application_form/",
                            contentType: "application/json; charset=utf-8",
                            data: JSON.stringify(assets_id_list),
                            success: function (result) {
                                var w = window.open();
                                $(w.document.body).html(result);
                            }
                        });
                    },
                    error: function (errorMsg) {

                    }

                });
            }
        },

        cancel: function (button) {

        }
        ,
        confirmButton: "确定",
        cancelButton:
            "取消",

    });


});
