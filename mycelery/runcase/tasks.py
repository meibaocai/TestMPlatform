# _*_ encoding:utf-8 _*_
# Create your tasks here
# celery的任务必须写在tasks.py的文件中，别的文件名不识别！！！
from mycelery.main import app
from django.http import JsonResponse
from api.models import EnvInfo, GlobalParameterInfo, ApiCaseInfo, RunApiResultInfo, RunApiPlanInfo
from manager.models import ServiceInfo
from django.db.models import Q
from utils.common import Init_GlobalParameter, run_opt, config_disc, send_request, show_return_data, show_return_cookies, show_return_headers, config_check, config_check_json, checkResult, random_str
from datetime import datetime
import json
from utils.Log import MyLog as Log

# Celery(bind=True) 修饰实例方法和类方法时怎么传参, self问题.
# 不用filter=task_method时，实例(self)不会自动传入。
# 只有bind=True时， task对象会作为第一个参数自动传入。
# 加上filter=task_method参数，实例(self)会作为第一个参数自动传入。
# 加上filter=task_method, bind=True, task对象会作为第一个，实例(self)会作为第二个参数自动传入。
# 所以，最佳调用方式应为:
# @app.task(bind=True, filter=task_method)
# def test1(task_self, self, a, b)

@app.task(bind=True)
def run_search_case(self, pid, search_key, select_env, select_service, username):
    print("pid")
    if pid != '':
            # 定义初始化全局参数和前置操作参数
            init_gp_log = ''
            pre_opt_log = ''
            # 初始化全局参数
            print("<-------------初始化全局参数 开始------------->")
            try:
                init_gp_log = Init_GlobalParameter(self, pid)
            except Exception as err:
                print("初始化全局参数失败！")
            print("<-------------初始化全局参数 结束------------->")
            all_apicase = ApiCaseInfo.objects.filter(Q(belong_project_id=pid) & Q(type='1')).order_by("-add_time")
            # 按照关键字搜索
            if search_key:
                all_apicase = all_apicase.filter(Q(api_name__icontains=search_key) | Q(api_method__icontains=search_key))
            # 按照环境搜索
            if select_env:
                all_apicase = all_apicase.filter(belong_env_id=select_env).order_by("-add_time")
            # 按照服务搜索
            if select_service:
                all_apicase = all_apicase.filter(belong_service=int(select_service)).order_by("-add_time")
            # 定义运行批次号run_batch
            run_batch = str(datetime.now().strftime("%Y%m%d%H%M%S"))
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for each_case in all_apicase:
                api_name = each_case.api_name
                case_id = each_case.id
                belong_env = each_case.belong_env.id
                belong_service = each_case.belong_service.id
                api_request = json.loads(each_case.api_request)
                # 初始化 ApiCaseInfo，belong_env
                related_case = ApiCaseInfo.objects.get(id=int(case_id))
                belong_env = EnvInfo.objects.get(id=int(belong_env))
                belong_service = ServiceInfo.objects.get(id=int(belong_service))
                # 初始化前后置操作
                pre_operation = []
                after_operation = []
                run_after_operation = []
                res_dict = {}
                # 第1步：获取请求URl
                if api_request["url"]["host"] and api_request["url"]["method_type"]:
                    send_host = api_request["url"]["host"]
                    method_type = api_request["url"]["method_type"]
                    send_host = GlobalParameterInfo.objects.get(id=int(send_host)).value
                    send_url = send_host + api_request["url"]["api_path"]
                    print("send_url:", send_url)
                else:
                    # return JsonResponse({"msg": "send_host不合法!", "code": 500})
                    # 初始化CI执行记录
                    run_api_info = RunApiResultInfo()
                    run_api_info.type = '2'
                    run_api_info.belong_project_id = pid
                    run_api_info.related_case = related_case
                    run_api_info.belong_env = belong_env
                    run_api_info.belong_service = belong_service
                    run_api_info.api_name = api_name
                    run_api_info.detail = "send_url不合法!"
                    run_api_info.run_batch = run_batch
                    run_api_info.status = '0'
                    run_api_info.save()
                    print("----------send_url不合法!----------------")
                    continue
                # 第2步：获取预置操作id，并且执行预制操作
                if each_case.pre_operation:
                    all_pre_operation = eval(each_case.pre_operation)
                    # 调用前置操作
                    print("<-------------调用前置操作------------->", all_pre_operation)
                    try:
                        (res_dict, pre_opt_log) = run_opt(self, *all_pre_operation)
                    except Exception as err:
                        print("调用前置操作失败！")
                    print("前置操作返回参数res_dict值:", res_dict)

                # 第3步：获取数据池,类型是个list,并且替换其中的取前置操作的值和全局操作的值
                if api_request["ds"]:
                    ds = api_request["ds"]
                    print("<-------------获取数据池------------->\n", ds)
                    for ds_line in ds:
                        if 'checkbox' in ds_line:
                            ds_line.pop('checkbox')
                        if 'ID' in ds_line:
                            ds_line.pop('ID')
                        for dl_key, dl_value in ds_line.items():
                            # dl_value 需要转换成str，否则如果dl_value是int的时候就会报错
                            if str(dl_value).startswith('${pre.') and str(dl_value).endswith('}'):
                                if res_dict:
                                    ds_line[dl_key] = res_dict[dl_value[6:-1]]
                                else:
                                    ds_line[dl_key] = ''
                            elif str(dl_value).startswith('${') and str(dl_value).endswith('}'):
                                if GlobalParameterInfo.objects.get(name=dl_value[2:-1]).value:
                                    dl_value = GlobalParameterInfo.objects.get(name=dl_value[2:-1]).value
                                else:
                                    dl_value = ''
                                ds_line[dl_key] = dl_value
                            else:
                                continue
                    print("<-------------更新后的获取数据池------------->\n",ds)

                    for ds_row in ds:
                        # 初始化日志
                        log_name = 'case_id_' + str(case_id) + random_str(6) + '_output.log'
                        log_batch = 'RunAllCaseView'
                        self.log_run_all = Log.get_log(log_name, log_batch, 'run_all_case')
                        self.logger_run_all = self.log_run_all.get_logger()
                        self.logger_run_all.info("调用初始化全局参数\n" + init_gp_log + "\n")
                        self.logger_run_all.info("调用前置操作\n" + pre_opt_log + "\n")
                        self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " START--------")
                        self.logger_run_all.info("send_url:" + send_url)
                        self.logger_run_all.info("method_type:" + method_type)
                        headers ={}
                        Cookies = {}
                        requests = {}
                        httpcode_check = '200'
                        include_check = ''
                        no_include_check = ''
                        json_check = []
                        print("api_name:", api_name, ds.index(ds_row))
                        # 获取接口请求head
                        if api_request["head"]:
                            headers = config_disc(str(api_request["head"]), str(res_dict), str(ds_row))
                            print("headers:", headers)
                            self.logger_run_all.info("headers：" + str(headers))

                        # 获取接口请求cookies
                        if api_request["Cookies"]:
                            Cookies = config_disc(str(api_request["Cookies"]), str(res_dict), str(ds_row))
                            print("Cookies:", Cookies)
                            self.logger_run_all.info("Cookies：" + str(Cookies))

                        # 获取接口request
                        if api_request["request"]:
                            # print(api_request["request"])
                            requests = config_disc(str(api_request["request"]), str(res_dict), str(ds_row))
                            print("requests:", requests)
                            self.logger_run_all.info("requests：" + str(requests))
                        else:
                            print("请求body不合法！")
                            self.logger_run_all.info("请求body不合法！")
                            self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
                            # 初始化CI执行记录
                            run_api_info = RunApiResultInfo()
                            run_api_info.type = '2'
                            run_api_info.belong_project_id = pid
                            run_api_info.related_case = related_case
                            run_api_info.belong_env = belong_env
                            run_api_info.belong_service = belong_service
                            run_api_info.api_name = api_name + str(ds.index(ds_row))
                            run_api_info.detail = self.log_run_all.get_logContent()
                            run_api_info.run_batch = run_batch
                            run_api_info.status = '0'
                            run_api_info.save()
                            self.log_run_all.remove_handler()
                            continue

                        if api_request["check"]:
                            if api_request["check"]["httpcode_check"]:
                                # print(api_request["request"])
                                try:
                                    httpcode_check = config_check(str(api_request["check"]["httpcode_check"]),str(res_dict), str(ds_row))
                                    print("httpcode_check:", httpcode_check)
                                    self.logger_run_all.info("httpcode_check:" + httpcode_check)
                                    # 获取的类型是str
                                except Exception as err:
                                    print("<-------------初始化json_check失败！------------->\n")
                                    self.logger_run_all.error("-------------初始化json_check失败！-------------")

                            if api_request["check"]["include_check"]:
                                # print(api_request["request"])
                                try:
                                    include_check = config_check(str(api_request["check"]["include_check"]),str(res_dict),'{}')
                                    print("include_check:", include_check)
                                    self.logger_run_all.info("include_check:" + str(include_check))
                                except Exception as err:
                                    print("<-------------初始化include_check失败！------------->\n")
                                    self.logger_run_all.error("-------------初始化include_check失败！-------------")

                            if api_request["check"]["no_include_check"]:
                                try:
                                    no_include_check = config_check(str(api_request["check"]["no_include_check"]),str(res_dict), str(ds_row))
                                    print("no_include_check:", no_include_check)
                                    self.logger_run_all.info("no_include_check:" + str(no_include_check))
                                except Exception as err:
                                    print("<-------------初始化no_include_check败！------------->\n")
                                    self.logger_run_all.error("-------------初始化no_include_check失败！-------------")

                            if api_request["check"]["json_check"]:
                                # json_check 类型是list
                                try:
                                    json_check = config_check_json(str(api_request["check"]["json_check"]),str(res_dict),str(ds_row))
                                    print("json_check:", json_check)
                                    self.logger_run_all.info("json_check:" + json_check.__str__())
                                except Exception as err:
                                    print("<-------------初始化json_check:败！------------->\n")
                                    self.logger_run_all.info("-------------初始化json_check:失败！-------------")

                        try:
                            return_json = send_request(api_name, method_type, send_url, str(headers), str(Cookies), str(requests))
                        except Exception as err:
                            print("<-------------请求不合法------------->")
                            self.logger_run_all.error("Time out！")
                            self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
                            # 初始化CI执行记录
                            run_api_info = RunApiResultInfo()
                            run_api_info.type = '2'
                            run_api_info.belong_project_id = pid
                            run_api_info.related_case = related_case
                            run_api_info.belong_env = belong_env
                            run_api_info.belong_service = belong_service
                            run_api_info.api_name = api_name + str(ds.index(ds_row))
                            run_api_info.detail = self.log_run_all.get_logContent()
                            run_api_info.status = '0'
                            run_api_info.run_batch = run_batch
                            run_api_info.save()
                            self.log_run_all.remove_handler()
                            continue

                        # 判断请求是否有返回
                        if return_json:
                            res_httpcode = return_json.status_code
                            print("res_httpcode:", res_httpcode)
                            self.logger_run_all.info("res_httpcode:" + str(res_httpcode))

                            reps_headers = show_return_headers(return_json)
                            print("reps_headers:", reps_headers)
                            self.logger_run_all.info("reps_headers:", reps_headers)

                            reps_cookies = show_return_cookies(return_json)
                            print("reps_cookies:", reps_cookies)
                            self.logger_run_all.info("reps_cookies:", **reps_cookies)

                            reps_data = show_return_data(return_json)
                            print("reps_data:", reps_data)
                            self.logger_run_all.info("请求返回值:" + '\n' + str(reps_data))

                            try:
                                run_status = checkResult(httpcode_check, include_check, no_include_check, res_httpcode,str(reps_headers),str(reps_cookies), str(reps_data), *json_check)
                            except Exception as err:
                                run_status = '0'
                                self.logger_run_all.error("调用checkResult方法异常！")

                            # 获取后置操作
                            if each_case.after_operation:
                                all_after_operation = eval(each_case.after_operation)
                                print("调用后置操作")
                                self.logger_run_all.info("调用后置操作开始！")
                                try:
                                    (after_dict, after_opt_log) = run_opt(self, *all_after_operation)
                                    self.logger_run_all.info("调用后置操作开始！\n" + after_opt_log + '\n')
                                except Exception as err:
                                    print("调用后置操作失败")
                                    self.logger_run_all.error("调用后置操作失败!")

                            # 获取执行后操作
                            if each_case.run_after_operation:
                                print(type(each_case.run_after_operation))
                                all_run_after_operation = eval(each_case.run_after_operation)
                                print(all_run_after_operation)
                                print("调用运行后操作")
                                self.logger_run_all.info("调用运行后操作开始！")
                                try:
                                    (run_after_dict, run_after_opt_log) = run_opt(self, *all_run_after_operation)
                                    self.logger_run_all.info("调用运行后操作结束！\n" + run_after_opt_log + '\n')
                                except Exception as err:
                                    print("调用运行后操作失败")
                                    self.logger_run_all.error("调用运行后的操作失败！")

                        else:
                            run_status = '0'
                            self.logger_run_all.error("Time out！")

                        self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
                        self.log_run_all.remove_handler()
                        # 初始化CI执行记录
                        run_api_info = RunApiResultInfo()
                        run_api_info.type = '2'
                        run_api_info.belong_project_id = pid
                        run_api_info.related_case = related_case
                        run_api_info.belong_env = belong_env
                        run_api_info.belong_service = belong_service
                        run_api_info.api_name = api_name + str(ds.index(ds_row))
                        run_api_info.detail = self.log_run_all.get_logContent()
                        run_api_info.run_batch = run_batch
                        run_api_info.status = run_status
                        run_api_info.save()

                    # return JsonResponse({"msg": "ok!", "code": 200})
                else:
                    # 初始化日志
                    log_name = 'case_id_' + str(case_id) + random_str(6) + '_output.log'
                    log_batch = 'RunAllCaseView'
                    self.log_run_all = Log.get_log(log_name, log_batch, 'run_all_case')
                    self.logger_run_all = self.log_run_all.get_logger()
                    self.logger_run_all.info("调用初始化全局参数\n" + init_gp_log + "\n")
                    self.logger_run_all.info("调用前置操作\n" + pre_opt_log + "\n")
                    self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " START--------")
                    self.logger_run_all.info("send_url:" + send_url)
                    self.logger_run_all.info("method_type:" + method_type)
                    headers = {}
                    Cookies = {}
                    requests = {}
                    httpcode_check = '200'
                    include_check = ''
                    no_include_check = ''
                    json_check = []
                    if api_request["head"]:
                        headers = config_disc(str(api_request["head"]), str(res_dict), '{}')
                        print("headers:", headers)
                        self.logger_run_all.info("headers：" + str(headers))

                    if api_request["Cookies"]:
                        Cookies = config_disc(str(api_request["Cookies"]), str(res_dict), '{}')
                        print("Cookies:", Cookies)
                        self.logger_run_all.info("Cookies：" + str(Cookies))

                    if api_request["request"]:
                            requests = config_disc(str(api_request["request"]), str(res_dict), '{}')
                            print("requests:", requests)
                            self.logger_run_all.info("requests：" + str(requests))

                            # 获取校验
                    if api_request["check"]:
                        if api_request["check"]["httpcode_check"]:
                            # print(api_request["request"])
                            try:
                                httpcode_check = config_check(str(api_request["check"]["httpcode_check"]),str(res_dict), '{}')
                                # 获取的类型是str
                                print("httpcode_check:", httpcode_check)
                                self.logger_run_all.info("httpcode_check:" + httpcode_check)
                            except Exception as err:
                                print("初始化httpcode_check失败")
                                self.logger_run_all.error("初始化httpcode_check失败！" )

                        if api_request["check"]["include_check"]:
                            try:
                                include_check = config_check(str(api_request["check"]["include_check"]), str(res_dict),'{}')
                                print("include_check:", include_check)
                                self.logger_run_all.info("include_check:" + str(include_check))
                            except Exception as err:
                                print("初始化include_check失败!")
                                self.logger_run_all.error("初始化include_check失败！" )

                        if api_request["check"]["no_include_check"]:
                            # print(api_request["request"])
                            try:
                                no_include_check = config_check(str(api_request["check"]["no_include_check"]),str(res_dict), '{}')
                                print("no_include_check:", no_include_check)
                                self.logger_run_all.info("no_include_check:" + str(no_include_check))
                            except Exception as err:
                                print("初始no_include_check失败!")
                                self.logger_run_all.error("初始化no_include_check失败！" )


                        if api_request["check"]["json_check"]:
                            # json_check 类型是list
                            try:
                                json_check = config_check_json(str(api_request["check"]["json_check"]), str(res_dict),'{}')
                                print("json_check:",json_check)
                                self.logger_run_all.info("json_check:" + json_check.__str__())
                            except Exception as err:
                                print("初始化json_check失败!")
                                self.logger_run_all.error("初始化json_check失败！" )

                    try:
                        return_json = send_request(api_name, method_type, send_url, str(headers), str(Cookies), str(requests))
                    except TimeoutError as err:
                        print("------Time out!------")
                        self.logger_run_all.error("------Time out!------")
                        self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
                        self.log_run_all.removeHandler()
                        # 初始化CI执行记录
                        run_api_info = RunApiResultInfo()
                        run_api_info.type = '2'
                        run_api_info.belong_project_id = pid
                        run_api_info.related_case = related_case
                        run_api_info.belong_env = belong_env
                        run_api_info.belong_service = belong_service
                        run_api_info.api_name = api_name
                        run_api_info.detail = self.log_run_all.get_logContent()
                        run_api_info.run_batch = run_batch
                        run_api_info.status = '0'
                        run_api_info.save()
                        continue
                    # 判断 请求是否有返回
                    if return_json:
                        res_httpcode = return_json.status_code
                        print("res_httpcode:", res_httpcode)
                        self.logger_run_all.info("res_httpcode:"+ str(res_httpcode))

                        reps_headers = show_return_headers(return_json)
                        print("reps_headers:", reps_headers)
                        self.logger_run_all.info("reps_headers:", reps_headers)

                        reps_cookies = show_return_cookies(return_json)
                        print("reps_cookies:", reps_cookies)
                        self.logger_run_all.info("reps_cookies:", **reps_cookies)

                        reps_data = show_return_data(return_json)
                        print("reps_data:", reps_data)
                        self.logger_run_all.info("请求返回值:" + '\n' + str(reps_data))

                        try:
                            run_status = checkResult(httpcode_check, include_check, no_include_check, res_httpcode,str(reps_headers),str(reps_cookies), str(reps_data), *json_check)
                        except Exception as err:
                            print("调用检查点函数checkResult失败！")
                            run_status = 0
                            self.logger_run_all.error("调用检查点函数checkResult失败！")

                        # 获取后置操作
                        if each_case.after_operation:
                            all_after_operation = eval(each_case.after_operation)
                            print("调用后置操作")
                            self.logger_run_all.info("调用后置操作开始！", *all_after_operation)
                            try:
                                (after_dict, after_opt_log) = run_opt(self, *all_after_operation)
                                self.logger_run_all.info("调用后置操作开始！\n" + after_opt_log + '\n')
                            except Exception as err:
                                print("调用后置操作失败")
                                self.logger_run_all.error("调用后置操作失败!")

                        # 获取执行后操作
                        if each_case.run_after_operation:
                            all_run_after_operation = eval(each_case.run_after_operation)
                            print("调用运行后操作")
                            self.logger_run_all.info("调用运行后操作开始！")
                            try:
                                (run_after_dict, run_after_opt_log) = run_opt(self, *all_run_after_operation)
                                self.logger_run_all.info("调用后置操作开始！\n" + run_after_opt_log + '\n')
                            except Exception as err:
                                print("调用运行后操作失败")
                                self.logger_run_all.error("调用运行后的操作失败！")
                        self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
                        self.log_run_all.remove_handler()

                    else:
                        run_status = 0
                        self.logger_run_all.error("Time out!")
                        self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
                        self.log_run_all.remove_handler()

                    # 初始化CI执行记录
                    run_api_info = RunApiResultInfo()
                    run_api_info.type = '2'
                    run_api_info.belong_project_id = pid
                    run_api_info.related_case = related_case
                    run_api_info.belong_env = belong_env
                    run_api_info.belong_service = belong_service
                    run_api_info.api_name = api_name
                    run_api_info.detail = self.log_run_all.get_logContent()
                    run_api_info.run_batch = run_batch
                    run_api_info.status = run_status
                    run_api_info.save()
            # 写入CI 执行计划表
            case_num = RunApiResultInfo.objects.filter(run_batch=run_batch).count()
            success_num = RunApiResultInfo.objects.filter(Q(run_batch=run_batch) & Q(status='1')).count()
            fail_num = case_num - success_num
            if case_num:
                success_ratio = round(success_num/case_num, 4)*100
            else:
                success_ratio = 0
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            run_plan_info = RunApiPlanInfo()
            run_plan_info.name = '触发CI-执行搜索用例' + str(start_time) + '_By_' + username
            run_plan_info.run_batch = run_batch
            run_plan_info.case_num = case_num
            run_plan_info.success_num = success_num
            run_plan_info.fail_num = fail_num
            run_plan_info.success_ratio = success_ratio
            run_plan_info.belong_project_id = pid
            run_plan_info.run_user = username
            run_plan_info.start_time = start_time
            run_plan_info.end_time = end_time
            run_plan_info.save()

            return JsonResponse({"msg": "CI执行完成！", "code": 200})
    else:
        return JsonResponse({"msg": "项目ID不能为空，请选择项目！", "code": 500})


