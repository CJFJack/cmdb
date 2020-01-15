var table;
var addSelect2='';
var addSelect3='';
//var uuid='ff80d0ef-4ace-4559-85ea-4d29eb803c56';
var uuid='table';

var current_project;
pre_project = '';
var select2;
//var root_count = 0;
var selected_project;
var new_agrs;
//var next_nodes = []


$(document).ready(function (){
    table = $("#usage").DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/dashboard/get_project_device",
            "data": function (d){
                d.uuid = uuid;
            },
            "type": "POST"
        },
        "columns": [
            {"data": "name" },
            {"data": "belong_project"},
            {"data": "intranet_ip"},
            {"data": "internet_ip"},
            {"data": "cpu_puse"},
            {"data": "eth0_traffic"},
            {"data": "eth1_traffic"},
            {"data": "disk_puse"},
            {"data": "iowait"},
            {"data": "load"},
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });
    
    //console.log('before count'+root_count);

    function show_device(args){
        uuid = JSON.parse(args).data.id;
        console.log('in show_device');
        table.ajax.reload();
    }

    function show (name, evt) {
        if (!evt) {
            var args = "{}";
        } else {
            var args = JSON.stringify(evt.params, function (key, value) {
                if (value && value.nodeName) return "[DOM node]";
                if (value instanceof $.Event) return "[$.Event]";
                return value;
            });
            show_device(args);
        }

    };

    var $select2 = $('#root').select2( {
        ajax: {
            url: "/dashboard/get_project",
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: current_project,
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
            cache: true,
        },
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2;
    $select2.on("select2:select", function (e) { log("select2:select", e, $(this)); });
    $select2.on("select2:open", function (e) { log("select2:open", e, $(this)); });


    function clear_next(dom){
        next_node = dom.next();
        if (next_node[0].className == "btn-group"){
            //next_nodes.push(next_node);
            next_node.remove();
            return clear_next(dom);
        } else {
            return;
        }
    }

    function get_pre_node_id(dom){
        if (dom.parent().prev().length == 0){
            //console.log('root');
            return null;
        } else{
            pre_node_id = dom.parent().prev().children().val();
            return pre_node_id;
        }
    }

    function has_next(dom){
        if (dom.parent().next()[0].className == "btn-group"){
            return true;
        } else {
            return false;
        }
    }

    function log (name, evt, dom) {
        //console.log(dom);
        if (!evt) {
            var args = "{}";
        } else {
            var args = JSON.stringify(evt.params, function (key, value) {
            if (value && value.nodeName) return "[DOM node]";
            if (value instanceof $.Event) return "[$.Event]";
            return value;
            });
        }
        //pre_project = {'data': {'id': get_pre_node_id(dom)}};
        //pre_project = $.toJSON(pre_project);
        //console.log('out of name', pre_project);
        if (name == "select2:open"){
            /*$('.js-data-example-ajax').on("select2:select", function (e) { log("select2:select", e, $(this)); });
            $('.js-data-example-ajax').on("select2:open", function (e) { log("select2:open", e, $(this)); });*/
        }
        if (name == "select2:select"){
            clear_next(dom.parent());   //首先清除兄弟节点
            show_device(args);
            
            $.ajax({
                url: "/dashboard/get_project",
                dataType: 'json',
                type: 'POST',
                delay: 250,
                data: args,   //这里会post当前的项目id
                success: function(data){
                    //console.log(data);
                    if (data.length !=0 ){
                        // 如果还存在子项目的话,需要重新生成子项目选项
                        //console.log('ok');
                        /*if (has_next(dom)){
                            var new_agrs = pre_project;
                            console.log('has_next');
                        }
                        else {
                            var new_agrs = args;
                        }*/
                        console.log(new_agrs);
                        clear_next(dom.parent());
                        addSelect = '<div class="btn-group" style="width: 90px"><select class="js-data-example-ajax"><option selected="selected">选择名称</option></select></div>'
                        dom.parent().after(addSelect);
                        var parent_node = dom.parent().next().children();
                        parent_node.select2( {
                            ajax: {
                                url: "/dashboard/get_project",
                                dataType: 'json',
                                type: 'POST',
                                delay: 250,
                                data: args,   //根据上一个项目的id来请求子项目
                                processResults: function (data, params) {
                                    // parse the results into the format expected by Select2
                                    // since we are using custom formatting functions we do not need to
                                    // alter the remote JSON data, except to indicate that infinite
                                    // scrolling can be used
                                    params.page = params.page || 1;
                                    if (data['data']){
                                        //show_device(args)
                                    }else{
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
                                    }
                                },
                                cache: true,
                            },
                            minimumResultsForSearch: Infinity,
                            escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
                            // minimumInputLength: 1,
                            templateResult: formatRepo, // omitted for brevity, see the source of this page
                            templateSelection: formatRepoSelection // omitted for brevity, see the source of this page
                        });
                        $('.js-data-example-ajax').on("select2:select", function (e) { log("select2:select", e, $(this)); });
                        $('.js-data-example-ajax').on("select2:open", function (e) { log("select2:open", e, $(this)); });
                    }
                }
            });
            
        }
    };

    

    function formatRepo (repo) {
        var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

        return markup;
    };

    function formatRepoSelection (repo) {
        return repo.text || repo.id;
    };

    
});