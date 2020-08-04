from __future__ import absolute_import, unicode_literals
from django.shortcuts import render,HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.generic.base import View
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from api.models import EnvInfo,GlobalParameterInfo, ApiCaseInfo, OperationInfo, RunApiResultInfo, RunApiPlanInfo
from api.forms import AddGlobalParameterForm, ModifyGlobalParameterForm, AddOptsForm, ModifyoOptsForm
from manager.models import ProjectInfo,ServiceInfo
from django.db.models import Q
from utils.common import Init_GlobalParameter, run_opt, config_disc, send_request, show_return_data, show_return_cookies, show_return_headers, config_check, config_check_json, checkResult, random_str
from datetime import datetime
import json
from utils.Log import MyLog as Log
from mycelery.runcase.tasks import run_search_case, run_single_case
# Create your views here.
from api.forms import AddEnvForm, ModifyEnvForm

# 运行环境列表
class EnvListView(View):
    def get(self,request):
        # 从cookie中获取选中的项目id
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id != '':
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            page_num = request.GET.get('page_num','')
            pa = Paginator(all_env,10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'api/env_list.html', {
                "all_env": all_env,
                "pages":pages,
            })
        else:
            return render(request, 'api/env_list.html', {
                "msg": "belong_project_id不能为空",
                "code":500,
            })

# 新增运行环境
class AddEnvView(View):

    def get(self, request):
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id:
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            return render(request, "api/env_add.html",
                          {
                              "all_env": all_env,
                          })
        else:
            return render(request, "api/env_add.html",
                          {
                              "msg": "p_id不能为空！",
                          })

    def post(self, request):
        belong_project_id = request.COOKIES["p_id"]
        AddEnv_Form = AddEnvForm(request.POST)
        if belong_project_id != '':
            if AddEnv_Form.is_valid():
                env_name = request.POST.get("env_name", "")
                # print("name:",env_name)
                base_url = request.POST.get("base_url", "")
                desc = request.POST.get("desc", "")
                evn_info = EnvInfo()
                if EnvInfo.objects.filter(env_name=env_name):
                    return render(request, "api/env_add.html",
                                  {"AddEnv_Form":AddEnv_Form,
                                   "msg": "新增失败,环境已经存在!",
                                   })
                #操作外键的的时候，必须要先实例化外键对应的mode
                project_id = ProjectInfo.objects.get(id=int(belong_project_id))
                evn_info.env_name = env_name
                evn_info.base_url = base_url
                evn_info.desc = desc
                evn_info.belong_project = project_id
                evn_info.save()
                return HttpResponseRedirect(reverse("api:EnvList"))

            else:
                return render(request, "api/env_add.html",
                              {
                                  "AddEnv_Form":AddEnv_Form,
                                  "msg": "新增环境失败！",
                              })
        else:
            return render(request, "api/env_add.html",
                              {
                                  "AddEnv_Form":AddEnv_Form,
                                  "msg": "请选择一个项目！",
                              })

# 修改运行环境
class ModifyEnvView(View):
    def get(self, request, env_id):
        all_env = EnvInfo.objects.get(id=int(env_id))
        return render(request, "api/env_modify.html", {
            "all_env": all_env,
        })

    def post(self, request, env_id):
        all_env = EnvInfo.objects.get(id=int(env_id))
        ModifyEnv_Form = ModifyEnvForm(request.POST)
        if ModifyEnv_Form.is_valid():
            env_name = request.POST.get("env_name", "")
            desc = request.POST.get("desc", "")
            base_url = request.POST.get("base_url", "")
            if EnvInfo.objects.filter(env_name=env_name).exclude(id=env_id):
                return render(request, "api/env_modify.html",
                              {"ModifyEnv_Form": ModifyEnv_Form,
                               "all_env":all_env,
                               "msg": "修改失败,环境名称已经存在!",
                               })

            # 操作外键的的时候，必须要先实例化外键对应的mode
            all_env.env_name = env_name
            all_env.base_url = base_url
            all_env.desc = desc
            # project_info.creator = creator
            all_env.save()
            return HttpResponseRedirect(reverse("api:EnvList"))
            # return HttpResponse('{"status":"success", "msg":"修改成功"}', content_type='application/json')

        else:
            return render(request, "api/env_modify.html",
                          {
                              "ModifyEnv_Form": ModifyEnv_Form,
                              "all_env":all_env,
                              "msg": "修改环境信息失败！",
                          })

# 删除运行环境
class DelEnvView(View):
    def post(self, request):
        env_id = request.POST.get("env_id", "")
        if env_id:
            all_env = EnvInfo.objects.get(id=int(env_id))
            all_env.delete()
            # print(all_service.status)
            return JsonResponse({"msg": "删除成功","code": 200})
        else:
            return JsonResponse({"msg": "删除环境失败，环境ID不存在！", "code": 500})

# 全局参数列表
class GlobalParameterListView(View):
    def get(self,request):
        # 从cookie中获取选中的项目id
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id != '':
            all_parameter = GlobalParameterInfo.objects.filter(belong_project_id=belong_project_id).order_by("-add_time")
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            search_key = request.GET.get('search_key','')
            # 按照关键字搜索
            if search_key:
                all_parameter = all_parameter.filter(Q(name__icontains=search_key) | Q(desc__icontains=search_key) | Q(value__icontains=search_key))
            select_env = request.GET.get('select_env', '')
            # 按照环境搜索
            if select_env:
                all_parameter = all_parameter.filter(belong_env=int(select_env)).order_by("-add_time")
            page_num = request.GET.get('page_num','')
            pa = Paginator(all_parameter,10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'api/GlobalParameter_list.html', {
                "all_parameter": all_parameter,
                "all_env":all_env,
                "pages":pages,
                "search_key":search_key,
                "select_env":select_env
            })
        else:
            return render(request, 'api/GlobalParameter_list.html', {
                "msg": "belong_project_id不能为空",
                "code":500
            })

# 新增全局参数
class AddGlobalParameterView(View):

    def get(self, request):
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id:
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            # 过滤掉已经删除的用例
            all_apicase = ApiCaseInfo.objects.filter(Q(belong_project_id=belong_project_id) & Q(type__in=['0','1','2'])).order_by("-add_time")
            return render(request, "api/GlobalParameter_add.html",
                          {
                              "all_env": all_env,
                              "all_apicase":all_apicase
                          })
        else:
            return render(request, "api/GlobalParameter_add.html",
                          {
                              "msg": "p_id不能为空！",

                          })

    def post(self, request):
        belong_project_id = request.COOKIES["p_id"]
        AddGlobalParameter_Form = AddGlobalParameterForm(request.POST)
        if belong_project_id != '':
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            if AddGlobalParameter_Form.is_valid():
                name = request.POST.get("name", "")
                desc = request.POST.get("desc", "")
                param_type = request.POST.get("param_type", "")
                belong_env_id = request.POST.get("belong_env", "")
                parameter_info = GlobalParameterInfo()
                parameter_info.name = name
                parameter_info.desc = desc
                related_case_id = request.POST.get("related_case_id", "")
                parameter_info.param_type = param_type
                belong_env = EnvInfo.objects.get(id=int(belong_env_id))
                parameter_info.belong_env = belong_env
                parameter_info.belong_project_id = belong_project_id
                if GlobalParameterInfo.objects.filter(Q(name=name) & Q(belong_env=int(belong_env_id)) & Q(belong_project_id=belong_project_id)):
                    return render(request, "api/env_add.html",
                                  {"AddGlobalParameter_Form": AddGlobalParameter_Form,
                                   "msg": "新增失败,同一环境下参数名称已经存在!",
                                   })
                elif param_type == '1':
                    value = request.POST.get("value", "")
                    parameter_info.value = value
                    parameter_info.save()
                    return HttpResponseRedirect(reverse("api:GlobalParameterList"))

                elif param_type == '2':
                    param_content = request.POST.get("param_content", "")
                    # print("param_content:",param_content)
                    parameter_info.param_content = param_content
                    parameter_info.save()
                    return HttpResponseRedirect(reverse("api:GlobalParameterList"))

                elif param_type == '3' and related_case_id:
                    related_case_id = ApiCaseInfo.objects.get(id=int(related_case_id))
                    param_header = request.POST.get("param_header", "")
                    param_cookie = request.POST.get("param_cookie", "")
                    param_path = request.POST.get("param_path", "")
                    param_content = {'param_header':param_header,'param_cookie':param_cookie,'param_path':param_path}
                    parameter_info.related_case = related_case_id
                    parameter_info.param_content = param_content
                    parameter_info.save()
                    return HttpResponseRedirect(reverse("api:GlobalParameterList"))

                else:
                    return render(request, "api/GlobalParameter_add.html",
                                  {
                                      "AddGlobalParameter_Form": AddGlobalParameter_Form,
                                      "msg": "param_type类型或者related_case_id不合法！",
                                      "all_env": all_env,
                                  })
            else:
                return render(request, "api/GlobalParameter_add.html",
                              {
                                  "AddGlobalParameter_Form":AddGlobalParameter_Form,
                                  "msg": "新增参数失败！",
                                  "all_env":all_env,
                              })
        else:
            return render(request, "api/GlobalParameter_add.html",
                          {
                                  "AddGlobalParameter_Form":AddGlobalParameter_Form,
                                  "msg": "belong_project_id不存在，请选择一个项目！",
                        })

