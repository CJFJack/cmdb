$.fn.select2.defaults.set( "theme", "bootstrap" );
$(function () {

    //初始化节点负责人
    $select2Leader = $('#leader').select2({
        theme: "bootstrap",
        ajax: {
            url: '/assets/list_user/',
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
    });

    //初始化父节点
    $select2Parent = $('#parent').select2({
        theme: "bootstrap",
        ajax: {
            url: '/users/list_new_organization/',
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
    });

    //清空节点负责人
    $('#reset_leader').on('click', function () {
        $('#leader-option').text('');
        $('#leader-option').val(0);
        $('#select2-leader-container').text('');
    });

});



