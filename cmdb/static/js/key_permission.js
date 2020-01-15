
$.fn.showMemo = function() {
	$(this).bind('plothover', function(event, pos, item) {

		if ( !item ) { return; }

		var html = [];
		var label = item.series.label;
		var count = item.series.data[0][1];
		var mylabel = label + '数量: ' + count;

		if ( $(this).attr('id') == 'flotcontainer_key_user' ) {
			if ( label == 'root用户' ) {
				var str = '<a href=/assets/user_host_list/?filter_r_status=1>' + mylabel + '</a>';
			} else {
				var str = '<a href=/assets/user_host_list/?filter_r_status=0>' + mylabel + '</a>';
			}
			html.push(str);
			$("#test").html(html.join(''));
		} else if ( $(this).attr('id') == 'flotcontainer_key_time' ) {
			if ( label == '永久' ) {
				var str = '<a href=/assets/user_host_list/?filter_t_status=0>' + mylabel + '</a>';
			} else {
				var str = '<a href=/assets/user_host_list/?filter_t_status=1>' + mylabel + '</a>';
			}
			html.push(str);
			$("#test2").html(html.join(''));
		} else if ( $(this).attr('id') == 'room_flotcontainer' ) {
			var next_element = $(this).next();
			var id = item.series.id;
			var str = '<a href=/assets/user_host_list/?filter_room=' + id + '>' + mylabel + '</a>';
			html.push(str);
			$(next_element).html(html.join(''));
		} else if ( $(this).attr('id') == 'project_flotcontainer' ) {
			var next_element = $(this).next();
			var id = item.series.id;
			var str = '<a href=/assets/user_host_list/?filter_game_project=' + id + '>' + mylabel + '</a>';
			html.push(str);
			$(next_element).html(html.join(''));
		} else if ( $(this).attr('id') == 'group_flotcontainer' ) {
			var next_element = $(this).next();
			var id = item.series.id;
			var str = '<a href=/assets/user_host_list/?filter_group=' + id + '>' + mylabel + '</a>';
			html.push(str);
			$(next_element).html(html.join(''));
		}

	});
};

function initPlot(selector, data) {
	var options = {
		series: {
	        pie: {
	            show: true,
	        }
	    },
	    legend: {
	        show: false
	    },
	    grid: {
    		hoverable: true
		},
	};

	if ( $(selector).attr('id') == 'flotcontainer_key_time' ) {
		data.forEach( function(e, i){
			if ( e.label == '永久' ) { e.color = '#FF4633' }
			if ( e.label == '临时' ) { e.color = '#1ABC9C' }
		} );
	}

	$.plot(selector, data, options);
	selector.showMemo();
}


function initPlotDetail(selector, data) {
	var options = {
		series: {
	        pie: {
	            show: true,
	            // innerRadius: 0.5,
	            radius: 1,
	            label: {
	                show: true,
	                radius: 2/3,
	                // formatter: labelFormatter,
	                threshold: 0.05
	            }
	        }
	    },
	    grid: {
    		hoverable: true
		},
		legend: {
	        // show: false
	    }
	};

	$.plot(selector, data, options);
	selector.showMemo();
}

function initMorrisBar(id, data){
    Morris.Bar({
        element: id,
        xLabelMargin: 10,
        xLabelAngle: 30,
        resize: true,
        xkey: 'name',
        ykeys: ['number'],
        labels: ['number'],
        data: data,
        gridTextColor: ['#800'],
        hoverCallback: function (index, options, content, row) {

            var filter_id = options.element;
            var id = row.id;

            if ( filter_id == 'room-id' ) {
            	var _url = '/assets/user_host_list/?filter_room=' + id;
            } else if ( filter_id == 'project-id' ) {
            	var _url = '/assets/user_host_list/?filter_game_project=' + id;
            } else if ( filter_id == 'group-id' ) {
            	var _url = '/assets/user_host_list/?filter_group=' + id;
            } 

            content += "<a href=" + _url + "><div class='mylink'>" + '查看详情' + "</div></a>";
            return content;
        }
    });
}

// 获取机房，部门，项目的数据
function fill_bar_data(id){
    var data = {
        'id': id,
    };

    var encoded = $.toJSON(data);
    var pdata = encoded;

    $.ajax({
        url: '/assets/permission_data_detail/',
        type: 'POST',
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            if ( data.length > 0 ){
                initMorrisBar(id, data);
            }
        },
    });    
    
}

$(document).ready(function() {

	$.ajax({
        type: "POST",
        url: "/assets/data_key_permission_type/",
        contentType: "application/json; charset=utf-8",
        success: function(data){
        	initPlot( $("#flotcontainer_key_user"), data.data_user );
        	initPlot( $("#flotcontainer_key_time"), data.data_time );
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });

    $(".bar-example").each( function(index, e){
    	var id = $(e).attr('id');
        fill_bar_data(id);
    } );

    $(".myflotcontainer").each( function(index, e){
    	var id = $(e).attr('id');
    	var data = {
        	'id': id,
    	};

    	var selector = $(this);

    	var encoded = $.toJSON(data);
    	var pdata = encoded;
    	$.ajax({
	        type: "POST",
	        data: pdata,
	        url: "/assets/permission_data_detail_pie/",
	        contentType: "application/json; charset=utf-8",
	        success: function(data){
	        	initPlotDetail( selector, data );
	        },
	    });

    } );
	
});