# 修改全局参数
class ModifyGlobalParameterView(View):
    def get(self,request,param_id):
        all_parameter = GlobalParameterInfo.objects.get(id=int(param_id))
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id:
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            all_apicase = ApiCaseInfo.objects.filter(Q(belong_project_id=belong_project_id) & Q(type__in=['0','1','2'])).order_by("-add_time")

            return render(request, "api/GlobalParameter_modify.html", {
                "all_parameter": all_parameter,
                "all_env":all_env,
                "all_apicase":all_apicase
            })
        else:
            return render(request, "api/GlobalParameter_modify.html", {
                "all_parameter": all_parameter,
                "msg": "COOKIES中p_id不存在,请先选择项目！"

            })

    def post(self,request,param_id):
        all_parameter = GlobalParameterInfo.objects.get(id=int(param_id))
        ModifyGlobalParameter_Form = ModifyGlobalParameterForm(request.POST)
        if ModifyGlobalParameter_Form.is_valid():
            name = request.POST.get("name", "")
            desc = request.POST.get("desc", "")
            param_type = request.POST.get("param_type", "")
            belong_env_id = request.POST.get("belong_env", "")
            all_parameter.name = name
            all_parameter.desc = desc
            all_parameter.param_type = param_type
            belong_env = EnvInfo.objects.get(id=int(belong_env_id))
            all_parameter.belong_env = belong_env
            if GlobalParameterInfo.objects.filter(Q(name=name) & Q(belong_env=int(belong_env_id))).exclude(id=param_id):
                return render(request, "api/GlobalParameter_modify.html",
                              {"ModifyGlobalParameter_Form": ModifyGlobalParameter_Form,
                               "msg": "修改失败,同一环境下参数名称已经存在!",
                               })
            elif param_type == '1':
                value = request.POST.get("value", "")
                all_parameter.value = value
                all_parameter.param_content = ''
                all_parameter.related_case_id = None
                all_parameter.save()
                return HttpResponseRedirect(reverse("api:GlobalParameterList"))

            elif param_type == '2':
                param_content = request.POST.get("param_content", "")
                # print("param_content:", param_content)
                all_parameter.param_content = param_content
                all_parameter.value = ''
                all_parameter.related_case_id = None
                all_parameter.save()
                return HttpResponseRedirect(reverse("api:GlobalParameterList"))

            elif param_type == '3':
                related_case_id = request.POST.get("related_case_id", "")
                # 实例化related_case_id
                related_case_id = ApiCaseInfo.objects.get(id=int(related_case_id))
                param_header = request.POST.get("param_header", "")
                param_cookie = request.POST.get("param_cookie", "")
                param_path = request.POST.get("param_path", "")
                param_content = {'param_header': param_header, 'param_cookie': param_cookie, 'param_path': param_path}
                all_parameter.related_case_id = related_case_id
                all_parameter.param_content = param_content
                all_parameter.value = ''
                all_parameter.save()
                return HttpResponseRedirect(reverse("api:GlobalParameterList"))

            else:
                return render(request, "api/GlobalParameter_modify.html",
                              {
                                  "ModifyGlobalParameter_Form": ModifyGlobalParameter_Form,
                                  "msg": "param_type类型不合法！",
                              })
        else:
            return render(request, "api/GlobalParameter_modify.html",
                          {
                              "ModifyGlobalParameter_Form": ModifyGlobalParameter_Form,
                              "msg": "新增参数失败！",
                          })

# 删除全局参数
class DelGlobalParameterView(View):
    def post(self, request):
        param_id = request.POST.get("param_id", "")
        if param_id:
            all_env = GlobalParameterInfo.objects.get(id=int(param_id))
            all_env.delete()
            # print(all_service.status)
            return JsonResponse({"msg": "删除成功","code": 200})
        else:
            return JsonResponse({"msg": "删除失败，param_id不存在！", "code": 500})

# API接口用例列表
class ApiCaseListView(View):
    def get(self, request):
        # 从cookie中获取选中的项目id
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id != '':
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            all_apicase = ApiCaseInfo.objects.filter(belong_project_id=belong_project_id).order_by("-add_time")
            all_service = ServiceInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            # 按照关键字搜索
            search_key = request.GET.get('search_key', '')
            if search_key:
                all_apicase = all_apicase.filter(
                    Q(api_name__icontains=search_key) | Q(api_method__icontains=search_key))
            select_env = request.GET.get('select_env', '')
            # 按照环境搜索
            if select_env:
                all_apicase = all_apicase.filter(belong_env_id=select_env).order_by("-add_time")
            # 按照服务搜索
            select_service = request.GET.get('select_service', '')
            if select_service:
                all_apicase = all_apicase.filter(belong_service=int(select_service)).order_by("-add_time")
            # 按照类型搜索
            select_type = request.GET.get('select_type', '')
            if select_type:
                all_apicase = all_apicase.filter(type=select_type).order_by("-add_time")
            else:
                # 过滤删除状态的用例
                all_apicase = all_apicase.filter(type__in=['0', '1', '2']).order_by("-add_time")
            page_num = request.GET.get('page_num', '')
            pa = Paginator(all_apicase, 10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'api/ApiCase_list.html', {
                "all_apicase": all_apicase,
                "pages": pages,
                "all_env": all_env,
                "all_service": all_service,
                "search_key": search_key,
                "select_env": select_env,
                "select_service": select_service,
                "select_type": select_type,
            })
        else:
            return render(request, 'api/ApiCase_list.html', {
                "msg": "belong_project_id不能为空",
                "code": 500,
            })

# 删除api接口
class DelApiCaseView(View):
    def post(self, request):
        api_id = request.POST.get("api_id", "")
        if api_id:
            api_info = ApiCaseInfo.objects.get(id=int(api_id))
            if api_info.type == '3':
                return JsonResponse({"msg": "当前接口状态已经是删除状态！", "code": 500})
            else:
                api_info.type = '3'
                api_info.save()
                # print(all_service.status)
                return JsonResponse({"msg": "删除成功！","code": 200})
        else:
            return JsonResponse({"msg": "删除失败，api_id！", "code": 500})

# 新增api接口
class AddApiCaseView(View):
    def get(self,request):
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id:
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            all_service = ServiceInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            all_gparam_host = GlobalParameterInfo.objects.filter(Q(param_type=1) & Q(name__icontains="HOST")).order_by("-add_time")
            all_opts = OperationInfo.objects.filter(Q(belong_project_id=int(belong_project_id)) & Q(status=1)).order_by("-add_time")
            return render(request, "api/ApiCase_add.html",
                          {
                              "all_env": all_env,
                              "all_service": all_service,
                              "all_opts": all_opts,
                              "all_gparam_host":all_gparam_host,
                          })
        else:
            return render(request, "api/ApiCase_add.html",
                          {
                              "msg": "p_id不能为空！",
                          })
    def post(self, request):
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id != '':
            api_name = request.POST.get("api_name", "")
            if api_name != '':
                api_method = request.POST.get("api_method", "")
                belong_service = request.POST.get("belong_service", "")
                belong_env_id = request.POST.get("belong_env", "")
                type = request.POST.get("type", "")
                pre_operation = request.POST.getlist("pre_operation", "")
                api_request = request.POST.get("api_request", "")
                after_operation = request.POST.getlist("after_operation", "")
                run_after_operation = request.POST.getlist("RunAfterOpsList", "")
                # print ("run_after_operation=",run_after_operation)
                if ApiCaseInfo.objects.filter(api_name=api_name):
                    return JsonResponse({"msg": "新增失败,接口名称不能为空或已经存在！", "code": 500}, content_type='application/json')
                else:
                    ApiCase_Info = ApiCaseInfo()
                    ApiCase_Info.api_name = api_name
                    ApiCase_Info.api_method = api_method
                    ApiCase_Info.belong_project_id = belong_project_id
                    # 操作外键的的时候，必须要先实例化外键对应的mode
                    belong_service = ServiceInfo.objects.get(id=int(belong_service))
                    ApiCase_Info.belong_service = belong_service
                    ApiCase_Info.belong_env_id = belong_env_id
                    ApiCase_Info.type = type
                    ApiCase_Info.pre_operation = pre_operation
                    ApiCase_Info.api_request = api_request
                    ApiCase_Info.run_after_operation = run_after_operation
                    ApiCase_Info.after_operation = after_operation
                    ApiCase_Info.designer = request.user.username
                    ApiCase_Info.save()
                    return JsonResponse({"msg": "操作成功！", "code": 200}, content_type='application/json')
            else:
                return JsonResponse({"msg": "用例名称不能为空！", "code": 500}, content_type='application/json')
        else:
            return JsonResponse({"msg": "版本id不存在，请详见项目！", "code": 500}, content_type='application/json')

# 修改api接口
class ModifyApiCaseView(View):
    def get(self, request,api_id):
        all_apicase = ApiCaseInfo.objects.get(id=int(api_id))
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id:
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            all_service = ServiceInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            all_gparam_host = GlobalParameterInfo.objects.filter(Q(param_type=1) & Q(name__icontains="HOST")).order_by("-add_time")
            all_opts = OperationInfo.objects.filter(Q(belong_project_id=int(belong_project_id)) & Q(status=1)).order_by("-add_time")
            api_request = json.loads(all_apicase.api_request)
            # 初始化前后置操作
            select_pre_operation = []
            select_after_operation = []
            select_run_after_operation = []
            data_Columns = []
            # 获取预置操作
            if all_apicase.pre_operation:
                all_pre_operation = eval(all_apicase.pre_operation)
                all_pre_operation = map(eval, all_pre_operation)
                select_pre_operation = OperationInfo.objects.filter(id__in=all_pre_operation)
                # 获取后置操作
            if all_apicase.after_operation:
                all_after_operation = eval(all_apicase.after_operation)
                all_after_operation = map(eval, all_after_operation)
                select_after_operation = OperationInfo.objects.filter(id__in=all_after_operation)
            # 获取执行后操作
            if all_apicase.run_after_operation:
                all_run_after_operation = eval(all_apicase.run_after_operation)
                all_run_after_operation = map(eval, all_run_after_operation)
                select_run_after_operation = OperationInfo.objects.filter(id__in=all_run_after_operation)

            if api_request["ds"]:
                # 获取请求的数据池的key作为数据池的表头，[2:]表示从第三个开始取
                data_Columns = [
                                   {
                                       'field': key,
                                       'title': key
                                   } for key in api_request["ds"][0]
                               ][2:]

            return render(request, "api/ApiCase_modify.html",
                          {
                              "all_env": all_env,
                              "all_service": all_service,
                              "all_opts": all_opts,
                              "all_gparam_host": all_gparam_host,
                              "all_apicase": all_apicase,
                              "data_Columns": data_Columns,
                              "select_pre_operation": select_pre_operation,
                              "select_after_operation": select_after_operation,
                              "select_run_after_operation": select_run_after_operation

                          })
        else:
            return render(request, "api/ApiCase_modify.html",
                          {
                              "msg": "p_id不能为空！",
                              "code": 500,
                          })
    def post(self, request,api_id):
        all_apicase = ApiCaseInfo.objects.get(id=int(api_id))
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id != '':
            api_name = request.POST.get("api_name", "")
            if api_name != '':
                api_method = request.POST.get("api_method", "")
                belong_service = request.POST.get("belong_service", "")
                belong_env_id = request.POST.get("belong_env", "")
                type = request.POST.get("type", "")
                pre_operation = request.POST.getlist("pre_operation", "")
                api_request = request.POST.get("api_request", "")
                after_operation = request.POST.getlist("after_operation", "")
                run_after_operation = request.POST.getlist("RunAfterOpsList", "")
                # print ("run_after_operation=",run_after_operation)
                if ApiCaseInfo.objects.filter(api_name=api_name).exclude(id=api_id):
                    return JsonResponse({"msg": "新增失败,用例名称已经存在！", "code": 500}, content_type='application/json')
                else:
                    all_apicase.api_name = api_name
                    all_apicase.api_method = api_method
                    all_apicase.belong_project_id = belong_project_id
                    # 操作外键的的时候，必须要先实例化外键对应的mode
                    belong_service = ServiceInfo.objects.get(id=int(belong_service))
                    all_apicase.belong_service = belong_service
                    all_apicase.belong_env_id = belong_env_id
                    all_apicase.type = type
                    all_apicase.pre_operation = pre_operation
                    all_apicase.api_request = api_request
                    all_apicase.run_after_operation = run_after_operation
                    all_apicase.after_operation = after_operation
                    all_apicase.modifier = request.user.username
                    all_apicase.save()
                    return JsonResponse({"msg": "操作成功！", "code": 200}, content_type='application/json')
            else:
                return JsonResponse({"msg": "api_name不能为空！", "code": 500}, content_type='application/json')

        else:
            return JsonResponse({"msg": "版本id不存在，请详见项目！", "code": 500}, content_type='application/json')

