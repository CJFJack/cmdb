var wse;

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

    // workflow = $("#workflow_id").text();
    // initModalSelect2();

    wse = $("#wse_id").text();

    get_workflow_state_approve_process();


} );
