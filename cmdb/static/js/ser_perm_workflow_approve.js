var wse;

var $select2Group;

function initModalSelect2(){
    // 初始化select2

    /*$select2Project = $('#project').select2( {
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
    });*/

    $select2Room = $("#room").select2( {
        ajax: {
            url: '/assets/list_room/',
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

    // $select2Group = $("#group").select2();

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};

function initDateTime(){
    var dt = new Date();
    var current_month = dt.getMonth() + 1
    var from = dt.getFullYear() + '-' + current_month + '-' + dt.getDate();
    var next_month = dt.getMonth() + 2
    var to = dt.getFullYear() + '-' + next_month + '-' + dt.getDate();
    $(".flatpickr").flatpickr({
        enableTime: true,
        time_24hr: true,
        // locale: "zh",
        /*disable: [
            function(date) {
                var dt = new Date();
                return (date < new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()));
            }
        ],*/
        enable: [
            {
                from: from,
                to: to,
            },
        ],
    });

    $("#start_time").val( $("#start_time").attr("data-time") );
    $("#end_time").val( $("#end_time").attr("data-time") );
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

    initModalSelect2();

    initDateTime();

    get_workflow_state_approve_process();

   
    // 提交
    $("#bt-commit").confirm({
        text:"确定提交?",
        confirm: function(button){

            $(".confirm").attr('disabled', true)

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
            }

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
            $(".confirm").attr('disabled', false)

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });
    
} );