# 前后置操作列表
class OperationListView(View):
    def get(self, request):
        # 从cookie中获取选中的项目id
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id != '':
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            all_opts = OperationInfo.objects.filter(Q(belong_project_id=belong_project_id) & Q(status=1)).order_by("-add_time")
            # 按照关键字搜索
            search_key = request.GET.get('search_key', '')
            if search_key:
                all_opts = all_opts.filter(
                    Q(name__icontains=search_key) | Q(desc__contains=search_key))
            select_env = request.GET.get('select_env', '')
            # 按照环境搜索
            if select_env:
                all_opts = all_opts.filter(belong_env_id=select_env).order_by("-add_time")

            # 按照类型搜索
            select_type = request.GET.get('select_type', '')
            if select_type:
                all_opts = all_opts.filter(type=select_type).order_by("-add_time")
            page_num = request.GET.get('page_num', '')
            pa = Paginator(all_opts, 10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'api/Operation_list.html', {
                "all_opts": all_opts,
                "pages": pages,
                "all_env":all_env,
                "search_key": search_key,
                "select_env":select_env,
                "select_type": select_type,
            })
        else:
            return render(request, 'api/Operation_list.html', {
                "msg": "belong_project_id不能为空",
                "code": 500,
            })()

    def post(self,request):
        # 从cookie中获取选中的项目id
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id != '':
            all_opts = OperationInfo.objects.filter(Q(belong_project_id=belong_project_id) & Q(status=1))
            search_key = request.POST.get('search_key', '')
            if search_key:
                all_opts = all_opts.filter(name__icontains=search_key)
            page_num = request.POST.get('page_num', '')
            pa = Paginator(all_opts, 10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'api/OptsList.html', {
                "all_opts": all_opts,
                "pages": pages,
                "search_key":search_key,
            })
        else:
            return render(request, 'api/OptsList.html', {
                "msg": "belong_project_id不能为空",
                "code": 500,
            })

# 新增前后置操作
class AddOperationView(View):

    def get(self, request):
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id:
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            # all_apicase = ApiCaseInfo.objects.filter(Q(belong_project_id=belong_project_id) & Q(type__in=['0','1','2'])).order_by("-add_time")
            # 新增前后置操作的，只是取type='0'的用例
            all_apicase = ApiCaseInfo.objects.filter(Q(belong_project_id=belong_project_id) & Q(type='0')).order_by("-add_time")
            return render(request, "api/Operation_add.html",
                          {
                              "all_env": all_env,
                              "all_apicase":all_apicase
                          })
        else:
            return render(request, "api/Operation_add.html",
                          {
                              "msg": "p_id不能为空！",
                          })

    def post(self, request):
        belong_project_id = request.COOKIES["p_id"]
        AddOpts_Form = AddOptsForm(request.POST)
        if belong_project_id != '':
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            # all_apicase = ApiCaseInfo.objects.filter(Q(belong_project_id=belong_project_id) & Q(type__in=['0','1','2'])).order_by("-add_time")
            # 新增前后置操作的，只是取type='0'的用例
            all_apicase = ApiCaseInfo.objects.filter(Q(belong_project_id=belong_project_id) & Q(type='0')).order_by("-add_time")
            if AddOpts_Form.is_valid():
                name = request.POST.get("name", "")
                desc = request.POST.get("desc", "")
                belong_env_id = request.POST.get("belong_env", "")
                opt_type = request.POST.get("type", "")
                related_case_id = request.POST.get("related_case", "")
                case_rep_json = request.POST.get("case_rep_json", "")
                opt_sql = request.POST.get("opt_sql", "")
                opt_delay = request.POST.get("opt_delay", "")
                belong_env = EnvInfo.objects.get(id=int(belong_env_id))
                if OperationInfo.objects.filter(Q(name=name) & Q(belong_env=int(belong_env_id)) & Q(belong_project_id=belong_project_id)):
                    return render(request, "api/Operation_add.html",
                                  {"Addopts_Form": AddOpts_Form,
                                   "msg": "新增失败,同一环境下操作名称已经存在!",
                                   })
                elif opt_type == '0' and related_case_id:
                    related_case_id = ApiCaseInfo.objects.get(id=int(related_case_id))
                    opts_info = OperationInfo()
                    opts_info.name = name
                    opts_info.desc = desc
                    opts_info.type = opt_type
                    opts_info.belong_env = belong_env
                    opts_info.belong_project_id = belong_project_id
                    opts_info.related_case = related_case_id
                    opts_info.operation = case_rep_json
                    opts_info.designer = request.user.username
                    opts_info.save()
                    return HttpResponseRedirect(reverse("api:OperationList"))
                elif opt_type == '1':
                    opts_info = OperationInfo()
                    # print("param_content:",param_content)
                    opts_info.name = name
                    opts_info.desc = desc
                    opts_info.type = opt_type
                    opts_info.belong_env = belong_env
                    opts_info.belong_project_id = belong_project_id
                    opts_info.operation = opt_sql
                    opts_info.designer = request.user.username
                    opts_info.save()
                    return HttpResponseRedirect(reverse("api:OperationList"))
                elif opt_type == '2':
                    opts_info = OperationInfo()
                    opts_info.name = name
                    opts_info.desc = desc
                    opts_info.type = opt_type
                    opts_info.belong_env = belong_env
                    opts_info.belong_project_id = belong_project_id
                    opts_info.operation = opt_delay
                    opts_info.designer = request.user.username
                    opts_info.save()
                    return HttpResponseRedirect(reverse("api:OperationList"))
                else:
                    return render(request, "api/Operation_add.html",
                                  {
                                      "Addopts_Form": AddOpts_Form,
                                      "msg": "opt_type类型或者related_case_id不合法！",
                                      "all_env": all_env,
                                  })
            else:
                return render(request, "api/Operation_add.html",
                              {
                                  "Addopts_Form":AddOpts_Form,
                                  "msg": "新增参数失败！",
                                  "all_env":all_env,
                              })
        else:
            return render(request, "api/Operation_add.html",
                          {
                                  "Addopts_Form":AddOpts_Form,
                                  "msg": "belong_project_id不存在，请选择一个项目！",
                        })

