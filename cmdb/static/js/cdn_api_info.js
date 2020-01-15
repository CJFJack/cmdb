var table;
var str = "确定删除选中的CDN接口?";
var count = 0;

$(document).ready(function () {
    $.fn.select2.defaults.set( "theme", "bootstrap" );

    var rows_selected = [];
    table = $('#mytable').DataTable({
        columns: [
            {},
            {"data": "id"},
            {"data": "name"},
            {"data": "auth"},
            {"data": "gameproject"},
            {"data": "area"},
            {"data": "remark"},
            {},
        ],
        responsive: true,
        language: {
            "url": "/static/js/i18n/Chinese.json"
        },
        ordering: false
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
            makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            makeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    // 全选table checkbox
    $('#chb-all').on('click', function (e) {
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked) {
                $row.addClass('selected');
                count = getSelectedTable().length;
                makeTitle(str, count);
            } else {
                $row.removeClass('selected');
                count = 0;
                makeTitle(str, count);
            }
        });

    });

    //删除
    $("#bt-del").confirm({
        //text:"确定删除所选的cdn接口?",
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请先勾选需要删除的接口');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/delete_cdn_api/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            location.reload();
                        } else {
                            alert(data['msg']);
                        }
                    },
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    // 初始化select2信息
    initModalSelect2();

    // 监听认证方式选择
    $("input[name='auth']").on("click", function () {
        var value = $(this).val();
        if (value == 1) {
            $('#secretId').attr('readonly', true);
            $('#secretKey').attr('readonly', true);
            $('#token').attr('readonly', false);
        } else {
            $('#token').attr('readonly', true);
            $('#secretId').attr('readonly', false);
            $('#secretKey').attr('readonly', false);
        }
    });
    $("input[name='edit_auth']").on("click", function () {
        var value = $(this).val();
        if (value == 1) {
            $('#edit_secretId').attr('readonly', true);
            $('#edit_secretKey').attr('readonly', true);
            $('#edit_token').attr('readonly', false);
        } else {
            $('#edit_token').attr('readonly', true);
            $('#edit_secretId').attr('readonly', false);
            $('#edit_secretKey').attr('readonly', false);
        }
    });


});