@app.task(bind=True)
def run_single_case(self, pid, case_id, *select_ds):
        if pid != '' and case_id != '':
            # 定义初始化全局参数和前置操作参数
            init_gp_log = ''
            pre_opt_log = ''
            # 删除单个用例执行记录,不包含批量执行的CI记录，即可：run_batch不为空的
            result_info = RunApiResultInfo.objects.filter(Q(related_case=int(case_id)) & Q(run_batch=''))
            result_info.delete()
            print("<-------------初始化全局参数 开始------------->")
            try:
                init_gp_log = Init_GlobalParameter(self, pid)
            except Exception as err:
                print("初始化全局参数失败！")
            print("<-------------初始化全局参数 结束------------->")
            # select_ds :前台传过来选中的数据池行数据
            all_apicase = ApiCaseInfo.objects.get(id=int(case_id))
            api_name = all_apicase.api_name
            # api_method = all_apicase.api_method
            belong_env = all_apicase.belong_env.id
            belong_service = all_apicase.belong_service.id
            api_request = json.loads(all_apicase.api_request)
            # 初始化前后置操作
            pre_operation = []
            after_operation = []
            run_after_operation = []
            res_dict = {}
            # 初始化 ApiCaseInfo，belong_env
            related_case = ApiCaseInfo.objects.get(id=int(case_id))
            belong_env = EnvInfo.objects.get(id=int(belong_env))
            belong_service = ServiceInfo.objects.get(id=int(belong_service))

            # 第1步：获取请求URl
            if api_request["url"]["host"] and api_request["url"]["method_type"]:
                send_host = api_request["url"]["host"]
                method_type = api_request["url"]["method_type"]
                send_host = GlobalParameterInfo.objects.get(id=int(send_host)).value
                send_url = send_host + api_request["url"]["api_path"]
                print("send_url:", send_url)
            else:
                print("<-------------请求URL或者参数不合法------------->\n", api_name)
                return JsonResponse({"msg": "send_host不合法!", "code": 500})

            # 第2步：获取预置操作id，并且执行预制操作
            if all_apicase.pre_operation:
                all_pre_operation = eval(all_apicase.pre_operation)
                # 调用前置操作
                print("<-------------调用前置操作------------->", all_pre_operation)
                try:
                    # res_dict:调用前置操作返回的字典，pre_detail_opt：日志信息
                    (res_dict, pre_opt_log) = run_opt(self, *all_pre_operation)
                except Exception as err:
                    print("调用前置操作异常!")

                print("前置操作返回参数res_dict值:", res_dict)
            # 第3步：获取数据池,类型是个list,并且替换其中的取前置操作的值和全局操作的值
            if api_request["ds"]:
                # 判断前台传过来选中的数据池数据是否为空，如果未空，就执行所有数据
                if len(select_ds) == 0:
                    ds = api_request["ds"]
                else:
                    ds = select_ds
                print("<-------------获取数据池------------->\n", ds)
                for ds_line in ds:
                    if 'checkbox' in ds_line:
                        ds_line.pop('checkbox')
                    if 'ID' in ds_line:
                        ds_line.pop('ID')
                    for dl_key, dl_value in ds_line.items():
                        # dl_value 需要转换成str，否则如果dl_value是int的时候就会报错
                        if str(dl_value).startswith('${pre.') and str(dl_value).endswith('}'):
                            if res_dict:
                                ds_line[dl_key] = res_dict[dl_value[6:-1]]
                            else:
                                ds_line[dl_key] = ''
                        elif str(dl_value).startswith('${') and str(dl_value).endswith('}'):
                            if GlobalParameterInfo.objects.get(name=dl_value[2:-1]).value:
                                dl_value = GlobalParameterInfo.objects.get(name=dl_value[2:-1]).value
                            else:
                                dl_value = ''
                            ds_line[dl_key] = dl_value
                        else:
                            continue
                print("<-------------更新后的获取数据池------------->\n",ds)

                for ds_row in ds:
                    # 初始化日志
                    log_name = 'case_id_' + case_id + random_str(6) + '_output.log'
                    log_batch = 'RunSingleCase'
                    self.log_run_single = Log.get_log(log_name, log_batch, 'run_single_case')
                    self.logger_run_single = self.log_run_single.get_logger()
                    self.logger_run_single.info("调用全局参数\n" + init_gp_log + "\n")
                    self.logger_run_single.info("调用前置操作\n" + pre_opt_log + "\n")
                    self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " START--------")
                    self.logger_run_single.info("method_type：" + method_type)
                    self.logger_run_single.info("send_url：" + send_url)

                    headers = {}
                    Cookies = {}
                    requests = {}

                    print("api_name:", api_name, ds.index(ds_row))
                    # 获取接口请求head
                    if api_request["head"]:
                        headers = config_disc(str(api_request["head"]), str(res_dict), str(ds_row))
                        print("headers:", headers)
                        self.logger_run_single.info("headers：" + str(headers))

                    # 获取接口请求cookies
                    if api_request["Cookies"]:
                        Cookies = config_disc(str(api_request["Cookies"]), str(res_dict), str(ds_row))
                        print("Cookies:", Cookies)
                        self.logger_run_single.info("Cookies：" + str(Cookies))


                    # 获取接口request
                    if api_request["request"]:
                        # print(api_request["request"])
                        requests = config_disc(str(api_request["request"]), str(res_dict), str(ds_row))
                        print("requests:", requests)
                        self.logger_run_single.info("requests：" + str(requests))


                    else:
                        print("请求body不合法！")
                        self.logger_run_single.info("--------请求body不合法!--------")
                        self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " END--------")

                        # 初始化CI执行记录
                        run_api_info = RunApiResultInfo()
                        run_api_info.type = '1'
                        run_api_info.belong_project_id = pid
                        run_api_info.related_case = related_case
                        run_api_info.belong_env = belong_env
                        run_api_info.belong_service = belong_service
                        run_api_info.api_name = api_name + str(ds.index(ds_row))
                        run_api_info.detail = self.log_run_single.get_logContent()
                        run_api_info.status = '0'
                        run_api_info.save()
                        self.log_run_single.remove_handler()
                        continue
                    # 获取校验
                    httpcode_check = '200'
                    include_check = ''
                    no_include_check = ''
                    json_check = []
                    if api_request["check"]:
                        if api_request["check"]["httpcode_check"]:
                            # print(api_request["request"])
                            httpcode_check = config_check(str(api_request["check"]["httpcode_check"]), str(res_dict), str(ds_row))
                            # 获取的类型是str
                            print("httpcode_check:", httpcode_check)
                            self.logger_run_single.info("httpcode_check:" + httpcode_check)

                        if api_request["check"]["include_check"]:
                            # print(api_request["request"])
                            include_check = config_check(str(api_request["check"]["include_check"]), str(res_dict), str(ds_row))
                            print("include_check:", include_check)
                            self.logger_run_single.info("include_check:" + str(include_check))

                        if api_request["check"]["no_include_check"]:
                            # print(api_request["request"])
                            no_include_check = config_check(str(api_request["check"]["no_include_check"]), str(res_dict), str(ds_row))
                            print("no_include_check:", no_include_check)
                            self.logger_run_single.info("no_include_check:" + str(no_include_check))


                        if api_request["check"]["json_check"]:
                            # print(api_request["request"])
                            # json_check 类型是list
                            json_check = config_check_json(str(api_request["check"]["json_check"]), str(res_dict), str(ds_row))
                            print("json_check:", json_check)
                            self.logger_run_single.info("json_check:" + json_check.__str__())
                    start_time = datetime.now()
                    try:
                        return_json = send_request(api_name, method_type, send_url, str(headers), str(Cookies), str(requests))
                        end_time = datetime.now()
                    except TimeoutError as err:
                        print("Time out!")
                        self.logger_run_single.info("Time out!")
                        self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " END--------")

                        # 初始化CI执行记录
                        run_api_info = RunApiResultInfo()
                        run_api_info.api_name = api_name + str(ds.index(ds_row))
                        run_api_info.type = '1'
                        run_api_info.belong_project_id = pid
                        run_api_info.related_case = related_case
                        run_api_info.belong_env = belong_env
                        run_api_info.belong_service = belong_service
                        run_api_info.detail = self.log_run_single.get_logContent()
                        run_api_info.status = '0'
                        run_api_info.save()
                        self.log_run_single.remove_handler()
                        continue
                    # res_code : 返回报文中http状态 HTTP/1.1 200 OK。类型是int，eg：200
                    if return_json:
                        res_httpcode = return_json.status_code
                        print("res_httpcode:", res_httpcode)
                        self.logger_run_single.info("res_httpcode:"+ str(res_httpcode))
                        reps_headers = show_return_headers(return_json)
                        print("reps_headers:", reps_headers)
                        self.logger_run_single.info("reps_headers:", reps_headers)
                        reps_cookies = show_return_cookies(return_json)
                        print("reps_cookies:", reps_cookies)
                        self.logger_run_single.info("reps_cookies:", **reps_cookies)
                        reps_data = show_return_data(return_json)
                        print("reps_data:", reps_data)
                        # print(type(reps_data))
                        self.logger_run_single.info("请求返回值:" + '\n' + str(reps_data))
                        try:
                        # 调用 checkResult，执行检查点校验:
                            run_status = checkResult(httpcode_check, include_check, no_include_check, res_httpcode,str(reps_headers), str(reps_cookies), str(reps_data), *json_check)
                            print("run_status:", run_status)
                        except Exception as err:
                            self.logger_run_single.info("调用“检查点校验”异常！")
                            run_status = '0'

                    else:
                        self.logger_run_single.error("Time out!")
                        run_status = '0'
                    # 获取后置操作
                    if all_apicase.after_operation:
                        all_after_operation = eval(all_apicase.after_operation)
                        print("调用后置操作")
                        self.logger_run_single.info("调用后置操作:", *all_after_operation)

                        try:
                            (after_dict, after_opt_log) = run_opt(self, *all_after_operation)
                        except Exception as err:
                            print("调用后置操作失败")
                            self.logger_run_single.error("调调用后置操作失败!")
                        self.logger_run_single.info("\n" + after_opt_log + "\n")

                    # 获取执行后操作
                    if all_apicase.run_after_operation:
                        all_run_after_operation = eval(all_apicase.run_after_operation)
                        print("调用运行后操作")
                        try:
                            (after_dict, run_after_opt_log) = run_opt(self, *all_run_after_operation)
                        except Exception as err:
                            print("调用运行后操作失败")
                            self.logger_run_single.error("调用运行后操作失败!")
                        print(str(after_dict))
                        self.logger_run_single.info("\n" + run_after_opt_log + "\n")

                    # 初始化CI执行记录
                    run_api_info = RunApiResultInfo()
                    run_api_info.type = '1'
                    run_api_info.belong_project_id = pid
                    run_api_info.related_case = related_case
                    run_api_info.belong_env = belong_env
                    run_api_info.belong_service = belong_service
                    run_api_info.api_name = api_name + str(ds.index(ds_row))
                    run_api_info.detail = self.log_run_single.get_logContent()
                    run_api_info.status = run_status
                    run_api_info.start_time = start_time
                    run_api_info.end_time = end_time
                    run_api_info.save()
                    self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " END--------")
                    self.log_run_single.remove_handler()

                return JsonResponse({"msg": "ok!", "code": 200})

                # return JsonResponse({"msg": "ok!", "code": 200})
            else:
                # 初始化日志
                log_name = 'case_id_' + case_id + random_str(6) + '_output.log'
                log_batch = 'RunSingleCase'
                self.log_run_single = Log.get_log(log_name, log_batch, 'run_single_case')
                self.logger_run_single = self.log_run_single.get_logger()
                self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " START--------")
                self.logger_run_single.info("method_type:" + method_type)
                self.logger_run_single.info("send_url:" + send_url)
                headers = {}
                Cookies = {}
                requests = {}
                httpcode_check = '200'
                include_check = ''
                no_include_check = ''
                json_check = []
                if api_request["head"]:
                    headers = config_disc(str(api_request["head"]), str(res_dict), '{}')
                    print("headers:", headers)
                    self.logger_run_single.info("headers:", **headers)
                if api_request["Cookies"]:
                    Cookies = config_disc(str(api_request["Cookies"]), str(res_dict), '{}')
                    print("Cookies:", Cookies)
                    self.logger_run_single.info("Cookies:", **Cookies)

                if api_request["request"]:
                        requests = config_disc(str(api_request["request"]), str(res_dict), '{}')
                        print("requests:", requests)
                        self.logger_run_single.info("Cookies:", **Cookies)

                # 获取校验
                if api_request["check"]:
                        if api_request["check"]["httpcode_check"]:
                            # print(api_request["request"])
                            try:
                                httpcode_check = config_check(str(api_request["check"]["httpcode_check"]), str(res_dict),'{}')
                                # 获取的类型是str
                                print("httpcode_check:", httpcode_check)
                                self.logger_run_single.info("httpcode_check:" + httpcode_check)
                            except Exception as err:
                                print("<-------------初始化httpcode_check失败！------------->\n")
                                self.logger_run_single.info("-------------初始化httpcode_check失败！-------------")

                        if api_request["check"]["include_check"]:
                            # print(api_request["request"])
                            try:
                                include_check = config_check(str(api_request["check"]["include_check"]), str(res_dict), '{}')
                                print("include_check:", include_check)
                                self.logger_run_single.info("include_check:",include_check)
                            except Exception as err:
                                print("<-------------初始化include_check失败！------------->\n")
                                self.logger_run_single.info("-------------初始化include_check失败！-------------")

                        if api_request["check"]["no_include_check"]:
                            # print(api_request["request"])
                            try:
                                no_include_check = config_check(str(api_request["check"]["no_include_check"]), str(res_dict), '{}')
                                print("no_include_check:", no_include_check)
                                self.logger_run_single.info("no_include_check:", no_include_check)
                            except Exception as err:
                                print("<-------------初始化include_check失败！------------->\n")
                                self.logger_run_single.info("-------------初始化include_check失败！-------------")

                        if api_request["check"]["json_check"]:
                            # print(api_request["request"])
                            try:
                                # json_check 类型是list
                                json_check = config_check_json(str(api_request["check"]["json_check"]), str(res_dict), '{}')
                                print("json_check:", json_check)
                                self.logger_run_single.info("json_check:" + json_check.__str__())
                                # print("json_check_type:",type(json_check))
                            except Exception as err:
                                print("<-------------初始化json_check失败！------------->\n")
                                self.logger_run_single.info("-------------初始化json_check失败！-------------")

                start_time = datetime.now()
                try:
                    return_json = send_request(api_name, method_type, send_url, str(headers), str(Cookies), str(requests))
                    end_time = datetime.now()
                except Exception as err:
                    self.logger_run_single.info("Time out!")
                    self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " END--------")
                    print("<-------------Time out!------------->")
                    # 初始化CI执行记录
                    run_api_info = RunApiResultInfo()
                    run_api_info.api_name = api_name
                    run_api_info.type = '1'
                    run_api_info.belong_project_id = pid
                    run_api_info.related_case = related_case
                    run_api_info.belong_env = belong_env
                    run_api_info.belong_service = belong_service
                    run_api_info.detail = self.log_run_single.get_logContent()
                    run_api_info.status = '0'
                    self.log_run_single.remove_handler()
                    run_api_info.save()
                if return_json:
                    res_httpcode = return_json.status_code
                    print("res_httpcode:", res_httpcode)
                    self.logger_run_single.info("res_httpcode", res_httpcode)

                    reps_headers = show_return_headers(return_json)
                    print("reps_headers:", reps_headers)
                    self.logger_run_single.info("reps_headers", reps_headers)

                    reps_cookies = show_return_cookies(return_json)
                    print("reps_cookies:", reps_cookies)
                    self.logger_run_single.info("reps_cookies", **reps_cookies)

                    reps_data = show_return_data(return_json)
                    print("reps_data:", reps_data)
                    self.logger_run_single.info("请求返回值:" + '\n' + str(reps_data))

                    try:
                        run_status = checkResult(httpcode_check, include_check, no_include_check, res_httpcode, str(reps_headers),str(reps_cookies), str(reps_data), *json_check)
                    except Exception as err:
                        self.logger_run_single.info("调用检查结果失败！")
                        run_status = '0'
                else:
                    self.logger_run_single.info("Time out！")
                    run_status = '0'

                    # 获取后置操作
                if all_apicase.after_operation:
                    all_after_operation = eval(all_apicase.after_operation)
                    print("调用后置操作")
                    self.logger_run_single.info("调用后置操作:", *all_after_operation)

                    try:
                        (after_dict, after_opt_log) = run_opt(self, *all_after_operation)
                    except Exception as err:
                        print("调用后置操作失败")
                        self.logger_run_single.error("调调用后置操作失败!")
                    self.logger_run_single.info("\n" + after_opt_log + "\n")

                    # 获取执行后操作
                if all_apicase.run_after_operation:
                    all_run_after_operation = eval(all_apicase.run_after_operation)
                    print("调用运行后操作")
                    self.logger_run_single.info("调用运行后操作:", *all_run_after_operation)
                    try:
                        (after_dict, run_after_opt_log) = run_opt(self, *all_run_after_operation)
                    except Exception as err:
                        print("调用运行后操作失败")
                        self.logger_run_single.error("调用运行后操作失败!")
                    self.logger_run_single.info("\n" + run_after_opt_log + "\n")

                    # 初始化CI执行记录
                self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " END--------")
                self.log_run_single.remove_handler()
                run_api_info = RunApiResultInfo()
                run_api_info.api_name = api_name
                run_api_info.type = '1'
                run_api_info.belong_project_id = pid
                run_api_info.related_case = related_case
                run_api_info.belong_env = belong_env
                run_api_info.belong_service = belong_service
                run_api_info.detail = self.log_run_single.get_logContent()
                run_api_info.status = run_status
                run_api_info.start_time = start_time
                run_api_info.end_time = end_time
                run_api_info.save()


                return JsonResponse({"msg": "ok!", "code": 200})

        else:
            return JsonResponse({"msg": "项目ID或者用例ID不能为空，请选择项目！", "code": 500})

