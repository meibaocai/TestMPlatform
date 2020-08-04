from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.views.generic.base import View
from requirement.models import RequirementInfo
from bugs.models import BugInfo,BugRecords
from manager.models import VersionInfo
from users.models import UserProfile
from bugs.forms import AddBugForm,BugDetailForm,ModifyBugForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse

# 版本bug列表.
class BugListView(View):
    def get(self,request):
        belong_version_id = request.COOKIES["v_id"]
        if belong_version_id != '':
            all_Requirement = RequirementInfo.objects.filter(belong_version=int(belong_version_id)).order_by("-id")
            all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")
            all_bugs = BugInfo.objects.filter(belong_version=int(belong_version_id)).order_by("-id")
            page_num = request.GET.get('page_num','')
            pa = Paginator(all_bugs,10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'bugs/bug_list.html', {
                "pages":pages,
                "all_Requirement":all_Requirement,
                "all_users":all_users,
            })
        else:
            return render(request, 'bugs/bug_list.html', {
                "msg":"请先选择版本！",
                "code":500,
            })

class BugDetailView(View):
    def get(self,request,bug_id):
        # belong_version_id = request.COOKIES["v_id"]
        all_bugs = BugInfo.objects.get(id=int(bug_id))
        form = BugDetailForm(initial={'detail':all_bugs.detail})
        return render(request, "bugs/bug_detail.html", {
                "form": form,
                "all_bugs": all_bugs,
                # "detail":all_bugs.detail
            })

class AddBugView(View):
    def get(self,request):
        belong_verison_id = request.COOKIES["v_id"]
        form = AddBugForm()
        all_Requirement = RequirementInfo.objects.filter(belong_version=int(belong_verison_id)).order_by("-id")
        all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")

        return render(request, "bugs/bug_add.html", {
            "all_Requirement":all_Requirement,
            "form":form,
            "all_users":all_users
        })

    def post(self, request):
        #获取选择页面头部的项目id
        belong_version_id = request.COOKIES["v_id"]
        if belong_version_id:
            form = AddBugForm(request.POST)
            name = request.POST.get("name", "")
            detail = request.POST.get("detail","")
            solver = request.POST.get("solver","")
            level = request.POST.get("level","")
            belong_requirement = request.POST.get("belong_requirement","")
            # print("belong_requirement",belong_requirement)
            env = request.POST.get("env","")
            # print("env",env)
            if not name:
                return render(request, "bugs/bug_add.html",
                              {
                                  "form.name": form.name,
                                  "msg": "BUG主题不能为空！",
                              })
            if not detail:
                return render(request, "bugs/bug_add.html",
                              {
                                  "form": form,
                                  "msg": "请填写需求详情",
                              })
            if not solver:
                return render(request, "bugs/bug_add.html",
                              {
                                  "form": form,
                                  "msg": "指派人不能为空！",
                              })
            else:
                reporter = request.user.username
                bug_info = BugInfo()
                #操作外键的的时候，必须要先实例化外键对应的mode
                version_id = VersionInfo.objects.get(id=int(belong_version_id))
                belong_requirement = RequirementInfo.objects.get(id=int(belong_requirement))
                bug_info.name = name
                bug_info.belong_version = version_id
                bug_info.detail = detail
                bug_info.reporter = reporter
                bug_info.solver = solver
                bug_info.level = level
                bug_info.env = env
                bug_info.belong_requirement = belong_requirement
                bug_info.status = "Open"
                bug_info.save()
                return HttpResponseRedirect(reverse("bugs:MyBugs"))
        else:
            return JsonResponse({"msg": "版本id不存在，请详见项目！", "code": 404}, content_type='application/json')

class ModifyBugView(View):
    def get(self,request,bug_id):
        #all_project用于头部的版本选择
        belong_version_id = request.COOKIES["v_id"]
        all_bugs = BugInfo.objects.get(id=int(bug_id))
        all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")
        all_requirement = RequirementInfo.objects.filter(belong_version=int(belong_version_id)).order_by("id")
        # print(all_requirement)
        form = ModifyBugForm(initial={'detail':all_bugs.detail})
        return render(request, "bugs/bug_modify.html", {
            "form":form,
            "all_bugs": all_bugs,
            "all_users":all_users,
            "all_requirement":all_requirement
        })
    def post(self,request,bug_id):
        #获取选择页面头部的版本id
        belong_version_id = request.COOKIES["v_id"]
        all_requirement = RequirementInfo.objects.filter(belong_version=int(belong_version_id)).order_by("id")
        form = ModifyBugForm(request.POST)
        name = request.POST.get("name", "")
        detail = request.POST.get("detail","")
        solver = request.POST.get("solver", "")
        status = request.POST.get("status","")
        belong_requirement = request.POST.get("belong_requirement","")
        print("belong_requirement",belong_requirement)
        env = request.POST.get("env","")
        level = request.POST.get("level", "")
        if not name:
            return render(request, "bugs/bug_modify.html",
                          {
                              "form.dtail": form.dtail,
                              "msg": "需求主题不能为空！",
                              "all_requirement": all_requirement,
                          })
        if not detail:
            return render(request, "bugs/bug_modify.html",
                          {
                              "form": form,
                              "msg": "请填写需求详情",
                              "all_requirement": all_requirement,
                          })
        else:
            bug_info = BugInfo.objects.get(id=int(bug_id))
            #操作外键的的时候，必须要先实例化外键对应的mode
            belong_requirement = RequirementInfo.objects.get(id=int(belong_requirement))
            bug_info.name = name
            bug_info.belong_requirement = belong_requirement
            bug_info.detail = detail
            bug_info.solver = solver
            bug_info.status = status
            bug_info.env = env
            bug_info.level = level
            bug_info.save()
            return HttpResponseRedirect(reverse("bugs:MyBugs"))

