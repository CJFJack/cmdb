
// 时间戳
var ts;
var pro;
var result;

$(document).ready(function() {

    $("#add").confirm({
        text: '确定新增导入数据?excel表格里面的内容将会全部新增到cmdb中',
        confirm: function(button){
            var fpath = $("#mytable tr td")[0].innerHTML;
            var action = "add";
            ts = new Date().getTime();
            var pdata = {
                'fpath': fpath,
                'action': action,
                'ts': ts,
            };
            var pdata=$.toJSON( pdata );

            //添加进度条
            /*$("#pro-bar").append('<div class="pro"></div><div class="result"></div>');

            result = document.getElementsByClassName('result')[0];

            pro = new progress({
                width : 200,//进度条宽度
                height: 30,//进度条高度
                bgColor : "#3E4E5E",//背景颜色
                proColor : "#009988",//前景颜色
                fontColor : "#FFFFFF",//显示字体颜色
                val : 1,//默认值
                text:"当前进度为#*val*#%",//显示文字信息
                showPresent : true,
                completeCallback:function(val){
                    result.innerHTML = '已完成';
                },
                changeCallback:function(val){
                    result.innerHTML = '当前进度为'+val+'%';
                }
            });

            document.getElementsByClassName('pro')[0].appendChild(pro.getBody());

            $.ajax({
                type: "POST",
                url: "/assets/import_data/",
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    if (data['data']) {
                        $("#ImportResult").val('全部数据导入成功');
                    }else{
                    $("#ImportResult").val(data.msg);
                    }
                }
            });

            get_percentage(pro);*/

            $.ajax({
                type: "POST",
                url: "/assets/import_data/",
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    if (data['data']) {
                        $("#ImportResult").val('全部数据导入成功');
                    }else{
                    $("#ImportResult").val(data.msg);
                    }
                }
            });

        },

        cancel: function(button){
            //console.log('cancel');
        },
        confirmButton: "确定",
        cancelButton: "取消",
    });

    

    $("#update").confirm({
        text: '确定更新导入数据?excel里面的数据将会更新到cmdb中',
        confirm: function(button){
            var fpath = $("#mytable tr td")[0].innerHTML;
            var action = "update";
            ts = new Date().getTime();
            var pdata = {
                'fpath': fpath,
                'action': action,
                'ts': ts,
            };
            var pdata=$.toJSON( pdata );

            //添加进度条
            $("#pro-bar").append('<div class="pro"></div><div class="result"></div>');

            result = document.getElementsByClassName('result')[0];

            pro = new progress({
                width : 200,//进度条宽度
                height: 30,//进度条高度
                bgColor : "#3E4E5E",//背景颜色
                proColor : "#009988",//前景颜色
                fontColor : "#FFFFFF",//显示字体颜色
                val : 1,//默认值
                text:"当前进度为#*val*#%",//显示文字信息
                showPresent : true,
                completeCallback:function(val){
                    result.innerHTML = '已完成';
                },
                changeCallback:function(val){
                    result.innerHTML = '当前进度为'+val+'%';
                }
            });

            document.getElementsByClassName('pro')[0].appendChild(pro.getBody());

            $.ajax({
                async: true,
                type: "POST",
                url: "/assets/import_data/",
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    if (data['data']) {
                        $("#ImportResult").val('全部数据更新成功');
                    }else{
                    $("#ImportResult").val(data.msg);
                    }
                }
            });

            get_percentage(pro);

        },

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",
    });

    $("#clear").click(function(){
        $("#ImportResult").val('');
        $('.pro').remove();
        $('.result').remove();
    });

    function get_percentage(pro){
        var urls = "/assets/import_data/?ts=" + ts;
        $.ajax({
            type: "GET",
            url: urls,
            success: function( data ){
                if (data['finished'] == data['records_total']){
                    pro.update(100);
                    return false;
                }else{
                    var percentage = data['finished']/data['records_total'] * 100;
                    pro.update(Math.ceil(percentage));
                    setTimeout(get_percentage, 1000, pro);
                }
            },
            // 发生错误以后，继续
            error: function (data){
                setTimeout(get_percentage, 1000, pro);
            }
        });
    };

} );