// 初始化select2信息
function initModalSelect2() {
    $select2CDNSupplier = $("#cdn_supplier").select2({
        ajax: {
            url: '/assets/list_cdn_supplier/',
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

    $select2EditCDNSupplier = $("#edit_cdn_supplier").select2({
        ajax: {
            url: '/assets/list_cdn_supplier/',
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

    // 初始化项目列表
    $select2EditGameProject = $("#edit_game_project").select2({
        ajax: {
            url: '/myworkflows/list_game_project/',
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
        minimumResultsForSearch: Infinity,
        placeholder: '',
    });

    // 初始化项目列表
    $select2AddGameProject = $("#add_game_project").select2({
        ajax: {
            url: '/myworkflows/list_game_project_by_group/',
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
        minimumResultsForSearch: Infinity,
        placeholder: '',
    });

    // 列出地区
    $select2AddArea = $("#add_area").select2({
        ajax: {
            url: '/assets/list_all_area_name/',
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

    // 列出地区
    $select2EditArea = $("#edit_area").select2({
        ajax: {
            url: '/assets/list_all_area_name/',
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

}


// 新增cdn接口信息modal框
function add_cdn_info() {
    initSelect2('cdn_supplier', '0', '选择cdn供应商');
    $("input[name='auth']:checked").prop('checked', false);
    $('#token').val('');
    $('#secretId').val('');
    $('#secretKey').val('');
    $('#add_remark').val('');
    initSelect2('add_area', '', '选择接口适用地区');
    $("#add_game_project").val('').trigger('change');
    $('#secretId').attr('readonly', false);
    $('#secretKey').attr('readonly', false);
    $('#token').attr('readonly', false);
    $('#modal-notify-add-api').hide();
    $('#Modal-Add').modal('show')
}

// 修改cdn接口信息modal框
function edit_cdn_info(id) {
    $('#edit_token').val('');
    $('#edit_secretId').val('');
    $('#edit_secretKey').val('');
    $('#edit_token').attr('readonly', false);
    $('#edit_secretId').attr('readonly', false);
    $('#edit_secretKey').attr('readonly', false);
    $('#edit_cdn_api_id').attr('value', id);
    inputs = {
        'id': id,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_cdn_api_detail/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            let auth = data.auth;
            $('#edit_remark').val(data.remark);
            initSelect2('edit_cdn_supplier', data.cdn_supplier_id, data.cdn_supplier);
            initSelect2('edit_area', data.area, data.area);
            // 重新填充select2多选框
            if (data.game_project) {
                $("#edit_game_project").val('').trigger('change');
                $("#edit_game_project").html('');
                var values = new Array();
                data.game_project.forEach(function (e, i) {
                    $("#edit_game_project").append('<option value="' + e.id + '">' + e.name + '</option>');
                    values.push(e.id);
                });
                $("#edit_game_project").select2('val', values);
            }
            if (auth == 1) {
                $('#edit_token').val(data.token);
                $('#edit_secretId').attr('readonly', true);
                $('#edit_secretKey').attr('readonly', true);
                $('#edit_auth_token').prop('checked', true);
                $('#edit_auth_secret').prop('checked', false);
            } else {
                $('#edit_secretId').val(data.secret_id);
                $('#edit_secretKey').val(data.secret_key);
                $('#edit_token').attr('readonly', true);
                $('#edit_auth_secret').prop('checked', true);
                $('#edit_auth_token').prop('checked', false);
            }
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
    $('#modal-notify-edit-api').hide();
    $('#Modal-edit').modal('show')
}

// 保存新增接口信息
function save_add_cdn_api() {
    var cdn_supplier = $("#cdn_supplier").select2('data')[0].id;
    var auth = $("input[name='auth']:checked").val();
    var token = $('#token').val();
    var secret_id = $('#secretId').val();
    var secret_key = $('#secretKey').val();
    var area = $("#add_area").select2('data')[0].id;
    var remark = $('#add_remark').val();
    var game_project = $('#add_game_project').val();
    if (cdn_supplier == 0) {
        $('#lb-msg-add-api').text('请选择CDN供应商!');
        $('#modal-notify-add-api').show();
        return false;
    }
    if (auth == null) {
        $('#lb-msg-add-api').text('请选择认证方式!');
        $('#modal-notify-add-api').show();
        return false;
    }
    if (auth == 1) {
        inputs = {
            'cdn_supplier': cdn_supplier,
            'auth': auth,
            'token': token,
            'remark': remark,
            'game_project': game_project,
            'area': area,
        };
    } else {
        inputs = {
            'cdn_supplier': cdn_supplier,
            'auth': auth,
            'secret_id': secret_id,
            'secret_key': secret_key,
            'remark': remark,
            'game_project': game_project,
            'area': area,
        };
    }
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/add_cdn_api/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data['success']) {
                location.reload();
            }
            else {
                alert(data['msg'])
            }
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
}

// 保存修改接口信息
function save_edit_cdn_api() {
    var cdn_api_id = $('#edit_cdn_api_id').attr('value');
    var cdn_supplier = $("#edit_cdn_supplier").select2('data')[0].id;
    var auth = $("input[name='edit_auth']:checked").val();
    var token = $('#edit_token').val();
    var area = $("#edit_area").select2('data')[0].id;
    var secret_id = $('#edit_secretId').val();
    var secret_key = $('#edit_secretKey').val();
    var game_project = $('#edit_game_project').val();
    var remark = $('#edit_remark').val();
    if (auth == 1) {
        inputs = {
            'cdn_api_id': cdn_api_id,
            'cdn_id': cdn_supplier,
            'auth': auth,
            'token': token,
            'game_project': game_project,
            'area': area,
            'remark': remark,
        };
    } else {
        inputs = {
            'cdn_api_id': cdn_api_id,
            'cdn_id': cdn_supplier,
            'auth': auth,
            'secret_id': secret_id,
            'secret_key': secret_key,
            'game_project': game_project,
            'area': area,
            'remark': remark,
        };
    }
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/edit_cdn_api/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data['success']) {
                location.reload();
            }
            else {
                alert(data['msg'])
            }
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
}