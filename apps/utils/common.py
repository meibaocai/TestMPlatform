# _*_ encoding:utf-8 _*_
from random import Random
import json, jsonpath
import time
from django.db.models import Q
from utils.Log import MyLog, Log
from api.models import GlobalParameterInfo, ApiCaseInfo, OperationInfo
from case.models import VersionCase, TestCase, VersionInfo, ProjectInfo
from utils import configHttp as ConfigHttp
from datetime import datetime
from utils.Log import MyLog as Log

def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
        # str+=choice(chars)
    return str

def get_value_from_return_json(json, name1, name2):
        """
        get value by key
        :param json:
        :param name1:
        :param name2:
        :return:
        """
        info = json['info']
        group = info[name1]
        value = group[name2]
        return value

def show_return_data(response):
        """
        show msg detail
        :param response:
        :return:
        """
        url = response.url
        msg = response.text

        # headers = response.headers
        # cookies = response.cookies
        # print("\n请求地址："+url)
        # 可以显示中文
        # print("\n请求返回值："+'\n'+json.dumps(json.loads(msg), ensure_ascii=False, sort_keys=True, indent=4))
        return msg

def show_return_cookies(response):
    """
    show msg detail
    :param response:
    :return:
    """

    # response.cookies是获取response中cookie属性, 返回的 <class 'requests.cookies.RequestsCookieJar'>, 是一个类
    # response.cookies.get_dict()     # 返回的是字典格式cookie
    cookies = response.cookies.get_dict()
    # print("\n请求地址："+url)
    # 可以显示中文
    # print("\n请求返回值："+'\n'+json.dumps(json.loads(msg), ensure_ascii=False, sort_keys=True, indent=4))
    return cookies

def show_return_headers(response):
    """
    show msg detail
    :param response:
    :return:
    """
    headers = response.headers
    # cookies = response.cookies
    # 可以显示中文
    # print("\n请求返回值："+'\n'+json.dumps(json.loads(msg), ensure_ascii=False, sort_keys=True, indent=4))

    return headers

def json_txt(dic_json):
        dic = {}
        if isinstance(dic_json,dict): #判断是否是字典类型isinstance 返回True false
            for key in dic_json:
                if isinstance(dic_json[key],dict):#如果dic_json[key]依旧是字典类型
                    print("****key--：%s value--: %s"%(key,dic_json[key]))
                    json_txt(dic_json[key])
                    dic[key] = dic_json[key]
                else:
                    print("****key--：%s value--: %s"%(key,dic_json[key]))
                    dic[key] = dic_json[key]
        else:
            pass

