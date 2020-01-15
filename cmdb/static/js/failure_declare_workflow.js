var workflow;
var $select2Applicant;
var $select2AssignedTo;
var $select2Classification;


function initModalSelect2(){
    $select2Applicant = $("#applicant").select2({
        ajax: {
            url: '/assets/list_user/',
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
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2Classification = $("#classification").select2({
        minimumResultsForSearch: Infinity,
    }).on("select2:select", function (e) { $("#assigned_to").val('0').trigger('change'); });

    $select2AssignedTo = $("#assigned_to").select2({
        ajax: {
            url: '/assets/list_administrator/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    classification: $("#fail_class option:selected").val(),
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
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
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

function checkBefore(applicant, title, content, fail_class){

    if (applicant == '0'){
        alert('请选择申请人');
        return false;
    }

    if (title == ''){
        alert('请输入标题');
        return false;
    }

    if ($('input:radio[name="fail_class"]:checked').val() == null){
        alert('请选择故障分类');
        return false;
    }

    if (content == ''){
        alert('请输入内容');
        return false;
    }


    return true;

}


$(document).ready(function() {

    workflow = $("#workflow_id").text();
    initModalSelect2();

    // 提交
    $("#bt-commit").confirm({
        text:"确定提交到下一步?",
        confirm: function(button){

            var applicant = $("#applicant").select2('data')[0].id;
            var title = $("#title").val();
            //var classification = $("#classification").select2('data')[0].id;
            var classification = $("input[name='fail_class']:checked").val();
            var content = $("#content").val();

            var assigned_to = $("#assigned_to").select2('data')[0].id;
            

            var result = checkBefore(applicant, title, content);

            var inputs = {
                'applicant': applicant,
                'title': title,
                'classification': classification,
                'content': content,
                'assigned_to': assigned_to,
                'workflow': workflow,
            }

            var encoded=$.toJSON( inputs );
            var pdata = encoded;

            if ( result ){
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/start_workflow/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        if (data.success) {
                            var redirect_url = '/myworkflows/apply_history/';
                            window.location.href = redirect_url;
                        } else {
                            alert(data.data);
                        }
                    }
                });
            }
        },

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

} );
