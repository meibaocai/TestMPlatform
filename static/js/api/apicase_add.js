       var csrftoken = getCookie("csrftoken");
       let $table_param = $('#table_param');
       let $add_param = $('#add_param');
       let $get_param = $('#get_param');
       let $del_param = $('#del_param');
       let $del_data= $('#del_data');
       //定义保存参数状态
       let save_status = 0;

       //消息中的头部/cookie/参数/返回消息取值表
       let $table_head = $('#table_head');
       let $table_Cookies = $('#table_Cookies');
       let $table_request_param = $('#table_request_param');
       let $table_response_param = $('#table_response_param');

       let $table_data = $('#table_data');
       let $add_data = $('#add_data');
       let $getdatasource = $('#getdatasource');
       //准备表头数据：
       var param_Columns = [{checkbox:true},{field:'param', title:'参数名称'}];
       var data_Columns = [{checkbox:true,field:'checkbox'},
           {
                    title: '序号',
                    field: 'ID',
                    align: 'center',
                    valign: 'middle',
                    width:50,
                    formatter: function (value, row, index) {
                    return index + 1;}
            }
       ];
        //准表数据：
       var table_param_data=[];
       var table_data_data=[];
        //准备request的头部/cookie/参数/返回消息取值表 公共表头数据：
       var request_public_Columns =  [{checkbox:true},{field:'param_name', title:'参数名称'},{field:'param_value', title:'参数取值'}];
       //准备request的头部/cookie/参数/返回消息取值表 公共表数据：
       var table_head_data=[];
       var table_Cookies_data=[];
       var table_request_param_data=[];
       var table_response_param_data=[];

        //$('#table_data').bootstrapTable('destroy');   //动态加载表格之前，先销毁表格
       //$('#table_param').bootstrapTable('destroy');   //动态加载表格之前，先销毁表格
        //表格初始化
       $('#table_param').bootstrapTable({
           columns: param_Columns,  //表头
           data:table_param_data, //表格中的数据,这是从本地取得数据，如果是从后台取数据，就应该改为后台地址
           clickEdit: true,
           striped: true,                      //是否显示行间隔色
           clickToSelect: true,                //是否启用点击选中行
           halign: 'center',  // 设置表头标题对齐方式可选项
           valign: 'middle',   // 设置单元格数据的垂直方向上的对齐方式
           checkbox:true,
           /**
            * @param {点击列的 field 名称} field
            * @param {点击列的 value 值} value
            * @param {点击列的整行数据} row
            * @param {td 元素} $element
            */
           onClickCell: function(field, value, row, $element) {
               $element.attr('contenteditable', true);
               $element.blur(function() {
                   let index = $element.parent().data('index');
                   let tdValue = $element.html();
                   let old_value = value;
                   //old_value修改前的参数值，如何不设置save_status状态，saveDate方法会执行多次
                   if (save_status !=1) {
                       saveData(index, field, tdValue,old_value);
                       save_status = 1;
                   }
               })
               save_status = 0;
           }
       });

       $('#table_data').bootstrapTable({//表格初始化
                            columns: data_Columns,  //表头
                            data:table_data_data, //表格中的数据,这是从本地取得数据，如果是从后台取数据，就应该改为后台地址
                            clickEdit: true,
                            striped: true,                      //是否显示行间隔色
                            clickToSelect: true,  //点击row选中radio或CheckBox
                            halign: 'center',  // 设置表头标题对齐方式可选项
                            valign: 'middle',   // 设置单元格数据的垂直方向上的对齐方式
                            checkbox:true,
                           /**
                            * @param {点击列的 field 名称} field
                            * @param {点击列的 value 值} value
                            * @param {点击列的整行数据} row
                            * @param {td 元素} $element
                            */
                            onClickCell: function(field, value, row, $element) {
                                    $element.attr('contenteditable', true);
                                    $element.blur(function() {
                                        let index = $element.parent().data('index');
                                        let tdValue = $element.html();
                                        saveDataResource(index, field, tdValue);
                                    })
                                }

                        });

       $table_head.bootstrapTable({//表格初始化
           columns: request_public_Columns,  //表头
           data:table_head_data, //表格中的数据,这是从本地取得数据，如果是从后台取数据，就应该改为后台地址
           clickEdit: true,
           striped: true,                      //是否显示行间隔色
           clickToSelect: true,                //是否启用点击选中行
           halign: 'center',  // 设置表头标题对齐方式可选项
           valign: 'middle',   // 设置单元格数据的垂直方向上的对齐方式
           checkbox:true,
           /**
            * @param {点击列的 field 名称} field
            * @param {点击列的 value 值} value
            * @param {点击列的整行数据} row
            * @param {td 元素} $element
            */
           onClickCell: function(field, value, row, $element) {
               $element.attr('contenteditable', true);
               $element.blur(function() {
                   let index = $element.parent().data('index');
                   let tdValue = $element.html();
                   let old_value = value;
                   let table_name = $table_head;
                   //old_value修改前的参数值
                   save_req_Data(index, field, tdValue,old_value,table_name);

               })
           }
       });
       $table_Cookies.bootstrapTable({//表格初始化
           columns: request_public_Columns,  //表头
           data:table_Cookies_data, //表格中的数据,这是从本地取得数据，如果是从后台取数据，就应该改为后台地址
           clickEdit: true,
           striped: true,                      //是否显示行间隔色
           clickToSelect: true,                //是否启用点击选中行
           halign: 'center',  // 设置表头标题对齐方式可选项
           valign: 'middle',   // 设置单元格数据的垂直方向上的对齐方式
           checkbox:true,
           /**
            * @param {点击列的 field 名称} field
            * @param {点击列的 value 值} value
            * @param {点击列的整行数据} row
            * @param {td 元素} $element
            */
           onClickCell: function(field, value, row, $element) {
               $element.attr('contenteditable', true);
               $element.blur(function() {
                   let index = $element.parent().data('index');
                   let tdValue = $element.html();
                   let old_value = value;
                   let table_name = $table_Cookies;
                   //old_value修改前的参数值
                   save_req_Data(index, field, tdValue,old_value,table_name);

               })
           }
       });
       $table_request_param.bootstrapTable({//表格初始化
           columns: request_public_Columns,  //表头
           data:table_request_param_data, //表格中的数据,这是从本地取得数据，如果是从后台取数据，就应该改为后台地址
           clickEdit: true,
           striped: true,                      //是否显示行间隔色
           clickToSelect: true,                //是否启用点击选中行
           halign: 'center',  // 设置表头标题对齐方式可选项
           valign: 'middle',   // 设置单元格数据的垂直方向上的对齐方式
           checkbox:true,
           /**
            * @param {点击列的 field 名称} field
            * @param {点击列的 value 值} value
            * @param {点击列的整行数据} row
            * @param {td 元素} $element
            */
           onClickCell: function(field, value, row, $element) {
               $element.attr('contenteditable', true);
               $element.blur(function() {
                   let index = $element.parent().data('index');
                   let tdValue = $element.html();
                   let old_value = value;
                   let table_name = $table_request_param;
                   //old_value修改前的参数值
                   save_req_Data(index, field, tdValue,old_value,table_name);

               })
           }
       });
       $table_response_param.bootstrapTable({//表格初始化
           columns: request_public_Columns,  //表头
           data:table_response_param_data, //表格中的数据,这是从本地取得数据，如果是从后台取数据，就应该改为后台地址
           clickEdit: true,
           striped: true,                      //是否显示行间隔色
           clickToSelect: true,                //是否启用点击选中行
           halign: 'center',  // 设置表头标题对齐方式可选项
           valign: 'middle',   // 设置单元格数据的垂直方向上的对齐方式
           checkbox:true,
           /**
            * @param {点击列的 field 名称} field
            * @param {点击列的 value 值} value
            * @param {点击列的整行数据} row
            * @param {td 元素} $element
            */
           onClickCell: function(field, value, row, $element) {
               $element.attr('contenteditable', true);
               $element.blur(function() {
                   let index = $element.parent().data('index');
                   let tdValue = $element.html();
                   let old_value = value;
                   let table_name = $table_response_param;
                   //old_value修改前的参数值
                   save_req_Data(index, field, tdValue,old_value,table_name);

               })
           }
       });


        // 新增参数param
       $add_param.click(function() {

           //返回10-100的随机数
           var new_param ='New'+ getRandom(1, 100)+ getRandom(1, 10);
           //获取表格行数rows
           var rows=$($table_param).bootstrapTable("getData").length;
           $table_param.bootstrapTable('insertRow', {
                   index: rows,
                   row: {
                       param: new_param,
                   },
               })
           // 向table_data表头最后插入表头
           data_Columns.push({field: new_param, title: new_param});
           //获取表格的行数
           var data_rows=$table_data.bootstrapTable("getData").length;
           //判断table_data表的行数，并写入行数据
           if(data_rows == 0) {
               table_data_data = [];
           }
           else
           {
               for(var j=0;j<data_rows;j++)
               {
                   table_data_data.forEach((val)=> {
                       if(val.hasOwnProperty(new_param)){
                       }
                       else {
                           // 增加一个新属性
                            val[new_param]='';
                       }
                   })
               }
           }
           $("#table_data").bootstrapTable('refreshOptions', {
                   columns:data_Columns,
                   data:table_data_data,
           });


       })

       function AddParam(table_name){
               //返回10-100的随机数
           var new_param ='New'+ getRandom(1, 100)+ getRandom(1, 10);
           //获取表格行数rows
           var rows=$(table_name).bootstrapTable("getData").length;
           table_name.bootstrapTable('insertRow', {
                   index: rows,
                   row: {
                       param_name: new_param,
                       param_value:"",
                   },
               })
       }

       // 新增table_data数据
       $add_data.click(function() {
           if(data_Columns.length >2) {
               var data_obj = {}; //或者 var obj=new Object();
               for (var i in  data_Columns) {
                   //alert(i)//显示的是 1、2、3等数值
                   //alert(data[i]);//显示为[object,object],不是我们想要的
                   //var Columns_name = data_Columns[i].field  //显示name属性的值
                   data_obj[data_Columns[i].field] = '';
               }
               table_data_data.push(data_obj);
               //alert(table_param_data)
               //$('#table_data').bootstrapTable('prepend', JSON.stringify(data_obj)); //将对象转换成字符串（利用JSON.stringify(zongObj);）
               $('#table_data').bootstrapTable('refreshOptions', {
                   columns: data_Columns,
                   data: table_data_data,
               })
           }
           else {
               alert("请先新增参数！")
               return;
           }

       })

       //获取table_param表json类型数据
       $get_param.click(function() {
               alert(JSON.stringify($table_param.bootstrapTable('getData')).replace(/^\s+|\s+$/g,"").replace(/<\/?.+?>/g,""));
       });

       //获取table_data表json类型数据
       $getdatasource.click(function() {
           //return JSON.stringify($table_param.bootstrapTable('getData'));
           alert(JSON.stringify($table_data.bootstrapTable('getData')).replace(/^\s+|\s+$/g,"").replace(/<\/?.+?>/g,""));
       });

        // 删除参数param
        // 删除参数param
       $del_param.on("click", function() {
        if (!confirm("是否确认删除？"))
            return;
        var rows = $("#table_param").bootstrapTable('getSelections');// 获得要删除的数据
        if (rows.length == 0) {// rows 主要是为了判断是否选中，下面的else内容才是主要
            alert("请先选择要删除的记录!");
            return;
        }
        else {
            $(rows).each(function () {// 通过获得别选中的来进行遍历
                $table_param.bootstrapTable('remove', {
                    field: 'param',//对应该字段param的columns的field
                    values: this.param,//字段param的值
                })
                ReSetDataResource("del",0,this.param);
            })
        }

    })

       //request请求删除参数
       function DelParam(request_table){
        if (!confirm("是否确认删除？"))
            return;
        //var rows = $("#table_param").bootstrapTable('getSelections');// 获得要删除的数据
        var rows = request_table.bootstrapTable('getSelections');// 获得要删除的数据

        //console.log(rows)
        if (rows.length == 0) {// rows 主要是为了判断是否选中，下面的else内容才是主要
            alert("请先选择要删除的记录!");
            return;
        }
        else {
            $(rows).each(function () {// 通过获得别选中的来进行遍历
                request_table.bootstrapTable('remove', {
                    field: 'param_name',//对应该字段param的columns的field
                    values: this.param_name,//字段param的值
                })
            })
        }
       }

       // 删除table_data数据
       $del_data.on("click", function() {
        if (!confirm("是否确认删除？"))
            return;
        var rows = $("#table_data").bootstrapTable('getSelections');// 获得要删除的数据
        //console.log(rows);
        if (rows.length == 0) {// rows 主要是为了判断是否选中，下面的else内容才是主要
            alert("请先选择要删除的记录!");
            return;
        }
        else {
            $(rows).each(function () {// 通过获得别选中的来进行遍历
                $table_data.bootstrapTable('remove', {
                    field: 'checkbox',//对应该字段param的columns的field
                    values: "true",//字段param的值
                })
            })

        }

    })

       // 删除和修改param参数后，重新设置table_data的表头和表的行数据
       function ReSetDataResource(type,col_num=null,data_column,old_value=null) {

           //删除table_data的表头
           if (type == "del") {
               data_Columns.forEach(function (item, index) {
                   if (item.field == data_column) {
                       //alert(item.field);
                       //alert(index);
                       data_Columns.splice(index, 1);
                   }

               })

               //table_data_data = JSON.stringify($table_data.bootstrapTable('getData'));
               //获取表格的行数
               var data_rows = $table_data.bootstrapTable("getData").length;
               //判断table_data表的行数，并写入行数据
               if (data_rows != 0) {
                    for (var j = 0; j < data_rows; j++) {
                        table_data_data.forEach((item) => {
                            if (item.hasOwnProperty(data_column)) {
                                           delete item[data_column];
                            }
                        })
                    }
               }

               $("#table_data").bootstrapTable('refreshOptions', {
                   columns: data_Columns,
                   data: table_data_data
               });
           }
           else if (type == "update") {
               // 更新table_data表头
               data_Columns[col_num + 2] = {field: data_column, title: data_column, sortable: true};
               //这里要修改，数据没有了
               //resource_data= JSON.stringify($table_data.bootstrapTable('getData'));
               //获取表格的行数
               //alert (JSON.stringify(table_data_data));
               var data_rows = $table_data.bootstrapTable("getData").length;

               //判断table_data表的行数，并写入行数据
               if (data_rows != 0) {

                   // 先将json对象转为json字符串，再替换你要替换的属性名，最后再转为json对象
                   table_data_data = JSON.parse(JSON.stringify(table_data_data).replace(new RegExp(old_value,'g'),data_column));
                   $("#table_data").bootstrapTable('refreshOptions', {
                       columns: data_Columns,
                       data:table_data_data,

                   });
               }
           }
       }

       function isExist(field, value,old_value) {
          //判断一个字段值是否在json数组中
           table_param_data = $table_param.bootstrapTable('getData');
                  // table_param_data.some((item)=>{return item.param === value;});
           for(let item of table_param_data) {
              if(item.param === value) {
                         // alert("3333");

              }
              else {
                 // alert("4444");
              }
           }

       }

       //保存表table_param表输入的数据
       function saveData(index, field, value,old_value) {

               $table_param.bootstrapTable('updateCell', {
                   index: index,       //行索引
                   field: field,       //列名
                   value: value        //cell值
               })
               ReSetDataResource("update",index,value,old_value);

           }

       //保存表table_param表输入的数据
       function save_req_Data(index, field, value,old_value,table_name) {

               table_name.bootstrapTable('updateCell', {
                   index: index,       //行索引
                   field: field,       //列名
                   value: value        //cell值
               })
           }

       //保存表table_data表输入的数据
       function saveDataResource(index, field, value) {
           $table_data.bootstrapTable('updateCell', {
               index: index,       //行索引
               field: field,       //列名
               value: value        //cell值
           })
       };

        //获取随机数函数
       function getRandom(min, max) {
            min = Math.ceil(min);
            max = Math.floor(max);
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }

         //关闭修改用例窗口
       function closeDiv() {
                document.getElementById("OptsList").style.display="none";
            }

       //打开前后置操作列表函数
       function GetOpts(obj) {
            var opts_type = obj;
            //alert(case_id);
                $.ajax({
                    type: 'post',
                    url: '/api/OperationList',
                    data: {
                        "page_num" : 1
                            },
                    timeout: 5000, //超时时间设置，单位毫秒
                    beforeSend:function(xhr, settings){xhr.setRequestHeader("X-CSRFToken",csrftoken);},

                    success: function (res) {
                        $("#OptsList").html(res);
                        $("#OptsList").show();
                        //设置前后置操作浮层的opt_type为pre
                        document.getElementById('opts_type').value=opts_type;

                    }

            });


        }

       //添加前后置操作
       function AddOpts(opts_id,opts_name) {
           var opts_id = opts_id;
           var opts_name = opts_name;
           var opts_type = $("#opts_type").val();

           if (opts_type == "pre") {

               //先保存div中原来的html
               var old_html = document.getElementById("preOpsList").innerHTML;
               var add_html = '<div class=""  style="height:20px;float:left;margin-left:30px;">' +
                   ' <input type="hidden" id="pre_opts_id" name="pre_opts_id"  value="' + opts_id + '">' +
                   '<a href="#">' + opts_name + '</a>' +
                   ' <span class="icon-remove red" onclick="DelOpts(this)"></span>' +
                   '</div>';
               //再跟你想追加的代码加到一起插入div中
               document.getElementById("preOpsList").innerHTML = old_html + add_html;

           }
           if (opts_type == "after") {
                              //先保存div中原来的html
               var old_html = document.getElementById("afterOpsList").innerHTML;
               var add_html = '<div class="form-inline"  style="height:20px;float:left;margin-left: 30px;">' +
                   ' <input type="hidden" id="after_opts_id" name="after_opts_id"  value="' + opts_id + '">' +
                   '<a href="#">' + opts_name + '</a>' +
                   ' <span class="icon-remove red" onclick="DelOpts(this)"></span>' +
                   '</div>';
               //再跟你想追加的代码加到一起插入div中
               document.getElementById("afterOpsList").innerHTML = old_html + add_html;

           }
           if (opts_type == "run_after") {
                              //先保存div中原来的html
               var old_html = document.getElementById("RunAfterOpsList").innerHTML;
               var add_html = '<div class="form-inline" id="run_after_opt" style="height:20px;float:left;margin-left: 30px;">' +
                   ' <input type="hidden" id="run_after_opt" name="run_after_opt" value="' + opts_id + '">' +
                   '<a href="#">' + opts_name + '</a>' +
                   ' <span class="" onclick="DelOpts(this)"><i class="icon-remove red "></i></span>' +
                   '</div>';
               //再跟你想追加的代码加到一起插入div中
               document.getElementById("RunAfterOpsList").innerHTML = old_html + add_html;

           }


       }

        //删除已添加的前后置操作
       function DelOpts(obj){
        $(obj).parent().remove();
        }

        //添加JsonPathCheck
       function AddJsonPathCheck() {
             //先保存div中原来的html
               var old_html = document.getElementById("jsonCheckList").innerHTML;
               var add_html = '<div class="form-inline"  style="height:30px;margin-top: 5px;">'+
                                   '<input type="text" placeholder="JsonPath" id="jpath_key" class="form-control">'+
                                   // '<select class="chzn-done" tabindex="-1">'+

                       '<select class="span2 select2_category select2-offscreen" data-placeholder="Choose a Category" tabindex="-1" id="jpath_opt">'+

                                                ' <option value="==">==</option>'+
                                               ' <option value="!=">!=</option>'+
                                                '<option value=">"> > </option>'+
                                              '  <option value="<"><</option>'+
                                               ' <option value=">=">>=</option>'+
                                               ' <option value="<"><</option>'+
                                                '<option value="<="><=</option>'+
                                                  '<option value="one_Contains">one_Contains</option>'+
                                                '<option value="Contains_one">Contains_one</option>'+
                                                '<option value="NotContains">NotContains</option>'+
                                    '</select>'+
                                   '<input type="text" placeholder="JsonValue" id="jpath_value" class="form-control">'+
                                   '<span class="btn red icn-only  btn-sm" onclick="DelOpts(this)"><i class="icon-remove"></i></span>'+
                              '</div>';
               //再跟你想追加的代码加到一起插入div中
               document.getElementById("jsonCheckList").innerHTML = old_html + add_html;
       }

       //新增api接口用力
       function AddApiCase() {
           //获取数据池json数据
           var datasource = JSON.stringify($table_data.bootstrapTable('getData')).replace(/^\s+|\s+$/g,"").replace(/<\/?.+?>/g,"");
           //获取用例基本信息
           var api_name = $("#api_name").val();
           var api_method = $("#api_method").val();
           var belong_service = $("#belong_service").val();
           var belong_env = $("#belong_env").val();
           //接口类型，("0", "前后置操作"), ("1", "CI"),("2", "非CI"),("3", "删除")
           var type = $("input[name='api_type']:checked").val();

           //获取用例前置操作
           var preOpsList = [];
           $("#preOpsList>div").each(function(){
                preOpsList.push($(this).find("input[id ='pre_opts_id']").val());
           });
           //alert(preOpsList);

           //后置操作:
           var afterOpsList = [];
           $("#afterOpsList>div").each(function(){
                afterOpsList.push($(this).find("input[id ='after_opts_id']").val());
           });

           //获取测试后操作列表
           var RunAfterOpsList = [];
           $("#RunAfterOpsList>div").each(function(){
                RunAfterOpsList.push($(this).find("input[id ='run_after_opt']").val());
           });

           //获取检查点校验
           var httpcode_check =  $("#httpcode_check ").val();
           var include_check =  $("#include_check").val();
           var no_include_check = $("#no_include_check ").val();
           var json_check = [];
               $("#jsonCheckList>div").each(function(){
                //json_check.push($(this).find("input[id='jpath_key']").val(), $(this).find("#jpath_opt option:selected").val(),$(this).find("input[id='jpath_value']").val());
                json_check.push({json_key:$(this).find("input[id='jpath_key']").val(),json_compare:$(this).find("#jpath_opt option:selected").val(),json_value:$(this).find("input[id='jpath_value']").val()})
            });

           //alert(afterOpsList);

           // var api_request ='';
           var api_request =
               {
                   "url":{"method_type":$("#method_type").val(), "host":$("#GParam_host").val(),"api_path":$("#api_path").val()},
                   "ds_parm":JSON.parse(JSON.stringify($table_param.bootstrapTable('getData')).replace(/^\s+|\s+$/g,"").replace(/<\/?.+?>/g,"")),
                   "ds":JSON.parse(JSON.stringify($table_data.bootstrapTable('getData')).replace(/^\s+|\s+$/g,"").replace(/<\/?.+?>/g,"")),
                   "head":JSON.parse(JSON.stringify($table_head.bootstrapTable('getData')).replace(/^\s+|\s+$/g,"").replace(/<\/?.+?>/g,"")),
                   "Cookies":JSON.parse(JSON.stringify($table_Cookies.bootstrapTable('getData')).replace(/^\s+|\s+$/g,"").replace(/<\/?.+?>/g,"")),
                   "request":JSON.parse(JSON.stringify($table_request_param.bootstrapTable('getData')).replace(/^\s+|\s+$/g,"").replace(/<\/?.+?>/g,"")),
                   "response":JSON.parse(JSON.stringify($table_response_param.bootstrapTable('getData')).replace(/^\s+|\s+$/g,"").replace(/<\/?.+?>/g,"")),
                   "check":{
                       "httpcode_check":httpcode_check,
                       "include_check":include_check,
                       "no_include_check":no_include_check,
                       "json_check":json_check
                   }
               };
           $.ajax({
                    type: 'post',
                    url: '/api/AddApiCase',
                    traditional:true,
                    data: {
                        "api_name":api_name,
                        "api_method":api_method,
                        "belong_service":belong_service,
                        "belong_env":belong_env,
                        "type":type,
                        "pre_operation":preOpsList,
                        "api_request":JSON.stringify(api_request),
                        "RunAfterOpsList":RunAfterOpsList,
                        "after_operation":afterOpsList,
                    },
                    timeout: 5000, //超时时间设置，单位毫秒
                    beforeSend: function (xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken",csrftoken);
                        },
                    success: function (res) {
                           if (res.code == 200) {
                               //返回上一页并刷新：
                            self.location=document.referrer;
                        }
                           else{

                               alert(res.msg)
                           }
                    }

           });
       }