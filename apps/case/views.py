from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import render_to_response
from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.views.generic.base import View
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from manager.models import ProjectInfo,VersionInfo,ServiceInfo
from case.models import TestCase,VersionCase,TestCaseSuit,TestCaseSuitDetail,XMindCase
from case.forms import AddXMindCaseForm,ModifyXMindCaseForm,XMindCaseDetailForm
from requirement.models import RequirementInfo
from users.models import UserProfile
from mptt.models import MPTTModel
from django.db.models import Q
from django.urls import reverse
from  django.http import JsonResponse
import operator
from functools import reduce
import json
# 产品用例目录和列表
class CaseListView(View):
    def get(self,request):
        # 获取树节点，返回ztree简单树结构
        Nodes = []
        if request.COOKIES["p_id"]:
            belong_project_id = request.COOKIES["p_id"]
            caselist = TestCase.objects.filter(Q(type='ml') & Q(status='1') & Q(belong_project=int(belong_project_id)))
            Nodes = [
                {
                    'id': x.id,
                    'name': x.name,
                    'pId': x.parent_id if x.parent_id else 0, 'open': 0,
                } for x in caselist
            ]
            # caselist = TestCase.objects.filter(Q(type='ml') & Q(status='1') & Q(belong_project=int(belong_project_id))).values('id', 'name','parent_area_id')

            # print(Nodes)
            return render(request, 'case/case_list.html', {'Nodes_product': Nodes})
        else:
            return render(request, 'case/case_list.html',{'msg':"项目id不存在",'Nodes_product': Nodes})

    def post(self,request):
        belong_project_id = request.COOKIES["p_id"]
        # 获取前台树节点id，有了id_list，其实pId已经没有作用了，暂时保留
        pId = request.POST.get("pId", "")
        # strip去除前后[ ]，并且把"替换为空，因为case_list.html和table_list.html 传的id_list 不一样
        id_list = request.POST.get("id_list", "").strip('[ ]').replace('"', '')
        # print("id_list:", id_list)
        # 切割字符串id_list，并且转换成list，id_list即：所选节点的子节点和当前节点的集合
        id_list = id_list.split(',')

        if id_list:
            # 根据节点id，获取节点id下的用例
            all_testcase = TestCase.objects.filter(Q(type='yl') & Q(status='1') & Q(parent_id__in=id_list) & Q(belong_project=int(belong_project_id))).order_by('-id')
            # print("all_testcase:", all_testcase)
            pa = Paginator(all_testcase, 10)
            page_num = int(request.POST.get('page_num'))
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            # print(pages)
            return render(request, 'case/table_list.html', {"pages": pages, "pId": pId, "id_list": id_list})

        else:
            return JsonResponse({"msg": "节点ID不存在", "code": 500})

# 产品用例目录和用例新增
class AddCaseView(View):
    def post(self,request):
        project_id = int(request.COOKIES["p_id"])
        # 操作外键的的时候，必须要先实例化外键对应的mode
        if project_id != '':
            belong_project_id = ProjectInfo.objects.get(id=int(project_id))
            case_info = TestCase()
            name = request.POST.get("name", "")
            parent_area = int(request.POST.get("pId", ""))
            type = request.POST.get("type","")
            designer = request.user.username

            if type == 'ml'and parent_area > 0:
                # print(parent_area,type,name)
                case_info.name = name
                case_info.type = type
                case_info.belong_project = belong_project_id
                case_info.parent_id = parent_area
                case_info.designer = designer
                case_info.save()
                id = case_info.id
                # print(case_info.id,case_info.name,case_info.parent_area_id)
                return JsonResponse({"msg": "新增节点成功","code": 200,'id': id})
            elif type == 'ml'and parent_area == 0:
                case_info.name = name
                case_info.type = type
                case_info.belong_project = belong_project_id
                case_info.designer = designer
                case_info.save()
                id = case_info.id
                # print(case_info.id,case_info.name,case_info.parent_area_id)
                return JsonResponse({"msg": "新增根节点成功", "code": 200, 'id': id})
            elif type == 'yl':
                jb = request.POST.get("jb", "")
                precondition = request.POST.get("precondition", "")
                operation = request.POST.get("operation", "")
                expect_result = request.POST.get("expect_result", "")
                case_desc = request.POST.get("case_desc", "")
                case_info.belong_project = belong_project_id
                case_info.name = name
                case_info.parent_id = parent_area
                case_info.type = type
                case_info.jb = jb
                case_info.precondition = precondition
                case_info.operation = operation
                case_info.expect_result = expect_result
                case_info.case_desc = case_desc
                case_info.designer = designer
                case_info.save()
                return JsonResponse({"msg": "新增用例成功", "code": 200})
        else:
            return JsonResponse({"msg": "p_id不能为空", "code": 500})

