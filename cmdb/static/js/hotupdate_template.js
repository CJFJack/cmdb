var $select2_project;
function initModalSelect2(){
    // 初始化select2

    $select2_project = $('#project').select2( {
        ajax: {
            url: '/myworkflows/list_game_project_by_group/',
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
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
    });

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};

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
    initModalSelect2();

    $("#bt-go").click(function(event) {
        /* Act on the event */
        var project = $("#project").val();
        if ( project == '0' ) {
            alert('请选择游戏项目!');
            return false;
        }
        var workflow = $.urlParam('workflow');
        var _url = '/myworkflows/start_hotupdate?workflow=' + workflow + '&project=' + project;
        location.href = _url;
    });
} );