# 初始化全局参数中的用例类型param_type='3'的参数值
def Init_GlobalParameter(self,pid):
    # 初始化日志
    log_name = 'init_gp_' + random_str(6) + '.log'
    log_batch = 'Init_GlobalParameter'
    self.log_init_gp = Log.get_log(log_name, log_batch, 'init_gp')
    self.logger_init_gp = self.log_init_gp.get_logger()
    self.logger_init_gp.info("-------初始化全局参数开始！-------")
    all_gparam = GlobalParameterInfo.objects.filter(Q(belong_project_id=pid) & Q(param_type='3'))
    for obj in all_gparam:
        # 获取并打印用例类型param_type='3'的参数名称和参数内容
        gparam_name = obj.name
        gparam_content = eval(obj.param_content)
        # print("gparam_name:", gparam_name)
        # print("gparam_content:", obj.param_content)
        # print("gparam_content:", type(gparam_content))
        self.logger_init_gp.info("gparam_name:" + gparam_name)
        self.logger_init_gp.info("gparam_content:" + str(gparam_content))
        # 获取全局参数的关联的related_case_id
        related_case_id = obj.related_case.id
        api_name = obj.related_case.api_name
        # print("api_name:", api_name)
        all_apicase = ApiCaseInfo.objects.get(id=int(related_case_id))
        api_request = json.loads(all_apicase.api_request)
        method_type = api_request["url"]["method_type"]
        # print("method_type", method_type)

        # 初始化前后置操作
        pre_operation = []
        after_operation = []
        run_after_operation = []
        send_url = ''
        ds = {}
        headers = {}
        Cookies = {}
        request = {}
        res_dict = {}
        # 第一步：获取预置操作id，并且执行预制操作
        if all_apicase.pre_operation:
            all_pre_operation = eval(all_apicase.pre_operation)
            print("all_pre_operation:", all_pre_operation)
            # 调用前后置操作
            time.sleep(1)
            self.logger_init_gp.error("调用前后置操作:", *all_pre_operation)
            try:
                (res_dict, detail_opt) = run_opt(*all_pre_operation)
            except Exception as err:
                print("调用前后置操作失败:", *all_pre_operation)
                self.logger_init_gp.error("调用前后置操作失败:", *all_pre_operation)
            self.logger_init_gp.info("/n" + str(detail_opt) + "/n")
            print("前置操作返回参数res_dict值:", res_dict)
            self.logger_init_gp.error("前置操作返回参数res_dict值:", **res_dict)

            # print("前置操作返回参数res_dict类型:", type(res_dict))

        # 第二步：获取数据池第一行数据和请求相关数据，eg：header/cookie/request
        # 初始化全局参数，只取数据池第一行数据
        if api_request["ds"]:
            ds = api_request["ds"][0]
            if 'checkbox' in ds:
                ds.pop('checkbox')
            if 'ID' in ds:
                ds.pop('ID')
            # del ds['checkbox']
            # del ds['ID']
        # 获取接口请求url
        if api_request["url"]["host"]:
            send_host = api_request["url"]["host"]
            send_host = GlobalParameterInfo.objects.get(id=int(send_host)).value
            send_url = send_host + api_request["url"]["api_path"]
            # print("send_url:", send_url)
            self.logger_init_gp.info("send_url:" + send_url)

        else:
            print("请求url不合法！")
            self.logger_init_gp.error("请求url不合法！")
            continue

        # 获取接口请求head
        if api_request["head"]:
            head = api_request["head"]
            headers = config_disc(str(head), str(res_dict), str(ds))
            self.logger_init_gp.info("headers:" + str(headers))
            # print("headers:", headers)

        # 获取接口请求cookies
        if api_request["Cookies"]:
            Cookie = api_request["Cookies"]
            Cookies = config_disc(str(Cookie),  str(res_dict), str(ds))
            self.logger_init_gp.info("Cookies:" + str(Cookies))
            # print("Cookies:", Cookies)

        if api_request["request"]:
            # print("api_request:", api_request["request"])
            api_request = api_request["request"]
            request = config_disc(str(api_request), str(res_dict), str(ds))
            self.logger_init_gp.info("request:" + str(request))

            # print("request:", request)
        else:
            print("请求body不合法！")
            self.logger_init_gp.error("请求body不合法！")
            continue

        # 第三步：发送请求
        try:
            return_json = send_request(api_name, method_type, send_url, str(headers), str(Cookies), str(request))
        except Exception as err:
            # print("Time out!")
            self.logger_init_gp.error("Time out!")
            continue
        # 获取响应消息体
        reps_data = json.loads(show_return_data(return_json))
        self.logger_init_gp.info("\n请求返回值：" + '\n' + str(reps_data))
        # 获取响应消息头
        reps_headers = show_return_headers(return_json)
        self.logger_init_gp.info("reps_headers", reps_headers)

        # 获取响应消息cookies
        reps_cookies = show_return_cookies(return_json)
        self.logger_init_gp.info("reps_cookies", **reps_cookies)

        reps_josn = json.dumps(reps_data, ensure_ascii=False, sort_keys=True, indent=4)
        print("\n请求返回值：" + '\n' + reps_josn)
        # configHttp.logger.info("response:" + reps_josn)

        # 获取全局参数中gparam_content字典中的值,并使用jsonpath获取对应的返回值后，回填到参数对应的value字段中
        all_gparam_info = GlobalParameterInfo.objects.get(id=obj.id)
        print(all_gparam_info)

        gparme_header = gparam_content['param_header']
        print("gparme_header:", gparme_header)
        gparme_cookie = gparam_content['param_cookie']
        print("gparme_cookie:", gparme_cookie)
        gparme_path = gparam_content['param_path']
        print("gparme_path:", gparme_path)
        gparme_value = ''
        if gparme_path != '' and jsonpath.jsonpath(reps_data, gparme_path):
            # 应该jsonpath取出来的是个list所以取list的第一个元素,即[0]
            if jsonpath.jsonpath(reps_data, gparme_path)[0]:
                gparme_value = jsonpath.jsonpath(reps_data, gparme_path)[0]
                print("gparme_value:",gparme_value)

            else:
                gparme_value = ''
            all_gparam_info.value = gparme_value
            all_gparam_info.save()
        elif gparme_cookie != '':
            gparme_value = reps_cookies[gparme_cookie]
            all_gparam_info.value = gparme_value
            all_gparam_info.save()
        elif gparme_header != '':
            gparme_value = reps_headers[gparme_header]
            all_gparam_info.value = gparme_value
            all_gparam_info.save()
        else:
            all_gparam_info.value = gparme_value
            all_gparam_info.save()

        # 第四步：获取执行后操作,并且执行
        if all_apicase.run_after_operation:
            all_run_after_operation = eval(all_apicase.run_after_operation)
            print("all_run_after_operation:", all_run_after_operation)
            self.logger_init_gp.info("调用执行后操作：", *all_run_after_operation)
            # 调用后置操作
            print("调用执行后操作操作", str(all_run_after_operation))
            try:
                (res_dict_run_after, detail_opt_run_after) = run_opt(*all_run_after_operation)
            except Exception as err:
                self.logger_init_gp.error("调用执行后操作失败！")
            self.logger_init_gp.info("/n" + str(detail_opt_run_after) + "/n")

        # 第五步：获取后置操作,并且执行
        if all_apicase.after_operation:
            all_after_operation = eval(all_apicase.after_operation)
            # print("all_pre_operation:", all_after_operation)
            self.logger_init_gp.info("调用后置操作：", *all_after_operation)
            # 调用后置操作
            print("调用后置操作", str(all_after_operation))
            try:
                (res_dict_after, detail_opt_after) = run_opt(*all_after_operation)
            except Exception as err:
                self.logger_init_gp.error("调用后置操作失败！")
            self.logger_init_gp.info("/n" + str(detail_opt_after) + "/n")

    self.logger_init_gp.info("-------初始化全局参数结束！-------")

    Init_GP_detail = self.log_init_gp.get_logContent()
    print("Init_GP_detail", Init_GP_detail)
    self.log_init_gp.remove_handler()
    return Init_GP_detail