# 产品用例目录和用例修改
class ModifyCaseView(View):
    def get(self,request):
        case_id = int(request.GET.get("id", ""))
        case_name = TestCase.objects.get(id=int(case_id)).name
        case_jb = TestCase.objects.get(id=int(case_id)).jb
        case_precondition = TestCase.objects.get(id=int(case_id)).precondition
        case_operation = TestCase.objects.get(id=int(case_id)).operation
        case_expect_result = TestCase.objects.get(id=int(case_id)).expect_result
        case_desc = TestCase.objects.get(id=int(case_id)).case_desc
        return JsonResponse({
            "case_name":case_name,
            "case_jb":case_jb,
            "case_precondition":case_precondition,
            "case_operation":case_operation,
            "case_expect_result":case_expect_result,
            "case_desc": case_desc,
        })

    def post(self,request):
        case_id = int(request.POST.get("id", ""))
        name = request.POST.get("name", "")
        type = request.POST.get("type","")
        modifier = request.user.username
        case_info = TestCase.objects.get(id=int(case_id))
        if type == 'ml':
            case_info.name = name
            case_info.modifier = modifier
            case_info.save()
            return JsonResponse({"msg": "修改节点成功","code": 200})

        elif type == 'yl':
            jb = request.POST.get("jb", "")
            precondition = request.POST.get("precondition", "")
            operation = request.POST.get("operation", "")
            expect_result = request.POST.get("expect_result", "")
            case_desc = request.POST.get("case_desc", "")
            case_info.name = name
            case_info.jb = jb
            case_info.precondition = precondition
            case_info.operation = operation
            case_info.expect_result = expect_result
            case_info.case_desc = case_desc
            case_info.modifier = modifier
            case_info.save()
            return JsonResponse({"msg": "修改用例成功","code": 200})
        else:
            return JsonResponse({"msg": "修改失败","code": 500})

# 删除产品用例目录和用例project_id:
class DelCaseView(View):
    def post(self,request):
        case_id = int(request.POST.get("id", ""))
        # type = request.POST.get("type","")
        case_info = TestCase.objects.get(id=int(case_id))
        if TestCase.objects.filter(parent_id=int(case_id)):
            return JsonResponse({"msg": "该节点下有子节点，不能删除！", "code": 500})
        else:
            case_info.delete()
            return JsonResponse({"msg": "删除成功！", "code": 200})

# 版本用例目录和列表
class VersionCaseListView(View):
    def get(self,request):
        # 获取树节点，返回ztree简单树结构
        version_id = request.COOKIES["v_id"]
        belong_project_id = request.COOKIES["p_id"]
        # print("version_id：",version_id)
        Nodes = []
        Nodes_product = []
        if version_id.strip() != '' and belong_project_id != '':
            caselist = VersionCase.objects.filter(Q(type='ml') & Q(status='1') & Q(belong_version=int(version_id)))
            Nodes = [
                    {
                        'id': x.id,
                        'name': x.name,
                        'pId': x.parent_id if x.parent_id else 0, 'open': 0,
                    } for x in caselist
            ]
            # print("Nodes:",Nodes)
        # 获取树节点，返回ztree简单树结构

            product_caselist = TestCase.objects.filter(Q(status='1') & Q(belong_project=int(belong_project_id)))
            Nodes_product = [
                {
                    'id': x.id,
                    'name': x.name,
                    'pId': x.parent_id if x.parent_id else 0, 'open': 0,
                } for x in product_caselist
            ]

            return render(request, 'case/version_case_list.html', {"Nodes": Nodes, "Nodes_product": Nodes_product})

        else:
            return render(request, 'case/version_case_list.html', {"Nodes": Nodes, "Nodes_product": Nodes_product})

    def post(self,request):
        belong_version_id = request.COOKIES["v_id"]
        if belong_version_id != '':
           # 获取前台树节点id，有了id_list，其实pId已经没有作用了，暂时保留
            pId = request.POST.get("pId", "")
            # strip去除前后[ ]，并且把"替换为空，因为case_list.html和table_list.html 传的id_list 不一样
            id_list = request.POST.get("id_list", "").strip('[ ]').replace('"', '')
            # print("id_list:", id_list)
            # 切割字符串id_list，并且转换成list，id_list即：所选节点的子节点和当前节点的集合
            id_list = id_list.split(',')
            if id_list:
                # 根据节点id，获取节点id下的用例
                all_testcase = VersionCase.objects.filter(Q(type='yl') & Q(status='1') & Q(parent_id__in=id_list) & Q(belong_version=int(belong_version_id))).order_by('-id')
                # print("all_testcase:", all_testcase)
                pa = Paginator(all_testcase, 10)
                page_num = int(request.POST.get('page_num'))
                try:
                    pages = pa.page(page_num)
                except PageNotAnInteger:
                    pages = pa.page(1)
                except EmptyPage:
                    pages = pa.page(pa.num_pages)
                # print(pages)
                return render(request, 'case/version_table_list.html',{"pages": pages, "pId": pId, "id_list": id_list})
            else:
                return JsonResponse({"msg": "节点ID不存在", "code": 500})
        else:
            return JsonResponse({"msg": "version_id不存在", "code": 500})

