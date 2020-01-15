var company_name;
var company_id;

function initMorrisBar(status_code, data){
    Morris.Bar({
        element: status_code,
        xLabelMargin: 10,
        xLabelAngle: 30,
        resize: true,
        xkey: 'name',
        ykeys: ['number'],
        labels: ['number'],
        data: data,
        gridTextColor: ['#800'],
        hoverCallback: function (index, options, content, row) {

            var status_code = options.element;
            var name = row.name;

            if ( name.indexOf('-') == -1 ) {
                var _url = '/it_assets/assets_reception/'
            } else {
                var _url = '/it_assets/sub_assets_reception/'
            }

            _url += '?name=' + name + '&status_code=' + status_code + '&company_id=' + company_id;

            content += "<a href=" + _url + "><div class='mylink'>" + '查看详情' + "</div></a>";
            return content;
        }
    });
}


// 获取公司下状态的所有资产的库存
function fill_bar_data(status_code, company_name){
    var data = {
        'status_code': status_code,
        'company_name': company_name,
    };

    var encoded = $.toJSON(data);
    var pdata = encoded;

    $.ajax({
        url: '/it_assets/assets_data_detail/',
        type: 'POST',
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            if ( data.length > 0 ){
                initMorrisBar(status_code, data);
            }
        },
    });    
    
}


$(document).ready(function() {
    company_name = $("#company_name").html();
    company_id = $("#company_id").html();

    $(".bar-example").each( function(index, e){
        var status_code = $(e).attr('id');
        fill_bar_data(status_code, company_name);
    } );

} );