# 修改前后置操作
class ModifyOperationView(View):
    def get(self,request,opt_id):
        all_opts = OperationInfo.objects.get(id=int(opt_id))
        belong_project_id = request.COOKIES["p_id"]
        all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
        # all_apicase = ApiCaseInfo.objects.filter(belong_project_id=belong_project_id).order_by("-add_time")

        if belong_project_id:
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            # 新增前后置操作的，只是取type='0'的用例
            all_apicase = ApiCaseInfo.objects.filter(Q(belong_project_id=belong_project_id) & Q(type='0')).order_by("-add_time")
            return render(request, "api/Operation_modify.html", {
                "all_env":all_env,
                "all_opts":all_opts,
                "all_apicase":all_apicase
            })
        else:
            return render(request, "api/Operation_modify.html", {
                "all_env":all_env,
                "code":500,
                "msg":"COOKIES中p_id不存在,请先选择项目！"
            })

    def post(self,request,opt_id):
        belong_project_id = request.COOKIES["p_id"]
        opts_info = OperationInfo.objects.get(id=int(opt_id))
        ModifyOpts_Form = ModifyoOptsForm(request.POST)
        if belong_project_id != '':
            all_env = EnvInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-add_time")
            # all_apicase = ApiCaseInfo.objects.filter(Q(belong_project_id=belong_project_id) & Q(type__in=['0','1','2'])).order_by("-add_time")
            # 新增前后置操作的，只是取type='0'的用例
            all_apicase = ApiCaseInfo.objects.filter(Q(belong_project_id=belong_project_id) & Q(type='0')).order_by("-add_time")
            if ModifyOpts_Form.is_valid():
                name = request.POST.get("name", "")
                desc = request.POST.get("desc", "")
                belong_env_id = request.POST.get("belong_env", "")
                opt_type = request.POST.get("type", "")
                related_case_id = request.POST.get("related_case", "")
                case_rep_json = request.POST.get("case_rep_json", "")
                opt_sql = request.POST.get("opt_sql", "")
                opt_delay = request.POST.get("opt_delay", "")
                belong_env = EnvInfo.objects.get(id=int(belong_env_id))
                if OperationInfo.objects.filter(Q(name=name) & Q(belong_env=int(belong_env_id)) & Q(belong_project_id=belong_project_id)).exclude(id=opt_id):
                    return render(request, "api/Operation_modify.html",
                                  {"ModifyOpts_Form": ModifyOpts_Form,
                                   "msg": "新增失败,同一环境下操作名称已经存在!",
                                   "all_apicase":all_apicase,
                                   "all_env":all_env,
                                   "code":500
                                   })
                elif opt_type == '0' and related_case_id:
                    related_case_id = ApiCaseInfo.objects.get(id=int(related_case_id))
                    opts_info.name = name
                    opts_info.desc = desc
                    opts_info.type = opt_type
                    opts_info.belong_env = belong_env
                    opts_info.belong_project_id = belong_project_id
                    opts_info.related_case = related_case_id
                    opts_info.operation = case_rep_json
                    opts_info.modifier = request.user.username
                    opts_info.save()
                    return HttpResponseRedirect(reverse("api:OperationList"))
                elif opt_type == '1':
                    # print("param_content:",param_content)
                    opts_info.name = name
                    opts_info.desc = desc
                    opts_info.type = opt_type
                    opts_info.belong_env = belong_env
                    opts_info.belong_project_id = belong_project_id
                    opts_info.operation = opt_sql
                    opts_info.modifier = request.user.username
                    opts_info.save()
                    return HttpResponseRedirect(reverse("api:OperationList"))
                elif opt_type == '2':
                    opts_info.name = name
                    opts_info.desc = desc
                    opts_info.type = opt_type
                    opts_info.belong_env = belong_env
                    opts_info.belong_project_id = belong_project_id
                    opts_info.operation = opt_delay
                    opts_info.modifier = request.user.username
                    opts_info.save()
                    return HttpResponseRedirect(reverse("api:OperationList"))
                else:
                    return render(request, "api/Operation_modify.html",
                                  {
                                      "ModifyOpts_Form": ModifyOpts_Form,
                                      "msg": "opt_type类型或者related_case_id不合法！",
                                      "all_apicase": all_apicase,
                                      "all_env": all_env,
                                      "code": 500
                                  })
            else:
                return render(request, "api/Operation_modify.html",
                              {
                                  "ModifyOpts_Form":ModifyOpts_Form,
                                  "msg": "新增操作失败！",
                                  "all_apicase": all_apicase,
                                  "all_env": all_env,
                                  "code": 500
                              })
        else:
            return render(request, "api/Operation_modify.html",
                          {
                                  "ModifyOpts_Form":ModifyOpts_Form,
                                  "msg": "belong_project_id不存在，请选择一个项目！",
                                  "code": 500
                            })

# 删除全局参数
class DelOperationView(View):
    def post(self, request):
        opt_id = request.POST.get("opt_id", "")
        print(opt_id)
        if opt_id:
            all_opts = OperationInfo.objects.get(id=int(opt_id))
            all_opts.status = '0'
            all_opts.save()
            # print(all_service.status)
            return JsonResponse({"msg": "删除成功","code": 200})
        else:
            return JsonResponse({"msg": "删除失败，opt_id不存在！", "code": 500})

