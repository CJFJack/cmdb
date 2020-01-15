var wse;

function initModalSelect2(){
    // 初始化select2

    initGameProject();

    initProject();
    initRepo();

    myshow_svn_scheme();

    $("#applicant").select2();

    $(".permission").select2({
        /*data: [
            {'id': '读', 'text': '读'},
            {'id': '写', 'text': '写'},
            {'id': '读写', 'text': '读写'},
        ],*/
        minimumResultsForSearch: Infinity,
    });
};


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


    $("#bt-load").click( function(){
        var inputs = {
            'wse': wse,
        };

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