# 版本用例目录和用例新增
class AddVersionCaseView(View):
    def post(self,request):
        version_id = int(request.COOKIES["v_id"])
        if version_id != '':
            # 操作外键的的时候，必须要先实例化外键对应的mode
            belong_version_id = VersionInfo.objects.get(id=version_id)
            case_info = VersionCase()
            name = request.POST.get("name", "")
            parent_area = int(request.POST.get("pId", ""))
            type = request.POST.get("type","")
            designer = request.user.username
            if type == 'ml'and parent_area > 0:
                # print(parent_area,type,name)
                case_info.name = name
                case_info.type = type
                case_info.belong_version = belong_version_id
                case_info.parent_id = parent_area
                case_info.designer = designer
                case_info.save()
                id = case_info.id
                # print(case_info.id,case_info.name,case_info.parent_area_id)
                return JsonResponse({"msg": "新增节点成功","code": 200,'id': id})
            elif type == 'ml'and parent_area == 0:
                case_info.name = name
                case_info.type = type
                case_info.belong_version = belong_version_id
                case_info.designer = designer
                case_info.save()
                id = case_info.id
                return JsonResponse({"msg": "新增根节点成功", "code": 200,"id":id})
            elif type == 'yl':
                jb = request.POST.get("jb", "")
                precondition = request.POST.get("precondition", "")
                operation = request.POST.get("operation", "")
                expect_result = request.POST.get("expect_result", "")
                case_desc = request.POST.get("case_desc", "")
                # status = 1
                case_info.belong_version = belong_version_id
                case_info.name = name
                case_info.parent_id = parent_area
                case_info.type = type
                case_info.jb = jb
                case_info.precondition = precondition
                case_info.operation = operation
                case_info.expect_result = expect_result
                case_info.case_desc = case_desc
                case_info.designer = designer
                case_info.save()
                return JsonResponse({"msg": "新增用例成功", "code": 200})
        else:
            return JsonResponse({"msg": "version_id能为空", "code": 500})

# 版本用例目录和用例修改
class ModifyVersionCaseView(View):
    def get(self,request):
        case_id = int(request.GET.get("id", ""))
        case_name = VersionCase.objects.get(id=int(case_id)).name
        case_jb = VersionCase.objects.get(id=int(case_id)).jb
        case_precondition = VersionCase.objects.get(id=int(case_id)).precondition
        case_operation = VersionCase.objects.get(id=int(case_id)).operation
        case_expect_result = VersionCase.objects.get(id=int(case_id)).expect_result
        case_desc = VersionCase.objects.get(id=int(case_id)).case_desc
        # print("case_name:",case_name)
        return JsonResponse({
            "case_name":case_name,
            "case_jb":case_jb,
            "case_precondition":case_precondition,
            "case_operation":case_operation,
            "case_expect_result":case_expect_result,
            "case_desc": case_desc,
        })

    def post(self,request):
        case_id = int(request.POST.get("id", ""))
        name = request.POST.get("name", "")
        type = request.POST.get("type","")
        modifier = request.user.username
        case_info = VersionCase.objects.get(id=int(case_id))
        if type == 'ml':
            case_info.name = name
            case_info.modifier = modifier
            case_info.save()
            return JsonResponse({"msg": "修改节点成功","code": 200})

        elif type == 'yl':
            jb = request.POST.get("jb", "")
            precondition = request.POST.get("precondition", "")
            operation = request.POST.get("operation", "")
            expect_result = request.POST.get("expect_result", "")
            case_desc = request.POST.get("case_desc", "")
            case_info.name = name
            case_info.jb = jb
            case_info.precondition = precondition
            case_info.operation = operation
            case_info.expect_result = expect_result
            case_info.case_desc = case_desc
            case_info.modifier = modifier
            case_info.save()
            return JsonResponse({"msg": "修改用例成功","code": 200})

        else:
            return JsonResponse({"msg": "修改失败","code": 500})

# 版本用例目录和列表
class DelVersionCaseView(View):
    def post(self,request):
        case_id = int(request.POST.get("id", ""))
        # print("case_id:",case_id)
        # type = request.POST.get("type","")
        case_info = VersionCase.objects.get(id=int(case_id))
        # print("name",case_info.name)
        if VersionCase.objects.filter(parent_id=int(case_id)):
            return JsonResponse({"msg": "该节点下有子节点，不能删除！", "code": 500})
        else:
            case_info.delete()
            return JsonResponse({"msg": "删除成功！", "code": 200})