# # 运行单个用例--备份
# class RunSingleCaseView(View):
#     def post(self, request):
#         pid = request.COOKIES["p_id"]
#         if pid != '':
#             # 定义初始化全局参数和前置操作参数
#             init_gp_log = ''
#             pre_opt_log = ''
#             case_id = request.POST.get("case_id", "")
#             # 删除单个用例执行记录,不包含批量执行的CI记录，即可：run_batch不为空的
#             result_info = RunApiResultInfo.objects.filter(Q(related_case=int(case_id)) & Q(run_batch=''))
#             result_info.delete()
#             print("<-------------初始化全局参数 开始------------->")
#             try:
#                 init_gp_log = Init_GlobalParameter(self, pid)
#             except Exception as err:
#                 print("初始化全局参数失败！")
#
#             print("<-------------初始化全局参数 结束------------->")
#             # select_ds :前台传过来选中的数据池行数据
#             select_ds = json.loads(request.POST.get("select_ds", ""))
#             all_apicase = ApiCaseInfo.objects.get(id=int(case_id))
#             api_name = all_apicase.api_name
#             # api_method = all_apicase.api_method
#             belong_env = all_apicase.belong_env.id
#             belong_service = all_apicase.belong_service.id
#             api_request = json.loads(all_apicase.api_request)
#             # 初始化前后置操作
#             pre_operation = []
#             after_operation = []
#             run_after_operation = []
#             res_dict = {}
#             # 初始化 ApiCaseInfo，belong_env
#             related_case = ApiCaseInfo.objects.get(id=int(case_id))
#             belong_env = EnvInfo.objects.get(id=int(belong_env))
#             belong_service = ServiceInfo.objects.get(id=int(belong_service))
#
#             # 第1步：获取请求URl
#             if api_request["url"]["host"] and api_request["url"]["method_type"]:
#                 send_host = api_request["url"]["host"]
#                 method_type = api_request["url"]["method_type"]
#                 send_host = GlobalParameterInfo.objects.get(id=int(send_host)).value
#                 send_url = send_host + api_request["url"]["api_path"]
#                 print("send_url:", send_url)
#             else:
#                 print("<-------------请求URL或者参数不合法------------->\n", api_name)
#                 return JsonResponse({"msg": "send_host不合法!", "code": 500})
#
#             # 第2步：获取预置操作id，并且执行预制操作
#             if all_apicase.pre_operation:
#                 all_pre_operation = eval(all_apicase.pre_operation)
#                 # 调用前置操作
#                 print("<-------------调用前置操作------------->", all_pre_operation)
#                 try:
#                     # res_dict:调用前置操作返回的字典，pre_detail_opt：日志信息
#                     (res_dict, pre_opt_log) = run_opt(self, *all_pre_operation)
#                 except Exception as err:
#                     print("调用前置操作异常!")
#
#                 print("前置操作返回参数res_dict值:", res_dict)
#             # 第3步：获取数据池,类型是个list,并且替换其中的取前置操作的值和全局操作的值
#             if api_request["ds"]:
#                 # 判断前台传过来选中的数据池数据是否为空，如果未空，就执行所有数据
#                 if len(select_ds) == 0:
#                     ds = api_request["ds"]
#                 else:
#                     ds = select_ds
#                 print("<-------------获取数据池------------->\n", ds)
#                 for ds_line in ds:
#                     if 'checkbox' in ds_line:
#                         ds_line.pop('checkbox')
#                     if 'ID' in ds_line:
#                         ds_line.pop('ID')
#                     for dl_key, dl_value in ds_line.items():
#                         # dl_value 需要转换成str，否则如果dl_value是int的时候就会报错
#                         if str(dl_value).startswith('${pre.') and str(dl_value).endswith('}'):
#                             if res_dict:
#                                 ds_line[dl_key] = res_dict[dl_value[6:-1]]
#                             else:
#                                 ds_line[dl_key] = ''
#                         elif str(dl_value).startswith('${') and str(dl_value).endswith('}'):
#                             if GlobalParameterInfo.objects.get(name=dl_value[2:-1]).value:
#                                 dl_value = GlobalParameterInfo.objects.get(name=dl_value[2:-1]).value
#                             else:
#                                 dl_value = ''
#                             ds_line[dl_key] = dl_value
#                         else:
#                             continue
#                 print("<-------------更新后的获取数据池------------->\n",ds)
#
#                 for ds_row in ds:
#                     # 初始化日志
#                     log_name = 'case_id_' + case_id + random_str(6) + '_output.log'
#                     log_batch = 'RunSingleCase'
#                     self.log_run_single = Log.get_log(log_name, log_batch, 'run_single_case')
#                     self.logger_run_single = self.log_run_single.get_logger()
#                     self.logger_run_single.info("调用全局参数\n" + init_gp_log + "\n")
#                     self.logger_run_single.info("调用前置操作\n" + pre_opt_log + "\n")
#                     self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " START--------")
#                     self.logger_run_single.info("method_type：" + method_type)
#                     self.logger_run_single.info("send_url：" + send_url)
#
#                     headers = {}
#                     Cookies = {}
#                     requests = {}
#
#                     print("api_name:", api_name, ds.index(ds_row))
#                     # 获取接口请求head
#                     if api_request["head"]:
#                         headers = config_disc(str(api_request["head"]), str(res_dict), str(ds_row))
#                         print("headers:", headers)
#                         self.logger_run_single.info("headers：" + str(headers))
#
#                     # 获取接口请求cookies
#                     if api_request["Cookies"]:
#                         Cookies = config_disc(str(api_request["Cookies"]), str(res_dict), str(ds_row))
#                         print("Cookies:", Cookies)
#                         self.logger_run_single.info("Cookies：" + str(Cookies))
#
#
#                     # 获取接口request
#                     if api_request["request"]:
#                         # print(api_request["request"])
#                         requests = config_disc(str(api_request["request"]), str(res_dict), str(ds_row))
#                         print("requests:", requests)
#                         self.logger_run_single.info("requests：" + str(requests))
#
#
#                     else:
#                         print("请求body不合法！")
#                         self.logger_run_single.info("--------请求body不合法!--------")
#                         self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " END--------")
#
#                         # 初始化CI执行记录
#                         run_api_info = RunApiResultInfo()
#                         run_api_info.type = '1'
#                         run_api_info.belong_project_id = pid
#                         run_api_info.related_case = related_case
#                         run_api_info.belong_env = belong_env
#                         run_api_info.belong_service = belong_service
#                         run_api_info.api_name = api_name + str(ds.index(ds_row))
#                         run_api_info.detail = self.log_run_single.get_logContent()
#                         run_api_info.status = '0'
#                         run_api_info.save()
#                         self.log_run_single.remove_handler()
#                         continue
#                     # 获取校验
#                     httpcode_check = '200'
#                     include_check = ''
#                     no_include_check = ''
#                     json_check = []
#                     if api_request["check"]:
#                         if api_request["check"]["httpcode_check"]:
#                             # print(api_request["request"])
#                             httpcode_check = config_check(str(api_request["check"]["httpcode_check"]), str(res_dict), str(ds_row))
#                             # 获取的类型是str
#                             print("httpcode_check:", httpcode_check)
#                             self.logger_run_single.info("httpcode_check:" + httpcode_check)
#
#                         if api_request["check"]["include_check"]:
#                             # print(api_request["request"])
#                             include_check = config_check(str(api_request["check"]["include_check"]), str(res_dict), str(ds_row))
#                             print("include_check:", include_check)
#                             self.logger_run_single.info("include_check:" + str(include_check))
#
#                         if api_request["check"]["no_include_check"]:
#                             # print(api_request["request"])
#                             no_include_check = config_check(str(api_request["check"]["no_include_check"]), str(res_dict), str(ds_row))
#                             print("no_include_check:", no_include_check)
#                             self.logger_run_single.info("no_include_check:" + str(no_include_check))
#
#
#                         if api_request["check"]["json_check"]:
#                             # print(api_request["request"])
#                             # json_check 类型是list
#                             json_check = config_check_json(str(api_request["check"]["json_check"]), str(res_dict), str(ds_row))
#                             print("json_check:", json_check)
#                             self.logger_run_single.info("json_check:" + json_check.__str__())
#                     start_time = datetime.now()
#                     try:
#                         return_json = send_request(api_name, method_type, send_url, str(headers), str(Cookies), str(requests))
#                         end_time = datetime.now()
#                     except TimeoutError as err:
#                         print("Time out!")
#                         self.logger_run_single.info("Time out!")
#                         self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " END--------")
#
#                         # 初始化CI执行记录
#                         run_api_info = RunApiResultInfo()
#                         run_api_info.api_name = api_name + str(ds.index(ds_row))
#                         run_api_info.type = '1'
#                         run_api_info.belong_project_id = pid
#                         run_api_info.related_case = related_case
#                         run_api_info.belong_env = belong_env
#                         run_api_info.belong_service = belong_service
#                         run_api_info.detail = self.log_run_single.get_logContent()
#                         run_api_info.status = '0'
#                         run_api_info.save()
#                         self.log_run_single.remove_handler()
#                         continue
#                     # res_code : 返回报文中http状态 HTTP/1.1 200 OK。类型是int，eg：200
#                     if return_json:
#                         res_httpcode = return_json.status_code
#                         print("res_httpcode:", res_httpcode)
#                         self.logger_run_single.info("res_httpcode:"+ str(res_httpcode))
#                         reps_headers = show_return_headers(return_json)
#                         print("reps_headers:", reps_headers)
#                         self.logger_run_single.info("reps_headers:", reps_headers)
#                         reps_cookies = show_return_cookies(return_json)
#                         print("reps_cookies:", reps_cookies)
#                         self.logger_run_single.info("reps_cookies:", **reps_cookies)
#                         reps_data = show_return_data(return_json)
#                         print("reps_data:", reps_data)
#                         # print(type(reps_data))
#                         self.logger_run_single.info("请求返回值:" + '\n' + str(reps_data))
#                         try:
#                         # 调用 checkResult，执行检查点校验:
#                             run_status = checkResult(httpcode_check, include_check, no_include_check, res_httpcode,str(reps_headers), str(reps_cookies), str(reps_data), *json_check)
#                             print("run_status:", run_status)
#                         except Exception as err:
#                             self.logger_run_single.info("调用“检查点校验”异常！")
#                             run_status = '0'
#
#                     else:
#                         self.logger_run_single.error("Time out!")
#                         run_status = '0'
#                     # 获取后置操作
#                     if all_apicase.after_operation:
#                         all_after_operation = eval(all_apicase.after_operation)
#                         print("调用后置操作")
#                         self.logger_run_single.info("调用后置操作:", *all_after_operation)
#
#                         try:
#                             (after_dict, after_opt_log) = run_opt(self, *all_after_operation)
#                         except Exception as err:
#                             print("调用后置操作失败")
#                             self.logger_run_single.error("调调用后置操作失败!")
#                         self.logger_run_single.info("\n" + after_opt_log + "\n")
#
#                     # 获取执行后操作
#                     if all_apicase.run_after_operation:
#                         all_run_after_operation = eval(all_apicase.run_after_operation)
#                         print("调用运行后操作")
#                         try:
#                             (after_dict, run_after_opt_log) = run_opt(self, *all_run_after_operation)
#                         except Exception as err:
#                             print("调用运行后操作失败")
#                             self.logger_run_single.error("调用运行后操作失败!")
#                         print(str(after_dict))
#                         self.logger_run_single.info("\n" + run_after_opt_log + "\n")
#
#                     # 初始化CI执行记录
#                     run_api_info = RunApiResultInfo()
#                     run_api_info.type = '1'
#                     run_api_info.belong_project_id = pid
#                     run_api_info.related_case = related_case
#                     run_api_info.belong_env = belong_env
#                     run_api_info.belong_service = belong_service
#                     run_api_info.api_name = api_name + str(ds.index(ds_row))
#                     run_api_info.detail = self.log_run_single.get_logContent()
#                     run_api_info.status = run_status
#                     run_api_info.start_time = start_time
#                     run_api_info.end_time = end_time
#                     run_api_info.save()
#                     self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " END--------")
#                     self.log_run_single.remove_handler()
#
#                 return JsonResponse({"msg": "ok!", "code": 200})
#
#                 # return JsonResponse({"msg": "ok!", "code": 200})
#             else:
#                 # 初始化日志
#                 log_name = 'case_id_' + case_id + random_str(6) + '_output.log'
#                 log_batch = 'RunSingleCase'
#                 self.log_run_single = Log.get_log(log_name, log_batch, 'run_single_case')
#                 self.logger_run_single = self.log_run_single.get_logger()
#                 self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " START--------")
#                 self.logger_run_single.info("method_type:" + method_type)
#                 self.logger_run_single.info("send_url:" + send_url)
#                 headers = {}
#                 Cookies = {}
#                 requests = {}
#                 httpcode_check = '200'
#                 include_check = ''
#                 no_include_check = ''
#                 json_check = []
#                 if api_request["head"]:
#                     headers = config_disc(str(api_request["head"]), str(res_dict), '{}')
#                     print("headers:", headers)
#                     self.logger_run_single.info("headers:", **headers)
#                 if api_request["Cookies"]:
#                     Cookies = config_disc(str(api_request["Cookies"]), str(res_dict), '{}')
#                     print("Cookies:", Cookies)
#                     self.logger_run_single.info("Cookies:", **Cookies)
#
#                 if api_request["request"]:
#                         requests = config_disc(str(api_request["request"]), str(res_dict), '{}')
#                         print("requests:", requests)
#                         self.logger_run_single.info("Cookies:", **Cookies)
#
#                 # 获取校验
#                 if api_request["check"]:
#                         if api_request["check"]["httpcode_check"]:
#                             # print(api_request["request"])
#                             try:
#                                 httpcode_check = config_check(str(api_request["check"]["httpcode_check"]), str(res_dict),'{}')
#                                 # 获取的类型是str
#                                 print("httpcode_check:", httpcode_check)
#                                 self.logger_run_single.info("httpcode_check:" + httpcode_check)
#                             except Exception as err:
#                                 print("<-------------初始化httpcode_check失败！------------->\n")
#                                 self.logger_run_single.info("-------------初始化httpcode_check失败！-------------")
#
#                         if api_request["check"]["include_check"]:
#                             # print(api_request["request"])
#                             try:
#                                 include_check = config_check(str(api_request["check"]["include_check"]), str(res_dict), '{}')
#                                 print("include_check:", include_check)
#                                 self.logger_run_single.info("include_check:",include_check)
#                             except Exception as err:
#                                 print("<-------------初始化include_check失败！------------->\n")
#                                 self.logger_run_single.info("-------------初始化include_check失败！-------------")
#
#                         if api_request["check"]["no_include_check"]:
#                             # print(api_request["request"])
#                             try:
#                                 no_include_check = config_check(str(api_request["check"]["no_include_check"]), str(res_dict), '{}')
#                                 print("no_include_check:", no_include_check)
#                                 self.logger_run_single.info("no_include_check:", no_include_check)
#                             except Exception as err:
#                                 print("<-------------初始化include_check失败！------------->\n")
#                                 self.logger_run_single.info("-------------初始化include_check失败！-------------")
#
#                         if api_request["check"]["json_check"]:
#                             # print(api_request["request"])
#                             try:
#                                 # json_check 类型是list
#                                 json_check = config_check_json(str(api_request["check"]["json_check"]), str(res_dict), '{}')
#                                 print("json_check:", json_check)
#                                 self.logger_run_single.info("json_check:" + json_check.__str__())
#                                 # print("json_check_type:",type(json_check))
#                             except Exception as err:
#                                 print("<-------------初始化json_check失败！------------->\n")
#                                 self.logger_run_single.info("-------------初始化json_check失败！-------------")
#
#                 start_time = datetime.now()
#                 try:
#                     return_json = send_request(api_name, method_type, send_url, str(headers), str(Cookies), str(requests))
#                     end_time = datetime.now()
#                 except Exception as err:
#                     self.logger_run_single.info("Time out!")
#                     self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " END--------")
#                     print("<-------------Time out!------------->")
#                     # 初始化CI执行记录
#                     run_api_info = RunApiResultInfo()
#                     run_api_info.api_name = api_name
#                     run_api_info.type = '1'
#                     run_api_info.belong_project_id = pid
#                     run_api_info.related_case = related_case
#                     run_api_info.belong_env = belong_env
#                     run_api_info.belong_service = belong_service
#                     run_api_info.detail = self.log_run_single.get_logContent()
#                     run_api_info.status = '0'
#                     self.log_run_single.remove_handler()
#                     run_api_info.save()
#                 if return_json:
#                     res_httpcode = return_json.status_code
#                     print("res_httpcode:", res_httpcode)
#                     self.logger_run_single.info("res_httpcode", res_httpcode)
#
#                     reps_headers = show_return_headers(return_json)
#                     print("reps_headers:", reps_headers)
#                     self.logger_run_single.info("reps_headers", reps_headers)
#
#                     reps_cookies = show_return_cookies(return_json)
#                     print("reps_cookies:", reps_cookies)
#                     self.logger_run_single.info("reps_cookies", **reps_cookies)
#
#                     reps_data = show_return_data(return_json)
#                     print("reps_data:", reps_data)
#                     self.logger_run_single.info("请求返回值:" + '\n' + str(reps_data))
#
#                     try:
#                         run_status = checkResult(httpcode_check, include_check, no_include_check, res_httpcode, str(reps_headers),str(reps_cookies), str(reps_data), *json_check)
#                     except Exception as err:
#                         self.logger_run_single.info("调用检查结果失败！")
#                         run_status = '0'
#                 else:
#                     self.logger_run_single.info("Time out！")
#                     run_status = '0'
#
#                     # 获取后置操作
#                 if all_apicase.after_operation:
#                     all_after_operation = eval(all_apicase.after_operation)
#                     print("调用后置操作")
#                     self.logger_run_single.info("调用后置操作:", *all_after_operation)
#
#                     try:
#                         (after_dict, after_opt_log) = run_opt(self, *all_after_operation)
#                     except Exception as err:
#                         print("调用后置操作失败")
#                         self.logger_run_single.error("调调用后置操作失败!")
#                     self.logger_run_single.info("\n" + after_opt_log + "\n")
#
#                     # 获取执行后操作
#                 if all_apicase.run_after_operation:
#                     all_run_after_operation = eval(all_apicase.run_after_operation)
#                     print("调用运行后操作")
#                     self.logger_run_single.info("调用运行后操作:", *all_run_after_operation)
#                     try:
#                         (after_dict, run_after_opt_log) = run_opt(self, *all_run_after_operation)
#                     except Exception as err:
#                         print("调用运行后操作失败")
#                         self.logger_run_single.error("调用运行后操作失败!")
#                     self.logger_run_single.info("\n" + run_after_opt_log + "\n")
#
#                     # 初始化CI执行记录
#                 self.logger_run_single.info("--------执行用例：" + case_id + "_" + api_name + " END--------")
#                 self.log_run_single.remove_handler()
#                 run_api_info = RunApiResultInfo()
#                 run_api_info.api_name = api_name
#                 run_api_info.type = '1'
#                 run_api_info.belong_project_id = pid
#                 run_api_info.related_case = related_case
#                 run_api_info.belong_env = belong_env
#                 run_api_info.belong_service = belong_service
#                 run_api_info.detail = self.log_run_single.get_logContent()
#                 run_api_info.status = run_status
#                 run_api_info.start_time = start_time
#                 run_api_info.end_time = end_time
#                 run_api_info.save()
#
#
#                 return JsonResponse({"msg": "ok!", "code": 200})
#
#         else:
#             return JsonResponse({"msg": "项目ID不能为空，请选择项目！", "code": 500})


