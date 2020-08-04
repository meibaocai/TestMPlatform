from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.views.generic.base import View
from requirement.models import RequirementInfo
from manager.models import VersionInfo,ProjectInfo
from users.models import UserProfile
from requirement.forms import AddRequirementForm,ModifyRequirementForm,RequirementDetailForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.urls import reverse
import os
from django.conf import settings
from  django.http import JsonResponse
import json
from utils.email_send import random_str

# Create your views here.
class RequirementListView(View):
    def get(self,request):
        belong_project_id = request.COOKIES["p_id"]
        all_version = VersionInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-id")
        # all_requirement = RequirementInfo.objects.all().order_by("-add_time")
        all_requirement = RequirementInfo.objects.filter(Q(project_id=int(belong_project_id)) & ~Q(status='0')).order_by("-id")
        page_num = request.GET.get('page_num','')
        pa = Paginator(all_requirement,10)
        try:
            pages = pa.page(page_num)
        except PageNotAnInteger:
            pages = pa.page(1)
        except EmptyPage:
            pages = pa.page(pa.num_pages)
        return render(request, 'requirement/requirement_list.html', {
            "pages":pages,
            "all_version":all_version,
        })

class AddRequirementView(View):
    def get(self,request):
        belong_project_id = request.COOKIES["p_id"]
        form = AddRequirementForm()
        all_version = VersionInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-id")
        return render(request, "requirement/requirement_add.html", {
            "all_version":all_version,
            "form":form
        })

    def post(self, request):
        #获取选择页面头部的项目id
        belong_project_id = request.COOKIES["p_id"]
        if belong_project_id:
            all_version = VersionInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-id")
            form = AddRequirementForm(request.POST)
            name = request.POST.get("requirement_name", "")
            belong_version = request.POST.get("belong_version", "")
            detail = request.POST.get("detail","")
            if not name:
                return render(request, "requirement/requirement_add.html",
                              {
                                  "form": form,
                                  "msg": "需求主题不能为空！",
                                  "all_version": all_version,
                              })
            if not detail:
                return render(request, "requirement/requirement_add.html",
                              {
                                  "form": form,
                                  "msg": "请填写需求详情",
                                  "all_version": all_version,
                              })
            if not belong_version:
                return render(request, "requirement/requirement_add.html",
                              {
                                  "form": form,
                                  "msg": "需求版本不能为空！",
                                  "all_version": all_version,
                              })
            else:
                creator = request.user
                requirement_info = RequirementInfo()
                #操作外键的的时候，必须要先实例化外键对应的mode
                version_id = VersionInfo.objects.get(id=int(belong_version))
                requirement_info.name = name
                requirement_info.belong_version = version_id
                requirement_info.detail = detail
                requirement_info.creator = creator
                requirement_info.project_id = int(belong_project_id)
                requirement_info.save()
                return HttpResponseRedirect(reverse("requirement:RequirementList"))
        else:
            return JsonResponse({"msg": "项目id不存在，请详见项目！", "code": 404}, content_type='application/json')

class ModifyRequirementView(View):
    def get(self,request,requirement_id):
        #all_project用于头部的项目选择
        belong_project_id = request.COOKIES["p_id"]
        all_version = VersionInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-id")
        all_users = UserProfile.objects.filter(is_active=1).order_by("add_time")
        requirements = RequirementInfo.objects.get(id=int(requirement_id))
        # form = ModifyRequirementForm()
        form = ModifyRequirementForm(initial={'detail':requirements.detail})
        return render(request, "requirement/requirement_modify.html", {
            "all_version":all_version,
            "form":form,
            "requirements":requirements,
            "all_users":all_users,
        })

    def post(self, request,requirement_id):
        #获取选择页面头部的项目id
        belong_project_id = request.COOKIES["p_id"]
        all_version = VersionInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-id")
        form = ModifyRequirementForm(request.POST)
        name = request.POST.get("requirement_name", "")
        belong_version = request.POST.get("belong_version", "")
        detail = request.POST.get("detail","")
        creator = request.POST.get("creator", "")
        solver = request.POST.get("solver", "")
        tester = request.POST.get("tester", "")
        if not name:
            return render(request, "requirement/requirement_modify.html",
                          {
                              "form": form,
                              "msg": "需求主题不能为空！",
                              "all_version": all_version,
                          })
        if not detail:
            return render(request, "requirement/requirement_modify.html",
                          {
                              "form": form,
                              "msg": "请填写需求详情",
                              "all_version": all_version,
                          })
        else:
            requirement_info = RequirementInfo.objects.get(id=int(requirement_id))
            #操作外键的的时候，必须要先实例化外键对应的mode
            version_id = VersionInfo.objects.get(id=int(belong_version))
            requirement_info.name = name
            requirement_info.belong_version = version_id
            requirement_info.detail = detail
            requirement_info.creator = creator
            requirement_info.solver = solver
            requirement_info.tester = tester
            requirement_info.save()
            return HttpResponseRedirect(reverse("requirement:RequirementList"))

class RequirementDetailView(View):
    def get(self,request,requirement_id):
        #获取选择页面头部的项目id
        belong_project_id = request.COOKIES["p_id"]
        all_version = VersionInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-id")
        all_users = UserProfile.objects.all().order_by("add_time")
        requirements = RequirementInfo.objects.get(id=int(requirement_id))
        form = RequirementDetailForm(initial={'detail':requirements.detail})
        return render(request, "requirement/requirement_detail.html", {
            "all_version":all_version,
            "form":form,
            "requirements":requirements,
            "all_users":all_users,
        })