# 引入产品库用例到版本库
class IntoProductCaseView(View):

    def post(self, request):
        # idList产品用例库用例id集合
        idList = eval(request.POST.get("idList",""))
        version_id = int(request.COOKIES["v_id"])
        project_id = int(request.COOKIES["p_id"])
        print(idList)

        if idList and project_id and version_id:
            # 先删除版本用例库中已经存在的产品库用例，再插入数据
            VersionCase.objects.filter(p_case_id__in=idList).delete()
            querysetlist = list()
            for i in idList:
                TestCase_Info = TestCase.objects.get(id=int(i))
                belong_version = VersionInfo.objects.get(id=version_id)
                querysetlist.append(VersionCase(name=TestCase_Info.name,parent_id=TestCase_Info.parent_id,jb=TestCase_Info.jb,precondition=TestCase_Info.precondition, operation=TestCase_Info.operation,expect_result=TestCase_Info.expect_result, case_desc=TestCase_Info.case_desc,designer=TestCase_Info.designer,modifier=TestCase_Info.modifier,type=TestCase_Info.type,p_case_id=TestCase_Info.id,belong_version=belong_version))
            # 批量入库，插入后，parent_area 需要修改
            VersionCase.objects.bulk_create(querysetlist)

            # ToModifyCase带修改parent_area的版本库用例即可，[{'id': 269, 'parent_id': 268}]，其中id对应着p_case_id，parent_id和parent_id对应
            ToModifyCase = list(TestCase.objects.filter(Q(id__in=idList) & Q(parent_id__isnull=False) & Q(belong_project=project_id)).values('id', 'parent_id'))
            # print(ToModifyCase)
            updatelist = []
            for k in ToModifyCase:
                VersionCase_info = VersionCase.objects.get(p_case_id=k['parent_id'])
                VersionCase.objects.filter(p_case_id=k['id'],belong_version_id=version_id,parent_id=k['parent_id']).update(parent_id=VersionCase_info.id)
            return JsonResponse({"msg": "ok", "code": 200})
        else:
            return JsonResponse({"msg": "请选择用例集！", "code": 500})


# 执行集列表
class TestCaseSuitListView(View):
    def get(self,request):
        belong_verison_id = request.COOKIES["v_id"]
        if belong_verison_id != '':
            all_TestCaseSuit = TestCaseSuit.objects.filter(belong_version=int(belong_verison_id)).order_by("-id")
            all_requirement = RequirementInfo.objects.filter(Q(belong_version=int(belong_verison_id)) & ~Q(status='0')).order_by("-id")
            all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")

            page_num = request.GET.get('page_num','')
            pa = Paginator(all_TestCaseSuit,10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'case/TestCaseSuit_list.html', {
                "pages": pages,
                "all_requirement": all_requirement,
                "all_users": all_users,
            })
        else:
            return render(request, 'case/TestCaseSuit_list.html', {
                "msg":"belong_verison_id不能为空",
            })

# 新增执行集
class AddTestCaseSuitView(View):
    def get(self,request):
        belong_verison_id = request.COOKIES["v_id"]
        Nodes = []
        if belong_verison_id != '':
            all_requirement = RequirementInfo.objects.filter(Q(belong_version=int(belong_verison_id)) & ~Q(status='0')).order_by("-id")
            all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")
            if belong_verison_id:
                caselist = VersionCase.objects.filter(Q(status='1') & Q(belong_version=int(belong_verison_id)))
                Nodes = [
                    {
                        'id': x.id,
                        'name': x.name,
                        'pId': x.parent_id if x.parent_id else 0, 'open': 0,
                    } for x in caselist
                ]
                return render(request, 'case/TestCaseSuit_add.html', {
                    "Nodes": Nodes,
                    "all_requirement": all_requirement,
                    "all_users": all_users,
                })
            else:
                return render(request, 'case/TestCaseSuit_add.html', {
                    "Nodes": Nodes,
                    "all_requirement": all_requirement,
                    "all_users": all_users,
                })
        else:
            return render(request, 'case/TestCaseSuit_add.html', {
                "Nodes": Nodes,
            })

    def post(self,request):
        version_id = request.COOKIES["v_id"]
        if version_id != '':
            # 初始化用例执行集
            suit_info = TestCaseSuit()
            # 获取 前台传过来的用例执行集详情和勾选的用例id集合ids
            ids = request.POST.getlist("ids", "")
            # print(type(ids))
            # print(ids)

            ids = map(eval, ids)
            # print(ids)
            name = request.POST.get("name", "")
            requirement_id = request.POST.get("requirement_id", "")
            requirement_name = request.POST.get("requirement_name", "")
            executor = request.POST.get("executor", "")
            start_time = request.POST.get("start_time", "")
            end_time = request.POST.get("end_time", "")
            suit_info.name = name
            suit_info.requirement_id = requirement_id
            suit_info.requirement_name = requirement_name
            #  操作外键的的时候，必须要先实例化外键对应的mode
            version_id = VersionInfo.objects.get(id=int(version_id))
            suit_info.belong_version = version_id
            suit_info.executor = executor
            suit_info.creator = request.user.username
            suit_info.start_time = start_time
            suit_info.end_time = end_time
            suit_info.save()
            suit_id = suit_info.id
            all_case = VersionCase.objects.filter(id__in=ids)
            # print("all_case:",all_case)
            # 初始化用例执行集详情
            suit_id = TestCaseSuit.objects.get(id=int(suit_id))
            # print("suit_id",suit_id)
            querysetlist = list()
            for i in all_case:
                belong_version_case = VersionCase.objects.get(id=int(i.id))
                querysetlist.append(TestCaseSuitDetail(belong_version_case=belong_version_case,belong_suit=suit_id,parent_id=i.parent_id,name=i.name,jb=i.jb,precondition=i.precondition,operation=i.operation,expect_result=i.expect_result,type=i.type,designer=i.designer,modifier=i.modifier))
            TestCaseSuitDetail.objects.bulk_create(querysetlist)
            return JsonResponse({"msg": "新增执行集成功", "code": 200})
        else:
            return JsonResponse({"msg": "请选择版本！", "code": 500})