# 运行搜索或全部CI出来用例,备份
# class RunAllCaseView(View):
#     def post(self, request):
#         pid = request.COOKIES["p_id"]
#         search_key = request.POST.get("search_key", "")
#         select_env = request.POST.get("select_env", "")
#         select_service = request.POST.get("select_service", "")
#         if pid != '':
#             # 定义初始化全局参数和前置操作参数
#             init_gp_log = ''
#             pre_opt_log = ''
#             # 初始化全局参数
#             print("<-------------初始化全局参数 开始------------->")
#             try:
#                 init_gp_log = Init_GlobalParameter(self, pid)
#             except Exception as err:
#                 print("初始化全局参数失败！")
#             print("<-------------初始化全局参数 结束------------->")
#             all_apicase = ApiCaseInfo.objects.filter(Q(belong_project_id=pid) & Q(type='1')).order_by("-add_time")
#             # 按照关键字搜索
#             if search_key:
#                 all_apicase = all_apicase.filter(Q(api_name__icontains=search_key) | Q(api_method__icontains=search_key))
#             # 按照环境搜索
#             if select_env:
#                 all_apicase = all_apicase.filter(belong_env_id=select_env).order_by("-add_time")
#             # 按照服务搜索
#             if select_service:
#                 all_apicase = all_apicase.filter(belong_service=int(select_service)).order_by("-add_time")
#             # 定义运行批次号run_batch
#             run_batch = str(datetime.now().strftime("%Y%m%d%H%M%S"))
#             start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             for each_case in all_apicase:
#                 api_name = each_case.api_name
#                 case_id = each_case.id
#                 belong_env = each_case.belong_env.id
#                 belong_service = each_case.belong_service.id
#                 api_request = json.loads(each_case.api_request)
#                 # 初始化 ApiCaseInfo，belong_env
#                 related_case = ApiCaseInfo.objects.get(id=int(case_id))
#                 belong_env = EnvInfo.objects.get(id=int(belong_env))
#                 belong_service = ServiceInfo.objects.get(id=int(belong_service))
#                 # 初始化前后置操作
#                 pre_operation = []
#                 after_operation = []
#                 run_after_operation = []
#                 res_dict = {}
#                 # 第1步：获取请求URl
#                 if api_request["url"]["host"] and api_request["url"]["method_type"]:
#                     send_host = api_request["url"]["host"]
#                     method_type = api_request["url"]["method_type"]
#                     send_host = GlobalParameterInfo.objects.get(id=int(send_host)).value
#                     send_url = send_host + api_request["url"]["api_path"]
#                     print("send_url:", send_url)
#                 else:
#                     # return JsonResponse({"msg": "send_host不合法!", "code": 500})
#                     # 初始化CI执行记录
#                     run_api_info = RunApiResultInfo()
#                     run_api_info.type = '2'
#                     run_api_info.belong_project_id = pid
#                     run_api_info.related_case = related_case
#                     run_api_info.belong_env = belong_env
#                     run_api_info.belong_service = belong_service
#                     run_api_info.api_name = api_name
#                     run_api_info.detail = "send_url不合法!"
#                     run_api_info.run_batch = run_batch
#                     run_api_info.status = '0'
#                     run_api_info.save()
#                     print("----------send_url不合法!----------------")
#                     continue
#                 # 第2步：获取预置操作id，并且执行预制操作
#                 if each_case.pre_operation:
#                     all_pre_operation = eval(each_case.pre_operation)
#                     # 调用前置操作
#                     print("<-------------调用前置操作------------->", all_pre_operation)
#                     try:
#                         (res_dict, pre_opt_log) = run_opt(self, *all_pre_operation)
#                     except Exception as err:
#                         print("调用前置操作失败！")
#                     print("前置操作返回参数res_dict值:", res_dict)
#
#                 # 第3步：获取数据池,类型是个list,并且替换其中的取前置操作的值和全局操作的值
#                 if api_request["ds"]:
#                     ds = api_request["ds"]
#                     print("<-------------获取数据池------------->\n", ds)
#                     for ds_line in ds:
#                         if 'checkbox' in ds_line:
#                             ds_line.pop('checkbox')
#                         if 'ID' in ds_line:
#                             ds_line.pop('ID')
#                         for dl_key, dl_value in ds_line.items():
#                             # dl_value 需要转换成str，否则如果dl_value是int的时候就会报错
#                             if str(dl_value).startswith('${pre.') and str(dl_value).endswith('}'):
#                                 if res_dict:
#                                     ds_line[dl_key] = res_dict[dl_value[6:-1]]
#                                 else:
#                                     ds_line[dl_key] = ''
#                             elif str(dl_value).startswith('${') and str(dl_value).endswith('}'):
#                                 if GlobalParameterInfo.objects.get(name=dl_value[2:-1]).value:
#                                     dl_value = GlobalParameterInfo.objects.get(name=dl_value[2:-1]).value
#                                 else:
#                                     dl_value = ''
#                                 ds_line[dl_key] = dl_value
#                             else:
#                                 continue
#                     print("<-------------更新后的获取数据池------------->\n",ds)
#
#                     for ds_row in ds:
#                         # 初始化日志
#                         log_name = 'case_id_' + str(case_id) + random_str(6) + '_output.log'
#                         log_batch = 'RunAllCaseView'
#                         self.log_run_all = Log.get_log(log_name, log_batch, 'run_all_case')
#                         self.logger_run_all = self.log_run_all.get_logger()
#                         self.logger_run_all.info("调用初始化全局参数\n" + init_gp_log + "\n")
#                         self.logger_run_all.info("调用前置操作\n" + pre_opt_log + "\n")
#                         self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " START--------")
#                         self.logger_run_all.info("send_url:" + send_url)
#                         self.logger_run_all.info("method_type:" + method_type)
#                         headers ={}
#                         Cookies = {}
#                         requests = {}
#                         httpcode_check = '200'
#                         include_check = ''
#                         no_include_check = ''
#                         json_check = []
#                         print("api_name:", api_name, ds.index(ds_row))
#                         # 获取接口请求head
#                         if api_request["head"]:
#                             headers = config_disc(str(api_request["head"]), str(res_dict), str(ds_row))
#                             print("headers:", headers)
#                             self.logger_run_all.info("headers：" + str(headers))
#
#                         # 获取接口请求cookies
#                         if api_request["Cookies"]:
#                             Cookies = config_disc(str(api_request["Cookies"]), str(res_dict), str(ds_row))
#                             print("Cookies:", Cookies)
#                             self.logger_run_all.info("Cookies：" + str(Cookies))
#
#                         # 获取接口request
#                         if api_request["request"]:
#                             # print(api_request["request"])
#                             requests = config_disc(str(api_request["request"]), str(res_dict), str(ds_row))
#                             print("requests:", requests)
#                             self.logger_run_all.info("requests：" + str(requests))
#                         else:
#                             print("请求body不合法！")
#                             self.logger_run_all.info("请求body不合法！")
#                             self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
#                             # 初始化CI执行记录
#                             run_api_info = RunApiResultInfo()
#                             run_api_info.type = '2'
#                             run_api_info.belong_project_id = pid
#                             run_api_info.related_case = related_case
#                             run_api_info.belong_env = belong_env
#                             run_api_info.belong_service = belong_service
#                             run_api_info.api_name = api_name + str(ds.index(ds_row))
#                             run_api_info.detail = self.log_run_all.get_logContent()
#                             run_api_info.run_batch = run_batch
#                             run_api_info.status = '0'
#                             run_api_info.save()
#                             self.log_run_all.remove_handler()
#                             continue
#
#                         if api_request["check"]:
#                             if api_request["check"]["httpcode_check"]:
#                                 # print(api_request["request"])
#                                 try:
#                                     httpcode_check = config_check(str(api_request["check"]["httpcode_check"]),str(res_dict), str(ds_row))
#                                     print("httpcode_check:", httpcode_check)
#                                     self.logger_run_all.info("httpcode_check:" + httpcode_check)
#                                     # 获取的类型是str
#                                 except Exception as err:
#                                     print("<-------------初始化json_check失败！------------->\n")
#                                     self.logger_run_all.error("-------------初始化json_check失败！-------------")
#
#                             if api_request["check"]["include_check"]:
#                                 # print(api_request["request"])
#                                 try:
#                                     include_check = config_check(str(api_request["check"]["include_check"]),str(res_dict),'{}')
#                                     print("include_check:", include_check)
#                                     self.logger_run_all.info("include_check:" + str(include_check))
#                                 except Exception as err:
#                                     print("<-------------初始化include_check失败！------------->\n")
#                                     self.logger_run_all.error("-------------初始化include_check失败！-------------")
#
#                             if api_request["check"]["no_include_check"]:
#                                 try:
#                                     no_include_check = config_check(str(api_request["check"]["no_include_check"]),str(res_dict), str(ds_row))
#                                     print("no_include_check:", no_include_check)
#                                     self.logger_run_all.info("no_include_check:" + str(no_include_check))
#                                 except Exception as err:
#                                     print("<-------------初始化no_include_check败！------------->\n")
#                                     self.logger_run_all.error("-------------初始化no_include_check失败！-------------")
#
#                             if api_request["check"]["json_check"]:
#                                 # json_check 类型是list
#                                 try:
#                                     json_check = config_check_json(str(api_request["check"]["json_check"]),str(res_dict),str(ds_row))
#                                     print("json_check:", json_check)
#                                     self.logger_run_all.info("json_check:" + json_check.__str__())
#                                 except Exception as err:
#                                     print("<-------------初始化json_check:败！------------->\n")
#                                     self.logger_run_all.info("-------------初始化json_check:失败！-------------")
#
#                         try:
#                             return_json = send_request(api_name, method_type, send_url, str(headers), str(Cookies), str(requests))
#                         except Exception as err:
#                             print("<-------------请求不合法------------->")
#                             self.logger_run_all.error("Time out！")
#                             self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
#                             # 初始化CI执行记录
#                             run_api_info = RunApiResultInfo()
#                             run_api_info.type = '2'
#                             run_api_info.belong_project_id = pid
#                             run_api_info.related_case = related_case
#                             run_api_info.belong_env = belong_env
#                             run_api_info.belong_service = belong_service
#                             run_api_info.api_name = api_name + str(ds.index(ds_row))
#                             run_api_info.detail = self.log_run_all.get_logContent()
#                             run_api_info.status = '0'
#                             run_api_info.run_batch = run_batch
#                             run_api_info.save()
#                             self.log_run_all.remove_handler()
#                             continue
#
#                         # 判断请求是否有返回
#                         if return_json:
#                             res_httpcode = return_json.status_code
#                             print("res_httpcode:", res_httpcode)
#                             self.logger_run_all.info("res_httpcode:" + str(res_httpcode))
#
#                             reps_headers = show_return_headers(return_json)
#                             print("reps_headers:", reps_headers)
#                             self.logger_run_all.info("reps_headers:", reps_headers)
#
#                             reps_cookies = show_return_cookies(return_json)
#                             print("reps_cookies:", reps_cookies)
#                             self.logger_run_all.info("reps_cookies:", **reps_cookies)
#
#                             reps_data = show_return_data(return_json)
#                             print("reps_data:", reps_data)
#                             self.logger_run_all.info("请求返回值:" + '\n' + str(reps_data))
#
#                             try:
#                                 run_status = checkResult(httpcode_check, include_check, no_include_check, res_httpcode,str(reps_headers),str(reps_cookies), str(reps_data), *json_check)
#                             except Exception as err:
#                                 run_status = '0'
#                                 self.logger_run_all.error("调用checkResult方法异常！")
#
#                             # 获取后置操作
#                             if each_case.after_operation:
#                                 all_after_operation = eval(each_case.after_operation)
#                                 print("调用后置操作")
#                                 self.logger_run_all.info("调用后置操作开始！")
#                                 try:
#                                     (after_dict, after_opt_log) = run_opt(self, *all_after_operation)
#                                     self.logger_run_all.info("调用后置操作开始！\n" + after_opt_log + '\n')
#                                 except Exception as err:
#                                     print("调用后置操作失败")
#                                     self.logger_run_all.error("调用后置操作失败!")
#
#                             # 获取执行后操作
#                             if each_case.run_after_operation:
#                                 print(type(each_case.run_after_operation))
#                                 all_run_after_operation = eval(each_case.run_after_operation)
#                                 print(all_run_after_operation)
#                                 print("调用运行后操作")
#                                 self.logger_run_all.info("调用运行后操作开始！")
#                                 try:
#                                     (run_after_dict, run_after_opt_log) = run_opt(self, *all_run_after_operation)
#                                     self.logger_run_all.info("调用运行后操作结束！\n" + run_after_opt_log + '\n')
#                                 except Exception as err:
#                                     print("调用运行后操作失败")
#                                     self.logger_run_all.error("调用运行后的操作失败！")
#
#                         else:
#                             run_status = '0'
#                             self.logger_run_all.error("Time out！")
#
#                         self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
#                         self.log_run_all.remove_handler()
#                         # 初始化CI执行记录
#                         run_api_info = RunApiResultInfo()
#                         run_api_info.type = '2'
#                         run_api_info.belong_project_id = pid
#                         run_api_info.related_case = related_case
#                         run_api_info.belong_env = belong_env
#                         run_api_info.belong_service = belong_service
#                         run_api_info.api_name = api_name + str(ds.index(ds_row))
#                         run_api_info.detail = self.log_run_all.get_logContent()
#                         run_api_info.run_batch = run_batch
#                         run_api_info.status = run_status
#                         run_api_info.save()
#
#                     # return JsonResponse({"msg": "ok!", "code": 200})
#                 else:
#                     # 初始化日志
#                     log_name = 'case_id_' + str(case_id) + random_str(6) + '_output.log'
#                     log_batch = 'RunAllCaseView'
#                     self.log_run_all = Log.get_log(log_name, log_batch, 'run_all_case')
#                     self.logger_run_all = self.log_run_all.get_logger()
#                     self.logger_run_all.info("调用初始化全局参数\n" + init_gp_log + "\n")
#                     self.logger_run_all.info("调用前置操作\n" + pre_opt_log + "\n")
#                     self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " START--------")
#                     self.logger_run_all.info("send_url:" + send_url)
#                     self.logger_run_all.info("method_type:" + method_type)
#                     headers = {}
#                     Cookies = {}
#                     requests = {}
#                     httpcode_check = '200'
#                     include_check = ''
#                     no_include_check = ''
#                     json_check = []
#                     if api_request["head"]:
#                         headers = config_disc(str(api_request["head"]), str(res_dict), '{}')
#                         print("headers:", headers)
#                         self.logger_run_all.info("headers：" + str(headers))
#
#                     if api_request["Cookies"]:
#                         Cookies = config_disc(str(api_request["Cookies"]), str(res_dict), '{}')
#                         print("Cookies:", Cookies)
#                         self.logger_run_all.info("Cookies：" + str(Cookies))
#
#                     if api_request["request"]:
#                             requests = config_disc(str(api_request["request"]), str(res_dict), '{}')
#                             print("requests:", requests)
#                             self.logger_run_all.info("requests：" + str(requests))
#
#                             # 获取校验
#                     if api_request["check"]:
#                         if api_request["check"]["httpcode_check"]:
#                             # print(api_request["request"])
#                             try:
#                                 httpcode_check = config_check(str(api_request["check"]["httpcode_check"]),str(res_dict), '{}')
#                                 # 获取的类型是str
#                                 print("httpcode_check:", httpcode_check)
#                                 self.logger_run_all.info("httpcode_check:" + httpcode_check)
#                             except Exception as err:
#                                 print("初始化httpcode_check失败")
#                                 self.logger_run_all.error("初始化httpcode_check失败！" )
#
#                         if api_request["check"]["include_check"]:
#                             try:
#                                 include_check = config_check(str(api_request["check"]["include_check"]), str(res_dict),'{}')
#                                 print("include_check:", include_check)
#                                 self.logger_run_all.info("include_check:" + str(include_check))
#                             except Exception as err:
#                                 print("初始化include_check失败!")
#                                 self.logger_run_all.error("初始化include_check失败！" )
#
#                         if api_request["check"]["no_include_check"]:
#                             # print(api_request["request"])
#                             try:
#                                 no_include_check = config_check(str(api_request["check"]["no_include_check"]),str(res_dict), '{}')
#                                 print("no_include_check:", no_include_check)
#                                 self.logger_run_all.info("no_include_check:" + str(no_include_check))
#                             except Exception as err:
#                                 print("初始no_include_check失败!")
#                                 self.logger_run_all.error("初始化no_include_check失败！" )
#
#
#                         if api_request["check"]["json_check"]:
#                             # json_check 类型是list
#                             try:
#                                 json_check = config_check_json(str(api_request["check"]["json_check"]), str(res_dict),'{}')
#                                 print("json_check:",json_check)
#                                 self.logger_run_all.info("json_check:" + json_check.__str__())
#                             except Exception as err:
#                                 print("初始化json_check失败!")
#                                 self.logger_run_all.error("初始化json_check失败！" )
#
#                     try:
#                         return_json = send_request(api_name, method_type, send_url, str(headers), str(Cookies), str(requests))
#                     except TimeoutError as err:
#                         print("------Time out!------")
#                         self.logger_run_all.error("------Time out!------")
#                         self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
#                         self.log_run_all.removeHandler()
#                         # 初始化CI执行记录
#                         run_api_info = RunApiResultInfo()
#                         run_api_info.type = '2'
#                         run_api_info.belong_project_id = pid
#                         run_api_info.related_case = related_case
#                         run_api_info.belong_env = belong_env
#                         run_api_info.belong_service = belong_service
#                         run_api_info.api_name = api_name
#                         run_api_info.detail = self.log_run_all.get_logContent()
#                         run_api_info.run_batch = run_batch
#                         run_api_info.status = '0'
#                         run_api_info.save()
#                         continue
#                     # 判断 请求是否有返回
#                     if return_json:
#                         res_httpcode = return_json.status_code
#                         print("res_httpcode:", res_httpcode)
#                         self.logger_run_all.info("res_httpcode:"+ str(res_httpcode))
#
#                         reps_headers = show_return_headers(return_json)
#                         print("reps_headers:", reps_headers)
#                         self.logger_run_all.info("reps_headers:", reps_headers)
#
#                         reps_cookies = show_return_cookies(return_json)
#                         print("reps_cookies:", reps_cookies)
#                         self.logger_run_all.info("reps_cookies:", **reps_cookies)
#
#                         reps_data = show_return_data(return_json)
#                         print("reps_data:", reps_data)
#                         self.logger_run_all.info("请求返回值:" + '\n' + str(reps_data))
#
#                         try:
#                             run_status = checkResult(httpcode_check, include_check, no_include_check, res_httpcode,str(reps_headers),str(reps_cookies), str(reps_data), *json_check)
#                         except Exception as err:
#                             print("调用检查点函数checkResult失败！")
#                             run_status = 0
#                             self.logger_run_all.error("调用检查点函数checkResult失败！")
#
#                         # 获取后置操作
#                         if each_case.after_operation:
#                             all_after_operation = eval(each_case.after_operation)
#                             print("调用后置操作")
#                             self.logger_run_all.info("调用后置操作开始！", *all_after_operation)
#                             try:
#                                 (after_dict, after_opt_log) = run_opt(self, *all_after_operation)
#                                 self.logger_run_all.info("调用后置操作开始！\n" + after_opt_log + '\n')
#                             except Exception as err:
#                                 print("调用后置操作失败")
#                                 self.logger_run_all.error("调用后置操作失败!")
#
#                         # 获取执行后操作
#                         if each_case.run_after_operation:
#                             all_run_after_operation = eval(each_case.run_after_operation)
#                             print("调用运行后操作")
#                             self.logger_run_all.info("调用运行后操作开始！")
#                             try:
#                                 (run_after_dict, run_after_opt_log) = run_opt(self, *all_run_after_operation)
#                                 self.logger_run_all.info("调用后置操作开始！\n" + run_after_opt_log + '\n')
#                             except Exception as err:
#                                 print("调用运行后操作失败")
#                                 self.logger_run_all.error("调用运行后的操作失败！")
#                         self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
#                         self.log_run_all.remove_handler()
#
#                     else:
#                         run_status = 0
#                         self.logger_run_all.error("Time out!")
#                         self.logger_run_all.info("--------执行用例：" + str(case_id) + "_" + api_name + " END--------")
#                         self.log_run_all.remove_handler()
#
#                     # 初始化CI执行记录
#                     run_api_info = RunApiResultInfo()
#                     run_api_info.type = '2'
#                     run_api_info.belong_project_id = pid
#                     run_api_info.related_case = related_case
#                     run_api_info.belong_env = belong_env
#                     run_api_info.belong_service = belong_service
#                     run_api_info.api_name = api_name
#                     run_api_info.detail = self.log_run_all.get_logContent()
#                     run_api_info.run_batch = run_batch
#                     run_api_info.status = run_status
#                     run_api_info.save()
#             # 写入CI 执行计划表
#             case_num = RunApiResultInfo.objects.filter(run_batch=run_batch).count()
#             success_num = RunApiResultInfo.objects.filter(Q(run_batch=run_batch) & Q(status='1')).count()
#             fail_num = case_num - success_num
#             if case_num:
#                 success_ratio = round(success_num/case_num, 4)*100
#             else:
#                 success_ratio = 0
#             end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             run_plan_info = RunApiPlanInfo()
#             run_plan_info.name = '触发CI-执行搜索用例' + str(start_time) + '_By_' + request.user.username
#             run_plan_info.run_batch = run_batch
#             run_plan_info.case_num = case_num
#             run_plan_info.success_num = success_num
#             run_plan_info.fail_num = fail_num
#             run_plan_info.success_ratio = success_ratio
#             run_plan_info.belong_project_id = pid
#             run_plan_info.run_user = request.user.username
#             run_plan_info.start_time = start_time
#             run_plan_info.end_time = end_time
#             run_plan_info.save()
#
#             return JsonResponse({"msg": "CI执行完成！", "code": 200})
#         else:
#             return JsonResponse({"msg": "项目ID不能为空，请选择项目！", "code": 500})

