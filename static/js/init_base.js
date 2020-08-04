  $(document).ready(function(){
     // initlayout and core plugins

    App.init(); // initlayout and core plugins

    //初始化下一级下拉框，动态加载
    var csrftoken = getCookie("csrftoken");

    $.ajax({
    type: 'post',
    url: '/manager/plist',
    timeout: 5000, //超时时间设置，单位毫秒
    beforeSend:function(xhr, settings){xhr.setRequestHeader("X-CSRFToken",csrftoken)},
    success: function (data) {
        var arr = JSON.parse(data);
        for(var i=0;i<arr.length;i++){
            $("#base_project_id").append("<option value='"+arr[i].project_id+"'>"+arr[i].project_name+"</option>");
        }

        //从cooki中取上次的下拉框值,并设置选中状态
        if(getCookie("p_id")!="null")
            {
                //$("#base_project_id").find("option[value = '"+json.project_id+"']").attr("selected","selected");
                $("#base_project_id").find("option[value = '"+getCookie("p_id")+"']").attr("selected","selected");

                //调用获取版本下拉框
                getVersionlist(getCookie("p_id"))
            }
        if(typeof getCookie("p_id")!="undefined")
        {
                var project_id=($("#base_project_id").val());
                addCookie("p_id",project_id,200)
                getVersionlist(project_id)
            //location.replace(location.href);
               // window.location.reload();
        }
        else
            {
                addCookie("p_id","",200)
            }
    }

});
    });

//二级下拉框的选项随一级下拉框的值而改变
  $(function(){
  $("#base_project_id").change(function(){
   //获取当前选中的下拉框的value值
      var project_id=($("#base_project_id").val());
    //保存在cookie中，键名为project_id
      //document.cookie = 'project_id =' + project_id;
      addCookie("p_id",project_id,200)
      getVersionlist(project_id)
      //location.replace(location.href);
      window.location.reload();

  });

  $("#base_version_id").on('change', function() {

      var version_id=($("#base_version_id").val());

      //document.cookie = 'version_id =' + version_id;//保存在cookie中，
      addCookie("v_id",version_id,200)
      window.location.reload();


  });

 });

 //获取版本列表
  function getVersionlist(project_id) {
     var csrftoken = getCookie("csrftoken");

    $.ajax({
        type: 'post',
        url: '/manager/VersionList',
        data:
            {
                project_id:project_id
            },
        timeout: 5000, //超时时间设置，单位毫秒
       beforeSend:function(xhr, settings){xhr.setRequestHeader("X-CSRFToken", csrftoken)},
       success: function (data) {

        var arr = JSON.parse(data);

        //如果一级没有对应的二级 则清空二级并 不往下执行

        if(arr.length == 0){
            //清空 下拉框base_version_id:
            $("#base_version_id").empty();
            //删除cookie，
            //delCookie("v_id");
            addCookie("v_id","",200)

            return ;
         }
        //如果一级有对应的二级 则进行拼接，每次拼接前都进行清空

        else {
                $("#base_version_id").empty();

                for(var i=0;i<arr.length;i++){
                    $("#base_version_id").append("<option value='"+arr[i].version_id+"'>"+arr[i].version_name+"</option>");
                    if (arr[i].version_id=getCookie("v_id"))
                    {
                        $("#base_version_id").find("option[value = '"+getCookie("v_id")+"']").attr("selected","selected");
                    }
                }

                var version_id=($("#base_version_id").val());

                addCookie("v_id",version_id,200)//保存在cookie中，


                }

        }

       });

 };

//添加cookie
  function addCookie(objName,objValue,objHours){
    var str = objName + "=" + escape(objValue);
    if(objHours > 0){ // 如果不设定过期时间, 浏览器关闭时cookie会自动消失
        var date = new Date()
        var ms = objHours * 3600 * 1000;

        date.setTime(date.getTime() + ms);
        str += "; expires=" + date.toGMTString() + "; path=/;"; // 指定了cookie的path
    }

    document.cookie = str;
}
//获取cookie
  function getCookie(objName) {
        var arrStr = document.cookie.split("; ");

        for (var i = 0; i < arrStr.length; i ++) {
            var temp = arrStr[i].split("=");

            if(temp[0] == objName) return unescape(temp[1]);
        }
    }

//删除cookie
  function delCookie(objName) {
        var exp = new Date();
        exp.setTime(exp.getTime() - 1);
        var cval = getCookie(objName);
        if (cval != null) {
            document.cookie = objName + "=" + cval + "; expires=" + exp.toGMTString() + "; path=/;"; // 指定了cookie的path
        }
    }