# 修改执行集
class ModifyTestCaseSuitView(View):
    def get(self,request,suit_id):
        belong_verison_id = request.COOKIES["v_id"]
        all_suit = TestCaseSuit.objects.get(id=int(suit_id))
        Nodes = []
        Select_Nodes = []
        if belong_verison_id != '':
            all_requirement = RequirementInfo.objects.filter(Q(belong_version=int(belong_verison_id)) & ~Q(status='0')).order_by("-id")
            all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")
            caselist = VersionCase.objects.filter(Q(status='1') & Q(belong_version=int(belong_verison_id)))
            Nodes = [
                    {
                        'id': x.id,
                        'name': x.name,
                        'pId': x.parent_id if x.parent_id else 0, 'open': 0,
                    } for x in caselist
                ]
            # 获取已经选中的用例id

            # all_SuitDetail = TestCaseSuitDetail.objects.filter(belong_suit=int(suit_id))
            # for x in all_SuitDetail:
            #     Select_Nodes.append(x.belong_version_case_id)
            # 获取已经选中的用例id
            Select_Nodes = list(TestCaseSuitDetail.objects.values_list('belong_version_case_id',flat=True).filter(belong_suit=int(suit_id)))
            # print("Select_Nodes:",Select_Nodes)
            return render(request, 'case/TestCaseSuit_modify.html', {
                    "Nodes": Nodes,
                    "Select_Nodes": Select_Nodes,
                    "all_requirement": all_requirement,
                    "all_users": all_users,
                    "all_suit": all_suit,
                })

        else:
            return render(request, 'case/TestCaseSuit_modify.html', {
                "Nodes": Nodes,
                "Select_Nodes":Select_Nodes,
            })

    def post(self,request,suit_id):
        version_id = request.COOKIES["v_id"]
        if version_id != '':
            # 初始化用例执行集
            suit_info = TestCaseSuit.objects.get(id=int(suit_id))
            # 获取 前台传过来的用例执行集详情和勾选的用例id集合ids
            ids = request.POST.getlist("ids", "")
            ids = map(eval, ids)
            # suit_id = request.POST.get("suit_id","")
            name = request.POST.get("name", "")
            requirement_id = request.POST.get("requirement_id", "")
            requirement_name = request.POST.get("requirement_name", "")
            executor = request.POST.get("executor", "")
            start_time = request.POST.get("start_time", "")
            end_time = request.POST.get("end_time", "")
            suit_info.name = name
            suit_info.requirement_id = requirement_id
            suit_info.requirement_name = requirement_name
            #  操作外键的的时候，必须要先实例化外键对应的mode
            version_id = VersionInfo.objects.get(id=int(version_id))
            suit_info.belong_version = version_id
            suit_info.executor = executor
            suit_info.creator = request.user.username
            suit_info.start_time = start_time
            suit_info.end_time = end_time
            suit_info.save()
            all_case = VersionCase.objects.filter(id__in=ids)
            # print("all_case:",all_case)
            # 初始化用例执行集详情
            suit = TestCaseSuit.objects.get(id=int(suit_id))
            # 先删除测试执行集详情后，在插入数据
            TestCaseSuitDetail.objects.filter(belong_suit=int(suit_id)).delete()
            # print("suit_id",suit_id)
            querysetlist = list()
            for i in all_case:
                belong_version_case = VersionCase.objects.get(id=int(i.id))
                querysetlist.append(TestCaseSuitDetail(belong_version_case=belong_version_case,belong_suit=suit,parent_id=i.parent_id,name=i.name,jb=i.jb,precondition=i.precondition,operation=i.operation,expect_result=i.expect_result,type=i.type,designer=i.designer,modifier=i.modifier))
            TestCaseSuitDetail.objects.bulk_create(querysetlist)
            return JsonResponse({"msg": "修改执行集成功", "code": 200})
        else:
            return JsonResponse({"msg": "请选择版本！", "code": 500})

# 删除测试执行集
class DelTestCaseSuitListView(View):
    def post(self,request):
        suit_id = request.POST.get("suit_id","")
        print("suit_id:",suit_id)
        if suit_id:
            suit_info = TestCaseSuit.objects.get(id=int(suit_id))
            status = suit_info.status
            if status == 'new' or status == 'stop':
                suitcase_detail = TestCaseSuitDetail.objects.filter(belong_suit=int(suit_id))
                suitcase_detail.delete()
                suit_info.delete()
                return JsonResponse({"msg": "删除执行集成功", "code": 200})
            else:
                return JsonResponse({"msg": "非新建和终止状态的执行集不能删除", "code": 500})
        else:
            return JsonResponse({"msg": "执行集体不存在！", "code": 500})