# 初始化前后置操作，根据接口请求返回字典res_dict
def run_opt(self, *opt_id):
    # 初始化日志
    log_name = 'run_opt_' + random_str(6) + '.log'
    log_batch = 'run_opt'
    self.log_opt = Log.get_log(log_name, log_batch, 'run_opt')
    self.logger_opt = self.log_opt.get_logger()
    self.logger_opt.info("-------执行前后置操作开始！-------")
    self.logger_opt.info("前后置操作id:" + str(opt_id))
    # opt_id: ['5', '6']
    # 定义返回值res_dict
    global res_dict
    res_dict = {}
    for i in opt_id:
        # 这里过滤掉删除状态的操作,all_opts.type=1 表示用例类型的前后置操作
        all_opts = OperationInfo.objects.get(Q(id=int(i)) & Q(status='1'))
        # 等待类型的操作，调用time
        if all_opts.type == '2':
            times = int(all_opts.operation)
            time.sleep(times)
            print("Time sleep：", times, "秒")
            self.logger_opt.info("Time sleep：" + str(times) + "秒")

            # configHttp.logger.info("Time sleep:" + str(times) + "秒")
        # 用例类型的操作，调用调用requests，发送请求
        if all_opts.type == '0':
            # 获取请求提取内容字典
            # opt_operation = map(eval, all_opts.operation)
            opt_operation = json.loads(all_opts.operation)
            # print("opt_operation:", opt_operation)
            # print("opt_operation_type:", type(opt_operation))
            # 获取操作关联的用例类
            all_apicase = ApiCaseInfo.objects.get(id=int(all_opts.related_case.id))
            # api_method = all_apicase.api_method
            api_id = all_apicase.id
            api_name = all_apicase.api_name
            self.logger_opt.info("操作管理用例ID和名称" + str(api_id) + "_" + str(api_name))
            api_request = json.loads(all_apicase.api_request)
            method_type = api_request["url"]["method_type"]
            # 第二步：获取数据池第一行数据和请求相关数据，eg：header/cookie/request
            ds = {}
            headers = {}
            Cookies = {}
            request = {}
            # 初始化全局参数，只取数据池第一行数据
            if api_request["ds"]:
                ds = api_request["ds"][0]
                if 'checkbox' in ds:
                    ds.pop('checkbox')
                if 'ID' in ds:
                    ds.pop('ID')
            # 获取接口请求url
            if api_request["url"]["host"]:
                send_host = api_request["url"]["host"]
                send_host = GlobalParameterInfo.objects.get(id=int(send_host)).value
                send_url = send_host + api_request["url"]["api_path"]
                self.logger_opt.info("send_url:" + send_url)
            else:
                print("请求url不合法！")
                self.logger_opt.info("请求url不合法！")
                continue
            # 获取接口请求head
            if api_request["head"]:
                head = api_request["head"]
                # print("head:", head)
                headers = config_disc(str(headers),str(res_dict),str(ds))
                print("headers:", headers)
                self.logger_opt.info("headers:" + str(headers))
            # 获取接口请求cookies
            if api_request["Cookies"]:
                Cookie = api_request["Cookies"]
                Cookies = config_disc(str(Cookie),str(res_dict),str(ds))
                print("Cookies:", Cookies)
                self.logger_opt.info("Cookies:" + str(Cookies))
            # 获取接口请求消息体request
            if api_request["request"]:
                # print(api_request["request"])
                request_data = api_request["request"]
                request = config_disc(str(request_data),str(res_dict),str(ds))
                print("request:", request)
                self.logger_opt.info("request:" + str(request))
            else:
                print("请求body不合法！")
                self.logger_opt.info("请求body不合法！")
                continue
            # 第三步：发送请求
            try:
                return_json = send_request(api_name, method_type, send_url, str(headers), str(Cookies), str(request))
            except Exception as err:
                self.logger_opt.info("Time out！")
                continue
            # 获取响应消息体
            reps_data = json.loads(show_return_data(return_json))
            # 获取响应消息头
            reps_headers = show_return_headers(return_json)
            # 获取响应消息cookies
            reps_cookies = show_return_cookies(return_json)
            # print("url:", return_json.url)
            # self.logger_opt.info("url:" + str(return_json.url))
            print(str(return_json.request))
            print("reps_headers:", reps_headers)
            self.logger_opt.info("reps_headers:" + str(reps_headers))
            print("reps_cookies:", reps_cookies)
            self.logger_opt.info("reps_cookies:" + str(reps_cookies))
            reps_josn = json.dumps(reps_data, ensure_ascii=False, sort_keys=True, indent=4)
            print("\n请求返回值：" + '\n' + reps_josn)
            self.logger_opt.info("\n请求返回值:" + '\n' + str(reps_josn))
            # 根据接口返回，取前后置操作的operation，给数据池/参数取值
            self.logger_opt.info("根据接口返回，取前后置操作的operation，给数据池/参数取值")
            for operation in opt_operation:
                # print("operation:", operation)
                # print("operation_type:", type(operation))
                opt_res_name = operation['ParamName']
                if operation['JsonPath'] != '' and jsonpath.jsonpath(reps_data, operation['JsonPath'])[0]:
                    opt_res_value = jsonpath.jsonpath(reps_data, operation['JsonPath'])[0]
                elif operation['CookieName'] != '' and reps_cookies[operation['CookieName']]:
                    opt_res_value = reps_cookies[operation['CookieName']]
                elif operation['HeaderName'] != '' and reps_headers[operation['HeaderName']]:
                    opt_res_value = reps_headers[operation['HeaderName']]
                else:
                    opt_res_value = ''
                res_dict.update({opt_res_name: opt_res_value})
    print("res_dict:", res_dict)
    self.logger_opt.info("res_dict:" + str(res_dict))
    self.logger_opt.info("-------执行前后置操作结束！-------")
    detail_opt = self.log_opt.get_logContent()
    self.log_opt.remove_handler()
    return (res_dict, str(detail_opt))

