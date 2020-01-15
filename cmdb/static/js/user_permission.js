
var select2User;

function initModalSelect2(){
    // 初始化select2
    $select2User = $("#user").select2({
        ajax: {
            url: '/assets/list_user/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
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
        // minimumResultsForSearch: Infinity,
    });

    $select2User;
    $select2User.on("select2:select", function (e){ log("select2:select", e); });

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};

function log(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        var user_id = $("#user").select2('data')[0].id;

        pdata = {
            'user_id': user_id,
        }
        var encoded=$.toJSON( pdata );
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/users/get_user_permission/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                //console.log(data);

                // dischecked all
                $('input[type=checkbox]').map(function(){ $(this).prop('checked',false); })

                // add checked
                //data.forEach(function(info, i){ console.log(typeof $(this)); });
                data.forEach(function(info, i){ $("#"+info).prop('checked',true); });
            }
        });
    }
};


function getChecked(){
    var listChecked = new Array();
    $('input[type=checkbox]:checked').map(function(){ listChecked.push($(this).attr('id'));  });
    return listChecked;
};


$(document).ready(function() {

    initModalSelect2();

    $('input[type=checkbox]').map(function(){ $(this).prop('checked',false); });

    $("#user_permission_save").click(function(){
        var user_id = $("#user").select2('data')[0].id;
        if (user_id=='0'){
            alert('请选择用户');
            return false;
        }

        var listChecked = getChecked();


        user_permission = {
            'user_id': user_id,
            'listChecked': listChecked,
        }
        var encoded=$.toJSON( user_permission );
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/users/save_user_permission/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data['data']){
                    $.toast({
                        text: "保存成功", // Text that is to be shown in the toast
                        heading: 'Success', // Optional heading to be shown on the toast
                        icon: 'success', // Type of toast icon
                        showHideTransition: 'slide', // fade, slide or plain
                        allowToastClose: true, // Boolean value true or false
                        hideAfter: 1000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                        stack: 5, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                        position: 'top-center', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values
                        textAlign: 'left',  // Text alignment i.e. left, right or center
                        loader: true,  // Whether to show loader or not. True by default
                        loaderBg: '#9EC600',  // Background color of the toast loader
                        beforeShow: function () {}, // will be triggered before the toast is shown
                        afterShown: function () {}, // will be triggered after the toat has been shown
                        beforeHide: function () {}, // will be triggered before the toast gets hidden
                        afterHidden: function () {}  // will be triggered after the toast has been hidden
                    });
                }
                else{
                    alert(data.msg);
                }
            }
        });

    });

} );