# 终止测试执行集
class StopTestCaseSuitListView(View):
    def post(self,request):
        suit_id = request.POST.get("suit_id","")
        print("suit_id:",suit_id)
        if suit_id:
            suit_info = TestCaseSuit.objects.get(id=int(suit_id))
            status = suit_info.status
            if status == 'new' or status == 'ongoing':
                suit_info.status = 'stop'
                suit_info.save()
                return JsonResponse({"msg": "终止执行集成功", "code": 200})
            else:
                return JsonResponse({"msg": "非新建和进行中状态的执行集不能终止", "code": 500})
        else:
            return JsonResponse({"msg": "执行集体不存在！", "code": 500})

# 我的执行集列表
class MyTestCaseSuitListView(View):
    def get(self,request):
        belong_verison_id = request.COOKIES["v_id"]
        username = request.user.username
        if belong_verison_id != '':
            all_TestCaseSuit = TestCaseSuit.objects.filter(Q(belong_version=int(belong_verison_id)) & Q(executor=username)).order_by("-id")
            all_requirement = RequirementInfo.objects.filter(Q(belong_version=int(belong_verison_id)) & ~Q(status='0')).order_by("-id")
            all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")

            page_num = request.GET.get('page_num','')
            pa = Paginator(all_TestCaseSuit,10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'case/MyTestCaseSuit_list.html', {
                "pages":pages,
                "all_requirement":all_requirement,
                "all_users":all_users,
            })
        else:
            return render(request, 'case/MyTestCaseSuit_list.html', {
                "msg":"belong_verison_id不能为空",
            })

# 我的执行集详情SuitCaseDetail
class MyTestCaseSuitDetailView(View):
    def get(self, request, suit_id):
        belong_verison_id = request.COOKIES["v_id"]
        all_suit = TestCaseSuit.objects.get(id=int(suit_id))
        Nodes = []
        if belong_verison_id != '':
            # all_requirement = RequirementInfo.objects.filter(
            #     Q(belong_version=int(belong_verison_id)) & Q(status='1')).order_by("-id")
            # all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")
            all_SuitDetail = TestCaseSuitDetail.objects.filter(belong_suit=int(suit_id)).order_by("belong_suit")
            case_jb = request.GET.get("case_jb","")
            if case_jb:
                all_SuitDetail = all_SuitDetail.filter(jb=case_jb)

            case_status = request.GET.get("case_status", "")
            if case_status:
                all_SuitDetail = all_SuitDetail.filter(status=case_status)

            Nodes = [
                {
                    'id': x.belong_version_case_id,
                    'name': x.name,
                    'pId': x.parent_id if x.parent_id else 0, 'open': 0,
                } for x in all_SuitDetail
            ]

            return render(request, 'case/MyTestCaseSuit_detail.html', {
                "Nodes": Nodes,
                "all_suit": all_suit,
                "case_jb": case_jb,
                "case_status": case_status,
            })

        else:
            return render(request, 'case/MyTestCaseSuit_detail.html', {
                "Nodes": Nodes,
            })

# 我的执行集用例详情
class SuitCaseDetailView(View):
    def post(self,request):
        # 获取前台树节点id
        pId = request.POST.get("pId", "")
        suit_id = request.POST.get("suit_id", "")
        # print("pId:", pId)
        if pId and suit_id:
            # 根据节点id，获取节点id下的用例
            SuitCase_info = TestCaseSuitDetail.objects.get(Q(belong_version_case=int(pId)) & Q(belong_suit=int(suit_id)))
            # print("all_testcase",SuitCase_info)
            # print("all_testcase",SuitCase_info.name)
            if SuitCase_info.type == 'yl':
                return render(request, 'case/SuitCase_detail.html',{"SuitCase_info": SuitCase_info,"pId": pId})
            else:
                return JsonResponse({"msg": "您选择的是目录结构", "code": 500})
        else:
            return JsonResponse({"msg": "您选择的是目录结构不存在", "code": 500})

# 更改执行集中的用例状态
class ChangeSuitCaseStatusView(View):
    def post(self,request):
        # 获取前台树节点id,即用例id
        pId = request.POST.get("pId", "")
        suit_id = request.POST.get("suit_id", "")
        case_status = request.POST.get("case_status", "")
        # print("pId:", pId)
        if pId and suit_id and case_status:
            # 根据节点id，获取节点id下的用例
            SuitCase_info = TestCaseSuitDetail.objects.get(Q(belong_version_case=int(pId)) & Q(belong_suit=int(suit_id)))
            # print("all_testcase",SuitCase_info)
            # print("all_testcase",SuitCase_info.name)
            if SuitCase_info.type == 'yl':
                SuitCase_info.status = case_status
                SuitCase_info.save()
                return JsonResponse({"msg": "修改用例状态成功", "code": 200})
            else:
                return JsonResponse({"msg": "您选择的是目录结构", "code": 500})
        else:
            return JsonResponse({"msg": "您选择的是目录结构不存在", "code": 500})