# 初始化header，cookies，request，dictPre：前置操作返回的字典：dictDs数据池
def config_disc(dictArg, dictPre, dictDs):
    dictArg = eval(dictArg)
    dictPre = eval(dictPre)
    dictDs = eval(dictDs)
    init_dict = {}
    for key in dictArg:
        # print("head1_key:", key)
        # 删除head的dict字典中的名称为0的元素，即：前端传过来的复选框
        # del key['0']
        # 判断操作是不是从全局参数里面取值
        # 删除key字典中的名称为0的元素，即：前端传过来的复选框
        if '0' in key:
            key.pop('0')
            # 判断操作是不是从前置操作返回的res_dict里面取值
        if key['param_value'].startswith('${pre.') and key['param_value'].endswith('}'):
            p_value = key['param_value'][6:-1]
            if p_value in dictPre:
                param_value = dictPre[p_value]
            else:
                param_value = ''
            init_dict.update({key['param_name']: param_value})

            # 判断操作是不是从数据池里面取值，默认取数据池第一行对应参数的值
        elif key['param_value'].startswith('${ds.') and key['param_value'].endswith('}'):
            p_value = key['param_value'][5:-1]
            if p_value in dictDs:
                param_value = dictDs[p_value]
            else:
                param_value = ''
            init_dict.update({key['param_name']: param_value})

        elif key['param_value'].startswith('${') and key['param_value'].endswith('}'):
                #  str[2:-1] #截取第二位与倒数倒数第一位之前的字符
            p_value = key['param_value'][2:-1]
            if GlobalParameterInfo.objects.get(name=p_value).value:
                param_value = GlobalParameterInfo.objects.get(name=p_value).value
            else:
                param_value = ''
            init_dict.update({key['param_name']: param_value})

            # 如果以上都不是则写的固定的值
        else:
            init_dict.update({key['param_name']: key['param_value']})
    return init_dict