class DelRequirementView(View):
    def post(self, request):
        requirement_id = request.POST.get("requirement_id", "")
        if requirement_id:
            if RequirementInfo.objects.filter(status=1):
                # return render(request, "manager/porject_list.html", {"msg": "该项目下存在版本信息，请先删除版本信息！","code": 400,}, content_type='application/json')
                all_requirement = RequirementInfo.objects.get(id=int(requirement_id))
                all_requirement.delete()
                return JsonResponse({
                    "msg":"需求信息删除成功",
                    "code":200,
                })
        else:
            # return render(request, "manager/porject_list.html",{"msg": "删除项目失败，项目ID不存在！",})
            return JsonResponse({"msg":"当前需求非新建状态不能删除！", "code":202}, content_type='application/json')

class MyRequirementListView(View):
    def get(self, request):
        belong_project_id = request.COOKIES["p_id"]
        username = request.user.username
        if belong_project_id:
            all_version = VersionInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-id")
            all_requirement = RequirementInfo.objects.filter(Q(project_id=int(belong_project_id)) & ~Q(status='0') & (Q(creator=username) | Q(solver=username) | Q(tester=username))).order_by("-id")
            page_num = request.GET.get('page_num', '')
            pa = Paginator(all_requirement, 10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'requirement/my_requirement_list.html', {
                "pages": pages,
                "all_version": all_version,
            })
        else:
            return render(request, 'requirement/my_requirement_list.html', {
                "mgs":"请选择belong_project_id"
            })

class SearchMyRequirementView(View):
    def get(self, request):
        belong_project_id = request.COOKIES["p_id"]
        username = request.user.username
        all_version = VersionInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-id")

        if belong_project_id:
            all_requirement = RequirementInfo.objects.filter(Q(project_id=int(belong_project_id)) & ~Q(status='0') & (Q(creator=username) | Q(solver=username) | Q(tester=username))).order_by("-id")
            requirement_id = request.GET.get('requirement_id', '')
            if requirement_id:
                all_requirement = all_requirement.filter(id=int(requirement_id))
            search_key = request.GET.get('search_key', '')
            if search_key:
                all_requirement = all_requirement.filter(name__icontains=search_key)
            belong_version = request.GET.get('belong_version', '')
            if belong_version:
                all_requirement = all_requirement.filter(belong_version=int(belong_version))
            requirement_status = request.GET.get('requirement_status', '')
            if requirement_status:
                all_requirement = all_requirement.filter(status=requirement_status)
                # print("select_status:",select_status)
            page_num = request.GET.get('page_num', '')
            requirement_channel = request.GET.get('requirement_channel', '')

            pa = Paginator(all_requirement, 10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)

            if requirement_channel == 'myself':
                return render(request, 'requirement/my_requirement_list.html', {
                    "pages": pages,
                    "all_version": all_version,
                    "search_key":search_key,
                    "belong_version":belong_version,
                    "requirement_id":requirement_id,
                    "requirement_status":requirement_status,
                })
            if requirement_channel == 'everyone':
                return render(request, 'requirement/requirement_list.html', {
                    "pages": pages,
                    "all_version": all_version,
                    "search_key": search_key,
                    "belong_version": belong_version,
                    "requirement_id": requirement_id,
                    "requirement_status": requirement_status,
                })
            else:
                return JsonResponse({
                    "msg":"requirement_channel不合法！",
                    "code":500,
                })

        else:
            return render(request, 'requirement/my_requirement_list.html', {
                "all_version": all_version,
                "msg":"请选择版本！",
                "code":500,
            })

class RequirementMonitorView(View):
    def get(self, request):
        belong_version_id = request.COOKIES["v_id"]
                # all_version = VersionInfo.objects.filter(belong_project=int(belong_project_id)).order_by("-id")
                # all_requirement = RequirementInfo.objects.all().order_by("-add_time")
        if belong_version_id:
            all_requirement = RequirementInfo.objects.filter(Q(belong_version=int(belong_version_id)) & ~Q(status='0')).order_by("-id")

            page_num = request.GET.get('page_num', '')
            pa = Paginator(all_requirement, 10)
            try:
                pages = pa.page(page_num)
            except PageNotAnInteger:
                pages = pa.page(1)
            except EmptyPage:
                pages = pa.page(pa.num_pages)
            return render(request, 'requirement/requirement_Monitor.html', {
                        "pages": pages,
                        # "all_version": all_version,
                    })
        else:
            return render(request, 'requirement/requirement_Monitor.html', {
                "msg": "请选择版本号!",
                "code":500,
            })

class ChangeRequirementStatusView(View):
    def post(self, request):
        requirement_id = request.POST.get("requirement_id", "")
        requirement_status = request.POST.get("requirement_status", "")
        if requirement_id:
            all_requirement = RequirementInfo.objects.get(id=int(requirement_id))
            all_requirement.status = requirement_status
            all_requirement.save()
            return JsonResponse({
                    "msg":"修改需求状态成功",
                    "code":200,
            })
        else:
            # return render(request, "manager/porject_list.html",{"msg": "删除项目失败，项目ID不存在！",})
            return JsonResponse({"msg":"需求ID不存在！", "code":500}, content_type='application/json')