# 修改执行集中的用例
class ChangeSuitCaseDetailView(View):
    def post(self,request):
        # 获取前台树节点id,即用例id
        pId = request.POST.get("pId", "")
        suit_id = request.POST.get("suit_id", "")
        name = request.POST.get("name", "")
        jb = request.POST.get("jb", "")
        precondition = request.POST.get("precondition", "")
        operation = request.POST.get("operation", "")
        expect_result = request.POST.get("expect_result", "")
        desc = request.POST.get("desc", "")
        remind = request.POST.get("remind", "")
        # print("pId:", pId)
        if pId and suit_id:
            # 根据节点id，获取节点id下的用例
            SuitCase_info = TestCaseSuitDetail.objects.get(Q(belong_version_case=int(pId)) & Q(belong_suit=int(suit_id)))
            if SuitCase_info.type == 'yl':
                SuitCase_info.name = name
                SuitCase_info.jb = jb
                SuitCase_info.precondition = precondition
                SuitCase_info.operation = operation
                SuitCase_info.expect_result = expect_result
                SuitCase_info.desc = desc
                SuitCase_info.remind = remind
                SuitCase_info.save()
                return JsonResponse({"msg": "修改用例成功", "code": 200})
            else:
                return JsonResponse({"msg": "您选择的是目录结构", "code": 500})
        else:
            return JsonResponse({"msg": "您选择的是目录结构不存在", "code": 500})

# 我的执行集列表
class TestCaseSuitMonitorView(View):
    def get(self,request):
        belong_verison_id = request.COOKIES["v_id"]
        if belong_verison_id != '':
            all_TestCaseSuit = TestCaseSuit.objects.filter(Q(belong_version=int(belong_verison_id))).order_by("-id")
            all_requirement = RequirementInfo.objects.filter(Q(belong_version=int(belong_verison_id)) & ~Q(status='0')).order_by("-id")
            all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")

            page_num = request.GET.get('page_num','')
            pa = Paginator(all_TestCaseSuit,10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'case/TestCaseSuit_Monitor.html', {
                "pages":pages,
                "all_requirement":all_requirement,
                "all_users":all_users,
            })
        else:
            return render(request, 'case/TestCaseSuit_Monitor.html', {
                "msg":"belong_verison_id不能为空",
            })

# xmind用例列表
class XMindCaseListView(View):
    def get(self,request):
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id != '':
            all_service = ServiceInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-id")
            all_XMindCase = XMindCase.objects.filter(Q(belong_project=int(belong_project_id)) & ~Q(status='0')).order_by("-id")
            page_num = request.GET.get('page_num','')
            pa = Paginator(all_XMindCase,10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'case/XMindCase_list.html', {
                "pages":pages,
                "all_service":all_service,
            })
        else:
            return render(request, 'case/XMindCase_list.html', {
                "msg":"项目ID不存在",
                "code":500,
            })

# 新增XMind用例
class AddXMindCaseView(View):
    def get(self,request):
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id:
            form = AddXMindCaseForm()
            all_service = ServiceInfo.objects.filter(Q(belong_project=int(belong_project_id)) & ~Q(status='0')).order_by("-id")
            return render(request, "case/XMindCase_add.html", {
                "all_service":all_service,
                "form":form
            })
        else:
            return render(request, "case/XMindCase_add.html", {
                "msg":"请选择一个项目！",
                "code":500,
            })

    def post(self, request):
        #获取选择页面头部的项目id
        belong_project_id = request.COOKIES["p_id"]
        all_service = ServiceInfo.objects.filter(Q(belong_project=int(belong_project_id)) & ~Q(status='0')).order_by("-id")
        if belong_project_id:
            form = AddXMindCaseForm(request.POST)
            name = request.POST.get("name", "")
            belong_service = request.POST.get("belong_service", "")
            detail = request.POST.get("detail","")
            if form.is_valid():
                designer = request.user
                XMindCase_info = XMindCase()
                # 操作外键的的时候，必须要先实例化外键对应的mode
                belong_project = ProjectInfo.objects.get(id=int(belong_project_id))
                belong_service = ServiceInfo.objects.get(id=int(belong_service))
                XMindCase_info.name = name
                XMindCase_info.belong_project = belong_project
                XMindCase_info.belong_service = belong_service
                XMindCase_info.detail = detail
                XMindCase_info.designer = designer
                XMindCase_info.save()
                return HttpResponseRedirect(reverse("case:XMCList"))
            else:
                return render(request, "case/XMindCase_add.html",
                              {
                                  "form": form,
                                  "all_service":all_service,
                              })
        else:
            return JsonResponse({"msg": "项目id不存在，请选择一个项目！", "code": 500}, content_type='application/json')