# 初始化include_check, httpcode_check ,no_include_check
def config_check(ckeck, dictPre, dictDs):
    dictPre = eval(dictPre)
    dictDs = eval(dictDs)
    if ckeck.startswith('${pre.') and ckeck.endswith('}'):
        ckeck = ckeck[6:-1]
        if ckeck in dictPre:
            ckeck = dictPre[ckeck]
        else:
            ckeck = ''
            # 判断操作是不是从数据池里面取值，默认取数据池第一行对应参数的值
    elif ckeck.startswith('${ds.') and ckeck.endswith('}'):
        ckeck = ckeck[5:-1]
        if ckeck in dictDs:
            ckeck = dictDs[ckeck]
        else:
            ckeck = ''
    elif ckeck.startswith('${') and ckeck.endswith('}'):
        #  str[2:-1] #截取第二位与倒数倒数第一位之前的字符
        ckeck = ckeck[2:-1]
        if GlobalParameterInfo.objects.get(name=ckeck).value:
            ckeck = GlobalParameterInfo.objects.get(name=ckeck).value
        else:
            ckeck = ''
            # 如果以上都不是则写的固定的值
    else:
        ckeck = ckeck
    return ckeck

# 初始化json检查点
def config_check_json(ckeck_json, dictPre, dictDs):
    ckeck_json = eval(ckeck_json)
    dictPre = eval(dictPre)
    dictDs = eval(dictDs)
    for key in ckeck_json:
        # 判断操作是不是从前置操作返回的res_dict里面取值
        if key['json_value'].startswith('${pre.') and key['json_value'].endswith('}'):
            p_value = key['json_value'][6:-1]
            if p_value in dictPre:
                param_value = dictPre[p_value]
                key['json_value'] = param_value
            else:
                key['json_value'] = ''
        # 判断操作是不是从数据池里面取值，默认取数据池第一行对应参数的值
        elif key['json_value'].startswith('${ds.') and key['json_value'].endswith('}'):
            p_value = key['json_value'][5:-1]
            if p_value in dictDs:
                param_value = dictDs[p_value]
                key['json_value'] = param_value
            else:
                key['json_value'] = ''
        # 判断操作是不是从全职参数里面取值，默认取数据池第一行对应参数的值
        elif key['json_value'].startswith('${') and key['json_value'].endswith('}'):
            #  str[2:-1] #截取第二位与倒数倒数第一位之前的字符
            p_value = key['json_value'][2:-1]
            if GlobalParameterInfo.objects.get(name=p_value).value:
                param_value = GlobalParameterInfo.objects.get(name=p_value).value
                key['json_value'] = param_value
            else:
                key['json_value'] = ''
        # 如果以上都不是则写的固定的值
        else:
            pass
    return ckeck_json

