var wse;

$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURIComponent(results[1]) || 0;
    }
}


function show_svn_scheme(){
    var svn_scheme_id = $("#svn_scheme").select2('data')[0].id;
        var data = {
        'svn_scheme_id': svn_scheme_id,
    };

    var encoded = $.toJSON(data);
    var pdata = encoded;

    $.ajax({
        type: "POST",
        url: "/myworkflows/get_svn_scheme_data/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            // console.log(data);
            $(".cancel").remove();
            data.forEach(function(el){
                var add_str = '<div class="form-group row">' +
                                '<div class="col-sm-4">' +
                                    '<input type="text" class="form-control" readonly value='+ el.svn_repo + '>' +
                                '</div>' +
                                '<div class="col-sm-6">' +
                                    '<input type="text" class="form-control" readonly value='+ el.svn_path + '>' +
                                '</div>' +
                                '<div class="col-sm-2">' +
                                    '<input type="text" class="form-control" readonly value='+ el.svn_perm +'>' +
                                '</div>'+
                              '</div>'
                $("#insert_svn_scheme").after(add_str);

            });
        },
    });
}

function initRepo(){
    $('.repo').select2( {
        ajax: {
            url: '/myworkflows/list_svn_repo/',
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
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}


function initProject(){
    $('.svn_project').select2( {
        ajax: {
            url: '/assets/list_game_project/',
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
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function get_workflow_state_approve_process(){
    var inputs = {
        'wse': wse,
    }

    var encoded=$.toJSON( inputs );
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/workflow_state_approve_process/",
        async: true,
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            // console.log(data.data, data.current_index);
            $(".ystep1").loadStep({
                size: "large",
                color: "green",
                steps: data.data,
            });

            $(".ystep1").setStep(data.current_index + 1);
        }
    });
}

$(document).ready(function() {

    wse = $("#wse_id").text();

    get_workflow_state_approve_process();

    // get_workflow_state();

    // initProject();
    // initRepo();
    $("#svn_scheme").select2();

    show_svn_scheme();

    $(".permission").select2({
        /*data: [
            {'id': '读', 'text': '读'},
            {'id': '写', 'text': '写'},
            {'id': '读写', 'text': '读写'},
        ],*/
        minimumResultsForSearch: Infinity,
    });

    // 提交
    $("#bt-commit").confirm({
        text:"确定提交?",
        confirm: function(button){

            var transition = $('input[name=transitions]:checked').attr('id');
            var opinion = $("#opinion").val();

            if ( !transition ){
                alert('请选择审批意见!');
                return false;
            }

            var inputs = {
                'wse': wse,
                'transition': transition,
                'opinion': opinion,
            };

            var encoded=$.toJSON( inputs );
            var pdata = encoded;
            $.ajax({
                type: "POST",
                url: "/myworkflows/workflow_approve/",
                async: true,
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    if (data.success) {
                        var redirect_url = '/myworkflows/approve_list/';
                        window.location.href = redirect_url;
                    } else {
                        alert(data.data);
                        return false;
                    }
                }
            });
        },

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    $("#bt-load").click( function(){
        var inputs = {
            'wse': wse,
        }

        var encoded=$.toJSON( inputs );
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/myworkflows/test_load/",
            contentType: "application/json; charset=utf-8",
            async: true,
            data: pdata,
            beforeSend: function(){
                $("#myModal").modal("show");
                $("#modal-footer").hide();
                $("#show-msg").hide();
                $("#load").show();
            },
            success: function (data) {
                $("#load").hide();
                $("#modal-footer").show();
                $("#load-msg").text(data.data);
                $("#show-msg").show();
                
            },
            error: function(){
                $("#load").hide();
                $("#modal-footer").show();
                $("#load-msg").text(data.data);
                $("#show-msg").show();
            }
        });
    } )
    
} );