# 修改XMind用例
class ModifyXMindCaseView(View):

    def get(self,request,XMindCase_id):
        # all_project用于头部的项目选择
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id:
            all_service = ServiceInfo.objects.filter(Q(belong_project=int(belong_project_id)) & ~Q(status='0')).order_by("-id")
            all_XMindCase = XMindCase.objects.get(id=int(XMindCase_id))
            form = ModifyXMindCaseForm(initial={'detail':all_XMindCase.detail})
            return render(request, "case/XMindCase_modify.html", {
                "all_service":all_service,
                "form":form,
                "all_XMindCase":all_XMindCase,
            })
        else:
            return render(request, "case/XMindCase_modify.html", {
                "msg":"p_id不存在，请先选择一个项目！",
                "code":500,
            })

    def post(self, request, XMindCase_id):
        # 获取选择页面头部的项目id
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id:
            all_service = ServiceInfo.objects.filter(Q(belong_project=int(belong_project_id)) & ~Q(status='0')).order_by("-id")
            form = ModifyXMindCaseForm(request.POST)
            name = request.POST.get("name", "")
            belong_service = request.POST.get("belong_service", "")
            detail = request.POST.get("detail","")
            status = request.POST.get("status","")
            modifier = request.user.username
            if not name:
                return render(request, "case/XMindCase_modify.html",
                              {
                                  "form": form,
                                  "msg": "XMindCase主题不能为空！",
                                  "all_service": all_service,
                              })
            if not detail:
                return render(request, "case/XMindCase_modify.html",
                              {
                                  "form": form,
                                  "msg": "请填写XMindCase详情",
                                  "all_service": all_service,
                              })
            if not belong_service:
                return render(request, "case/XMindCase_modify.html",
                              {
                                  "form": form,
                                  "msg": "请选择所属服务！",
                                  "all_service": all_service,
                              })
            if XMindCase_id:
                XMindCase_info = XMindCase.objects.get(id=int(XMindCase_id))
                # 操作外键的的时候，必须要先实例化外键对应的mode
                belong_service = ServiceInfo.objects.get(id=int(belong_service))
                XMindCase_info.name = name
                XMindCase_info.belong_service = belong_service
                XMindCase_info.detail = detail
                XMindCase_info.modifier = modifier
                XMindCase_info.status = status
                XMindCase_info.save()
                return HttpResponseRedirect(reverse("case:XMCList"))
        else:
            return render(request, "case/XMindCase_modify.html", {
                "msg":"p_id或者XMindCase_id不存在！",
                "code":500,
            })

# XMind用例详情
class XMindCaseDetailView(View):
    def get(self,request,XMindCase_id):
        # 获取选择页面头部的项目id
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id:
            all_service = ServiceInfo.objects.filter(Q(belong_project=int(belong_project_id)) & ~Q(status='0')).order_by("-id")
            if XMindCase_id:
                all_XMindCase = XMindCase.objects.get(id=int(XMindCase_id))
                form = XMindCaseDetailForm(initial={'detail': all_XMindCase.detail})
                return render(request, "case/XMindCase_detail.html", {
                    "all_service":all_service,
                    "form":form,
                    "all_XMindCase":all_XMindCase,
                })
            else:
                return render(request, "case/XMindCase_detail.html", {
                    "msg":"XMindCase_id不存在",
                    "code":500,
                    "all_service":all_service,
                })
        else:
            return render(request, "case/XMindCase_detail.html", {
                    "msg":"belong_project_id不存在",
                    "code":500,
                })

# 删除XMindCase
class DelXMindCaseView(View):
    def post(self, request):
        XMindCase_id = request.POST.get("XMindCase_id", "")
        if XMindCase_id:
            if XMindCase.objects.filter(status=1):
                all_XMindCase = XMindCase.objects.get(id=int(XMindCase_id))
                all_XMindCase.status = '0'
                all_XMindCase.save()
                return JsonResponse({
                    "msg":"删除XMindCase成功",
                    "code":200,
                })
            else:
                return JsonResponse({"msg": "当前XMindCase非新建状态不能删除！", "code": 500}, content_type='application/json')

        else:
            return JsonResponse({"msg":"XMindCase_id不存在！", "code":500}, content_type='application/json')

# 搜索XMindCase
class SearchXMindCaseView(View):
    def get(self,request):
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id != '':
            all_service = ServiceInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-id")
            all_XMindCase = XMindCase.objects.filter(belong_project=int(belong_project_id)).order_by("-id")
            # 按照xmindcase_name搜索
            xmindcase_name = request.GET.get("xmindcase_name","")
            if xmindcase_name:
                all_XMindCase = all_XMindCase.filter(name__contains=xmindcase_name)
                print("xmindcase_name:",xmindcase_name)
            # 按照所属服务搜索
            xmindcase_belong_service = request.GET.get("xmindcase_belong_service","")
            if xmindcase_belong_service:
                all_XMindCase = all_XMindCase.filter(belong_service=int(xmindcase_belong_service))
                print("all_XMindCase:",all_XMindCase)
            # 按照状态搜索
            xmindcase_status = request.GET.get("xmindcase_status","")
            if xmindcase_status:
                all_XMindCase = all_XMindCase.filter(status=xmindcase_status)

            page_num = request.GET.get('page_num','')
            pa = Paginator(all_XMindCase,10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, "case/XMindCase_list.html", {
                    "pages": pages,
                    "all_service":all_service,
                    "xmindcase_name":xmindcase_name,
                    "xmindcase_belong_service":xmindcase_belong_service,
                    "xmindcase_status":xmindcase_status,

                })

        else:
            return render(request,"case/XMindCase_list.html", {
                    "code": 500,
                    "msg": "belong_project_id不存在",
            })