# 发送请求
def send_request(api_name, method_type, url, headers, cookies, request):
    configHttp = ConfigHttp.ConfigHttp()
    # configHttp.logger.info("api_name:" + api_name)
    # 设置请求url/headers/request data
    # configHttp.logger.info("send_url:" + url)
    # print("send_type:", method_type)
    # print("send_url:", url)
    # configHttp.logger.info("headers:" + headers)
    # print("headers:", headers)
    # configHttp.logger.info("cookies:" + cookies)
    # print("cookies:", cookies)
    # configHttp.logger.info("request data:" + request)
    # print("request data:", request)

    configHttp.set_url(url)
    configHttp.set_headers(eval(headers))
    configHttp.set_cookies(eval(cookies))
    if method_type == "POST":
        configHttp.set_data(eval(request))
        try:
            return_json = configHttp.postWithJson()
        except Exception as err:
            print("Time out")
            return None

    elif method_type == "GET":
        configHttp.set_params(eval(request))
        try:
            return_json = configHttp.get()
        except Exception as err:
            print("Time out")
            return None
    else:
        return None
    return return_json

# 验证返回的httpcode_check include_check no_include_check是否正确
def checkResult(httpcode_check, include_check, no_include_check, res_httpcode, reps_headers, reps_cookies, reps_data, *json_check):
    reps_headers = eval(reps_headers)
    reps_cookies = eval(reps_cookies)
    print("2222")

    try:
        reps_data = eval(reps_data)
    except Exception as err:
        run_status = '0'
        return run_status
    print("res_httpcode：", res_httpcode)
    print("reps_headers:", reps_headers)
    print("reps_cookies:", reps_cookies)
    print("reps_data:", reps_data)

    print("json_check:", json_check)
    #
    print("httpcode_check", httpcode_check)
    print("include_check", include_check)
    print("include_check_type",type(include_check))
    print("no_include_check", no_include_check)
    print("no_include_check", no_include_check)

    if str(httpcode_check) != str(res_httpcode):
        print("httpcode_check:", httpcode_check)
        print("res_httpcode", res_httpcode)
        run_status = '0'
        return run_status


    elif include_check and not(include_check in reps_data or include_check in str(reps_data.values())):
        run_status = '0'
        return run_status

    elif no_include_check and (no_include_check in reps_data or no_include_check in str(reps_data.values())):
        run_status = '0'

        return run_status
    # {'json_key': '$.code', 'json_compare': '==', 'json_value': 200},
    else:
        run_status = '1'

    for key in json_check:
        json_key = jsonpath.jsonpath(reps_data, key['json_key'])
        json_key_one = str(json_key[0])
        json_value = str(key['json_value'])
        json_compare = key['json_compare']
        print("json_key", json_key)
        print("json_value", json_value)
        print("json_compare", json_compare)

        if json_compare == '==' and json_key_one == json_value:
            pass
        elif json_compare == '>' and json_key_one > json_value:
            pass
        elif json_compare == '>=' and json_key_one >= json_value:
            pass
        elif json_compare == '<' and json_key_one < json_value:
            pass
        elif json_compare == '<=' and json_key_one <= json_value:
            pass
        elif json_compare == '!=' and json_key_one != json_value:
            pass
        elif json_compare == 'one_Contains' and type(json_key) is list and type(json_value) is list:
            if set(json_key) >= set(json_value):
                pass
            else:
                run_status = '0'
                break
        elif json_compare == 'Contains_one' and type(json_key) is list and type(json_value) is list:
            if set(json_key) <= set(json_value):
                pass
            else:
                run_status = '0'
                break
        elif json_compare == 'NotContains'and type(json_key) is list and type(json_value) is list:
            if set(json_key) != set(json_value):
                pass
            else:
                run_status = '0'
                break
        else:
            run_status = '0'
            break

    return run_status