# 运行单个用例--异步任务
class RunSingleCaseView(View):
    def post(self, request):
        pid = request.COOKIES["p_id"]
        case_id = request.POST.get("case_id", "")
        # select_ds 是个list
        select_ds = json.loads(request.POST.get("select_ds", ""))
        all_apicase = ApiCaseInfo.objects.get(id=int(case_id))
        api_request = json.loads(all_apicase.api_request)
        # 第1步：获取请求URl
        if api_request["url"]["host"] and api_request["url"]["method_type"]:
            try:
                # 调用异步任务
                run_single_case.delay(pid, case_id, *select_ds)
                return JsonResponse({"msg": "正在执行，请查阅调试报告！！", "code": 200})
            except:
                return JsonResponse({"msg": "项目ID不能为空，请选择项目！", "code": 500})
        else:
            print("请求URL或者参数不合法！",)
            return JsonResponse({"msg": "请求URL或者参数不合法!", "code": 500})

# 运行搜索或全部CI出来用例--异步任务
class RunAllCaseView(View):
    def post(self, request):
        pid = request.COOKIES["p_id"]
        search_key = request.POST.get("search_key", "")
        select_env = request.POST.get("select_env", "")
        select_service = request.POST.get("select_service", "")
        username = request.user.username
        try:
            run_search_case.delay(pid, search_key, select_env, select_service, username)
            return JsonResponse({"msg": "正在执行，稍后请查阅CI执行报告！", "code": 200})
        except:
            return JsonResponse({"msg": "调用异步任务失败！！", "code": 200})