class DelBugView(View):
    def post(self, request):
        bug_id = request.POST.get("bug_id", "")
        username =request.user.username
        if bug_id:
            if BugInfo.objects.filter(Q(reporter=username) & Q(status="Open")).order_by("-id"):
                all_bug = BugInfo.objects.get(id=int(bug_id))
                all_bug.delete()
                return JsonResponse({
                    "msg":"Bug删除成功",
                    "code":200,
                })
        else:
            # return render(request, "manager/porject_list.html",{"msg": "删除项目失败，项目ID不存在！",})
            return JsonResponse({"msg":"删除Bug信息失败！", "code":202}, content_type='application/json')

class MyBugListView(View):
    def get(self, request):
        belong_version_id = request.COOKIES["v_id"]
        # print("belong_version_id:",belong_version_id)
        if belong_version_id:
            all_Requirement = RequirementInfo.objects.filter(belong_version=int(belong_version_id)).order_by("-id")
            all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")
            print(belong_version_id)
            username = request.user
            print(username)
            all_bugs = BugInfo.objects.filter(Q(belong_version=int(belong_version_id)) & (Q(reporter=username) | Q(solver=username))).order_by("-id")
            page_num = request.GET.get('page_num', '')
            pa = Paginator(all_bugs, 10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'bugs/mybug_list.html', {
                "pages": pages,
                "all_Requirement":all_Requirement,
                "all_users":all_users,
            })
        else:
            return render(request, 'bugs/mybug_list.html', {
                "msg": "v_id不能为空，请先选择版本",
                "code":500,
            })

class SearchBugView(View):
    def get(self,request):
        belong_verison_id = request.COOKIES["v_id"]
        if belong_verison_id:
            all_Requirement = RequirementInfo.objects.filter(belong_version=int(belong_verison_id)).order_by("-id")
            all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")
            all_bugs = BugInfo.objects.filter(belong_version=int(belong_verison_id)).order_by("-id")
            # 按照bug_id搜索
            bug_id = request.GET.get("bug_id","")
            if bug_id:
                all_bugs = all_bugs.filter(id=int(bug_id))
            # 按照bug_name搜索
            bug_name = request.GET.get("bug_name","")
            if bug_name:
                all_bugs = all_bugs.filter(name__contains=bug_name)
            # 按照经办人搜索
            bug_solver = request.GET.get("bug_solver","")
            if bug_solver:
                all_bugs = all_bugs.filter(solver=bug_solver)
            # 按照报告人搜索
            bug_reporter = request.GET.get("bug_reporter","")
            if bug_reporter:
                all_bugs = all_bugs.filter(reporter=bug_reporter)
            # 按照优先级搜索
            bug_level = request.GET.get("bug_level","")
            if bug_level:
                all_bugs = all_bugs.filter(level=bug_level)
            # 按照所属需求搜索
            bug_belong_requirement = request.GET.get("bug_belong_requirement","")
            if bug_belong_requirement:
                all_bugs = all_bugs.filter(belong_requirement=int(bug_belong_requirement))
            # 按照环境搜索
            bug_env = request.GET.get("bug_env","")
            if bug_env:
                all_bugs = all_bugs.filter(env=bug_env)
            # 按照状态修改
            bug_status_list = request.GET.getlist("bug_status","")
            select_status = ''
            if bug_status_list:
                # print("bug_status:",bug_status)
                all_bugs = all_bugs.filter(status__in=bug_status_list)
                for i in bug_status_list:
                    select_status += 'bug_status='+i+'&'
                # print("select_status:",select_status)
            bug_channel = request.GET.get("bug_channel","")
            if bug_channel == 'everyone':
                # 分页
                page_num = request.GET.get('page_num','')
                pa = Paginator(all_bugs,10)
                try:
                    pages = pa.page(page_num)
                except PageNotAnInteger:
                    pages = pa.page(1)
                except EmptyPage:
                    pages = pa.page(pa.num_pages)
                return render(request, "bugs/bug_list.html", {
                    "pages": pages,
                    "all_Requirement": all_Requirement,
                    "all_users": all_users,
                    "bug_id": bug_id,
                    "bug_name": bug_name,
                    "bug_solver": bug_solver,
                    "bug_reporter": bug_reporter,
                    "bug_level": bug_level,
                    "bug_belong_requirement": bug_belong_requirement,
                    "bug_env": bug_env,
                    "bug_status": select_status,
                    "bug_status_list": bug_status_list,

                })
            if bug_channel == 'owner':
                username = request.user
                all_bugs = all_bugs.filter(Q(solver=username) | Q(reporter=username))
                # 分页
                page_num = request.GET.get('page_num', '')
                pa = Paginator(all_bugs, 10)
                try:
                    pages = pa.page(page_num)
                except PageNotAnInteger:
                    pages = pa.page(1)
                except EmptyPage:
                    pages = pa.page(pa.num_pages)

                return render(request,"bugs/mybug_list.html", {
                    "pages": pages,
                    "all_Requirement": all_Requirement,
                    "all_users": all_users,
                    "bug_id": bug_id,
                    "bug_name": bug_name,
                    "bug_solver": bug_solver,
                    "bug_reporter": bug_reporter,
                    "bug_level": bug_level,
                    "bug_belong_requirement": bug_belong_requirement,
                    "bug_env": bug_env,
                    "bug_status": select_status,
                    "bug_status_list": bug_status_list,

                })

        return render(request, "bugs/mybug_list.html", {
            "msg": "v_id不能为空，请先选择版本！",
            "code": 500,
        })