# 查看CI执行计划列表
class RunApiPlanInfoView(View):
    def get(self, request):
        pid = request.COOKIES["p_id"]
        if pid != '':
            all_plan = RunApiPlanInfo.objects.filter(belong_project_id=pid).order_by("-start_time")
            page_num = request.GET.get('page_num', '')
            pa = Paginator(all_plan, 10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'api/RunApiPlanList.html', {
                "pages": pages,
                "code": 200,
                "msg": "ok",
            })
        else:
            return render(request, 'api/RunApiPlanList.html', {
                "code": 500,
                "msg": "项目ID不能为空！",
            })

# 查看CI执行计划列表
class DelRunApiPlanView(View):
    def post(self, request):
        if request.POST.get("plan_id", "") != '':
            plan_id = eval(request.POST.get("plan_id", ""))
            # print("4444444444444444444:",plan_id)
            for pid in plan_id:
                all_plan = RunApiPlanInfo.objects.get(id=int(pid))
                run_batch = all_plan.run_batch
                all_detail = RunApiResultInfo.objects.filter(run_batch=run_batch)
                all_detail.delete()
                all_plan.delete()

                # print(all_service.status)
            return JsonResponse({"msg": "删除成功","code": 200})
        else:
            return JsonResponse({"msg": "删除失败，id不存在！", "code": 500})

# 查看用例执行记录列表
class RunApiResultListView(View):
    def get(self, request):
        # run_type = (("1", "单个"), ("2", "批量"))
        run_type = request.GET.get("run_type", "")
        case_id = request.GET.get("case_id", "")
        run_batch = request.GET.get("run_batch", "")
        if case_id != '' and run_type == '1' and run_batch == '':
            all_runresult = RunApiResultInfo.objects.filter(Q(related_case=int(case_id)) & Q(type='1')).order_by("status")
            success_runresult = RunApiResultInfo.objects.filter(Q(related_case=int(case_id)) & Q(type='1')& Q(status='1')).order_by("start_time")
            fail_runresult = RunApiResultInfo.objects.filter(Q(related_case=int(case_id)) & Q(type='1') & Q(status='0')).order_by("start_time")
            if all_runresult:
                success_ratio = round(success_runresult.count()/all_runresult.count(), 4)*100
            else:
                success_ratio = 0

            page_num = request.GET.get('page_num', '')
            pa = Paginator(all_runresult, 15)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'api/RunSingleCaseList.html', {
                "all_runresult": all_runresult,
                "success_runresult": success_runresult,
                "fail_runresult": fail_runresult,
                "success_ratio": success_ratio,
                "pages": pages,
                "code": 200,
                "case_id": case_id,
                "run_type": run_type,
                "run_batch": run_batch

            })

        elif run_type == '2' and run_batch != '':
            all_runresult = RunApiResultInfo.objects.filter(Q(type='2') & Q(run_batch=run_batch)).order_by("start_time")
            success_runresult = RunApiResultInfo.objects.filter(Q(type='2') & Q(run_batch=run_batch)  & Q(status='1')).order_by("start_time")
            fail_runresult = RunApiResultInfo.objects.filter(Q(type='2') & Q(run_batch=run_batch)  & Q(status='0')).order_by("start_time")
            if all_runresult:
                success_ratio = round(success_runresult.count()/all_runresult.count(), 4)*100
            else:
                success_ratio = 0
            page_num = request.GET.get('page_num', '')
            pa = Paginator(all_runresult, 15)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'api/RunSingleCaseList.html', {
                "all_runresult": all_runresult,
                "success_runresult": success_runresult,
                "fail_runresult": fail_runresult,
                "success_ratio": success_ratio,
                "pages": pages,
                "code": 200,
                "case_id": case_id,
                "run_type": run_type,
                "run_batch": run_batch
            })

        else:
            return render(request, 'api/RunSingleCaseList.html', {
                "msg": "用例ID，用例类型或者运行批次号不正确！",
                "code": 500,
        })

# 查看用例执行记录详情
class SingleResultDetailView(View):
    def post(self, request):
        # run_type = (("1", "单个"), ("2", "批量"))
        Result_id = request.POST.get("Result_id", "")
        if Result_id != '':
            SingleResultDetail = RunApiResultInfo.objects.filter(id=int(Result_id)).order_by("start_time")
            return render(request, 'api/SingleCaseDetail.html', {
                "SingleResultDetail": SingleResultDetail,
                "code": 200,
                "msg": "ok",
            })
        else:
            return render(request, 'api/SingleCaseDetail.html', {
                "msg": "Result_id 不正确",
                "code": 500,
        })







        

