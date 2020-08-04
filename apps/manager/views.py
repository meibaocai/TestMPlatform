from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.views.generic.base import View
from manager.models import ProjectInfo,DepartmentInfo,VersionInfo,ServiceInfo
from case.models import VersionCase,TestCaseSuit
from requirement.models import RequirementInfo
from manager.forms import AddProjectForm,ModifyProjectFrom,AddVersionForm,ModifyVersionForm,AddServiceForm,ModifyServiceFrom
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.urls import reverse
from  django.http import JsonResponse
import json


# Create your views here.
class ProjectInfoView(View):
    def get(self,request):
        all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
        page_num = request.GET.get('page_num','')
        pa = Paginator(all_project,10)
        try:
            pages = pa.page(page_num)
        except PageNotAnInteger:
            pages = pa.page(1)
        except EmptyPage:
            pages = pa.page(pa.num_pages)
        return render(request, 'manager/porject_list.html', {
            # "all_projects": all_project,
            "pages":pages,
        })
    def post(self,request):
        all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
        projects = [
            {
                'project_id': x.id,
                'project_name': x.project_name,
            } for x in all_project
        ]
        # return JsonResponse(projects,safe=False)

        # return JsonResponse({"projects": projects})
        # print(json.dumps(projects))
        return HttpResponse(json.dumps(projects,ensure_ascii=False))

class AddProjectView(View):
    def get(self,request):
        all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
        all_department = DepartmentInfo.objects.all().order_by("-add_time")
        return render(request, "manager/porject_add.html", {
            "all_department": all_department,
            "all_project": all_project,
        })

    def post(self, request):
        #返回默认项目名称和项目ID，default_pname，default_pid
        all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
        all_department = DepartmentInfo.objects.all().order_by("-add_time")
        AddProject_From = AddProjectForm(request.POST)
        if AddProject_From.is_valid():
            project_name = request.POST.get("project_name", "")
            department_id = request.POST.get("department_id", "")
            project_desc = request.POST.get("project_desc", "")
            creator = request.user
            project_info = ProjectInfo()
            if ProjectInfo.objects.filter(project_name=project_name):
                return render(request, "manager/porject_add.html",
                              {"AddProject_From":AddProject_From,
                               "all_department":all_department, "msg": "新增失败,项目已经存在!",
                               "all_project":all_project,

                               })
            #操作外键的的时候，必须要先实例化外键对应的mode
            department_id = DepartmentInfo.objects.get(id=int(department_id))
            project_info.project_name = project_name
            project_info.project_desc = project_desc
            project_info.blong_department = department_id
            project_info.creator = creator
            project_info.save()
            return render(request, "manager/porject_add.html",
                          {
                              "AddProject_From":AddProject_From,
                              "all_department":all_department,
                              "msg": "操作成功！",
                              "all_project": all_project,
                          })
        else:
            return render(request, "manager/porject_add.html",
                          {
                              "AddProject_From":AddProject_From,
                              "all_department":all_department,
                              "msg": "新增项目失败！",
                              "all_project": all_project,
                          })

class ModifyProjectView(View):
    def get(self,request,project_id):
        all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
        all_department = DepartmentInfo.objects.all().order_by("-add_time")
        projects = ProjectInfo.objects.get(id=int(project_id))
        return render(request, "manager/project_modify.html", {
            "projects": projects,
            "all_department": all_department,
            "all_project": all_project,
        })

    def post(self,request,project_id):
        all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
        projects = ProjectInfo.objects.get(id=int(project_id))
        all_department = DepartmentInfo.objects.all().order_by("-add_time")
        project_info = ProjectInfo.objects.get(id=int(project_id))
        ModifyProject_From = ModifyProjectFrom(request.POST)
        if ModifyProject_From.is_valid():
            project_name = request.POST.get("project_name", "")
            department_id = request.POST.get("department_id", "")
            project_desc = request.POST.get("project_desc", "")
            if ProjectInfo.objects.filter(project_name=project_name).exclude(id=project_id):
                return render(request, "manager/project_modify.html",
                              {"ModifyProject_From": ModifyProject_From,
                               "all_department": all_department,
                               "projects":projects,
                               "msg": "修改失败,项目名称已经存在!",
                               "all_project": all_project,
                               })
                # return HttpResponse('{"status":"fail", "msg":"修改失败，项目名称已经存在!"}', content_type='application/json')

            # 操作外键的的时候，必须要先实例化外键对应的mode
            department_id = DepartmentInfo.objects.get(id=int(department_id))
            project_info.project_name = project_name
            project_info.project_desc = project_desc
            project_info.blong_department = department_id
            # project_info.creator = creator
            project_info.save()
            return HttpResponseRedirect(reverse("manager:plist"))
            # return HttpResponse('{"status":"success", "msg":"修改成功"}', content_type='application/json')

        else:
            all_department = DepartmentInfo.objects.all().order_by("-add_time")
            projects = ProjectInfo.objects.get(id=int(project_id))
            return render(request, "manager/project_modify.html",
                          {
                              "ModifyProject_From": ModifyProject_From,
                              "all_department":all_department,
                              "projects":projects,
                              "msg": "修改项目失败！",
                              "all_project": all_project,
                          })
            # return HttpResponse('{"status":"fail", "msg":"修改失败"}', content_type='application/json')

class DelProjectView(View):
    def post(self, request):
        project_id = request.POST.get("project_id", "")
        if project_id:
            all_project = ProjectInfo.objects.get(id=int(project_id))
            if VersionInfo.objects.filter(belong_project=int(project_id)):
                # return render(request, "manager/porject_list.html", {"msg": "该项目下存在版本信息，请先删除版本信息！","code": 400,}, content_type='application/json')
                return JsonResponse({"msg": "该项目下存在版本信息，请先删除版本信息！","code": 201})

            else:
                all_project.status = '0'
                all_project.save()
                # return render(request, "manager/porject_list.html", {"msg": "项目删除成功","code": 200, }, content_type='application/json')
                return JsonResponse({"msg": "项目删除成功","code": 200})
        else:
            # return render(request, "manager/porject_list.html",{"msg": "删除项目失败，项目ID不存在！",})
            return JsonResponse({"msg": "删除项目失败，项目ID不存在！", "code": 500})

class VersionListView(View):
    def get(self,request):
        all_version = VersionInfo.objects.filter(status='1').order_by("-add_time")
        all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
        page_num = request.GET.get('page_num', '')
        pa = Paginator(all_version, 10)
        try:
            pages = pa.page(page_num)
        except PageNotAnInteger:
            pages = pa.page(1)
        except EmptyPage:
            pages = pa.page(pa.num_pages)
        return render(request, 'manager/version_list.html', {
            # "all_version": all_version,
            "pages": pages,
            "all_project":all_project,
        })

    def post(self,request):
        project_id = request.POST.get('project_id','')
        if project_id:
            all_version = VersionInfo.objects.filter(belong_project=int(project_id)).order_by("-add_time")
            versions = [
                {
                    'version_id': x.id,
                    'version_name': x.version_name,
                } for x in all_version
            ]
            return HttpResponse(json.dumps(versions, ensure_ascii=False))
        else:
            return HttpResponse(json.dumps({"msg": "项目ID不存在","code":500}))

class AddVersionView(View):
    def get(self,request):
        all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
        default_pname = all_project[0].project_name
        default_pid = all_project[0].id
        return render(request, "manager/version_add.html", {
            "all_project": all_project,
            "default_pname": default_pname,
            "default_pid": default_pid,
        })

    def post(self, request):
        all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
        AddVersion_From = AddVersionForm(request.POST)
        if AddVersion_From.is_valid():
            version_name = request.POST.get("version_name", "")
            project_id = request.POST.get("belong_project", "")
            version_desc = request.POST.get("version_desc", "")
            creator = request.user
            version_info = VersionInfo()
            #操作外键的的时候，必须要先实例化外键对应的mode
            project_id = ProjectInfo.objects.get(id=int(project_id))
            version_info.version_name = version_name
            version_info.version_desc = version_desc
            version_info.belong_project = project_id
            version_info.creator = creator
            version_info.save()
            return render(request, "manager/version_add.html",
                          {
                              "AddVerion_From":AddVersion_From,
                              "all_project":all_project,
                              "msg": "操作成功！"
                          })
        else:
            return render(request, "manager/version_add.html",
                          {
                              "AddVersion_From":AddVersion_From,
                              "all_project":all_project,
                              "msg": "新增项目失败！"
                          })

class ModifyVersionView(View):
    def get(self, request, version_id):
        all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
        all_version = VersionInfo.objects.get(id=int(version_id))

        return render(request, "manager/version_modify.html", {
                "all_project": all_project,
                "all_version": all_version,
            })

    def post(self, request, version_id):
        all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
        all_version = VersionInfo.objects.get(id=int(version_id))
        ModifyVersion_From = ModifyVersionForm(request.POST)
        if ModifyVersion_From.is_valid():
            version_name = request.POST.get("version_name", "")
            belong_project = request.POST.get("belong_project", "")
            version_desc = request.POST.get("version_desc", "")
            if VersionInfo.objects.filter(version_name=version_name).exclude(id=version_id):
                return render(request, "manager/project_modify.html",
                              {
                                  "ModifyVersion_From": ModifyVersion_From,
                                  "all_project": all_project,
                                  "all_version":all_version,
                                  "msg": "修改失败,版本名称已经存在!"})

            # 操作外键的的时候，必须要先实例化外键对应的mode
            belong_project = ProjectInfo.objects.get(id=int(belong_project))
            all_version.version_name = version_name
            all_version.version_desc = version_desc
            all_version.belong_project = belong_project
            all_version.save()
            return HttpResponseRedirect(reverse("manager:VersionList"))

        else:
            all_project = ProjectInfo.objects.filter(status='1').order_by("-add_time")
            all_version = VersionInfo.objects.get(id=int(version_id))
            return render(request, "manager/version_modify.html",
                          {
                              "ModifyProject_From": ModifyVersion_From,
                              "all_project": all_project,
                              "all_version":all_version,
                              "msg": "修改版本失败！",
                          })

class DelVersionView(View):
    def post(self, request):
        # all_project = ProjectInfo.objects.all().order_by("-add_time")
        version_id = request.POST.get("version_id", "")
        if version_id:
            all_version = VersionInfo.objects.get(id=int(version_id))
            if VersionCase.objects.filter(belong_version=int(version_id)) or TestCaseSuit.objects.filter(belong_version=int(version_id)):
                return JsonResponse({"msg": "该版本下存在用例和执行集信息，请先删除用例和执行集信息！","code": 500})
            elif RequirementInfo.objects.filter(belong_version=int(version_id)):
                return JsonResponse({"msg": "该项目下存在需求信息，不能删除！","code": 500})

            elif RequirementInfo.objects.filter(belong_version=int(version_id)):
                return JsonResponse({"msg": "该项目下存在需求信息，不能删除！","code": 500})
            else:
                all_version.status = '0'
                all_version.save()
                # return render(request, "manager/porject_list.html", {"msg": "项目删除成功","code": 200, }, content_type='application/json')
                return JsonResponse({"msg": "版本信息删除成功","code": 200})
        else:
            # return render(request, "manager/porject_list.html",{"msg": "删除项目失败，项目ID不存在！",})
            return JsonResponse({"msg": "删除版本信息失败，版本ID不存在！", "code": 202})

class ServiceInfoView(View):
    def get(self,request):
        all_service = ServiceInfo.objects.all().order_by("-add_time")
        page_num = request.GET.get('page_num','')
        pa = Paginator(all_service,10)
        try:
            pages = pa.page(page_num)
        except PageNotAnInteger:
            pages = pa.page(1)
        except EmptyPage:
            pages = pa.page(pa.num_pages)
        return render(request, 'manager/service_list.html', {
            "pages":pages,
        })
    def post(self,request):
        all_service = ServiceInfo.objects.filter(status='1').order_by("-add_time")
        services = [
            {
                'service_id': x.id,
                'service_name': x.name,
            } for x in all_service
        ]
        return HttpResponse(json.dumps(services,ensure_ascii=False))

class AddServiceView(View):
    def get(self,request):
        all_service = ServiceInfo.objects.filter(status='1').order_by("-add_time")
        return render(request, "manager/service_add.html", {
            "all_service": all_service,
        })

    def post(self, request):
        belong_project_id = request.COOKIES["p_id"]
        AddService_Form = AddServiceForm(request.POST)
        if belong_project_id != '':
            if AddService_Form.is_valid():
                name = request.POST.get("name", "")
                desc = request.POST.get("desc", "")
                creator = request.user
                service_info = ServiceInfo()
                if ServiceInfo.objects.filter(name=name):
                    return render(request, "manager/service_add.html",
                                  {"AddService_Form":AddService_Form,
                                   "msg": "新增失败,服务已经存在!",
                                   })
                #操作外键的的时候，必须要先实例化外键对应的mode
                project_id = ProjectInfo.objects.get(id=int(belong_project_id))
                service_info.name = name
                service_info.desc = desc
                service_info.belong_project = project_id
                service_info.creator = creator
                service_info.save()
                return render(request, "manager/service_add.html",
                              {
                                  "AddService_Form":AddService_Form,
                                  "msg": "操作成功！",
                              })
            else:
                return render(request, "manager/service_add.html",
                              {
                                  "AddService_Form":AddService_Form,
                                  "msg": "新增服务失败！",
                              })
        else:
            return render(request, "manager/service_add.html",
                              {
                                  "AddService_Form":AddService_Form,
                                  "msg": "请选择一个项目！",
                              })

class ModifyServiceView(View):
    def get(self,request,service_id):
        services = ServiceInfo.objects.get(id=int(service_id))
        return render(request, "manager/service_modify.html", {
            "services": services,
        })
    def post(self,request,service_id):
        services = ServiceInfo.objects.get(id=int(service_id))
        ModifyService_From = ModifyServiceFrom(request.POST)
        if ModifyService_From.is_valid():
            name = request.POST.get("name", "")
            status = request.POST.get("status", "")
            desc = request.POST.get("desc", "")
            if ServiceInfo.objects.filter(name=name).exclude(id=service_id):
                return render(request, "manager/service_modify.html",
                              {"ModifyService_From": ModifyService_From,
                               "services":services,
                               "msg": "修改失败,服务名称已经存在!",
                               })

            # 操作外键的的时候，必须要先实例化外键对应的mode
            services.name = name
            services.status = status
            services.desc = desc
            # project_info.creator = creator
            services.save()
            return HttpResponseRedirect(reverse("manager:ServiceList"))
            # return HttpResponse('{"status":"success", "msg":"修改成功"}', content_type='application/json')

        else:
            return render(request, "manager/service_modify.html",
                          {
                              "ModifyService_From": ModifyService_From,
                              "services":services,
                              "msg": "修改服务失败！",
                          })
            # return HttpResponse('{"status":"fail", "msg":"修改失败"}', content_type='application/json')

class DelServiceView(View):
    def post(self, request):
        service_id = request.POST.get("service_id", "")
        if service_id:
            all_service = ServiceInfo.objects.get(id=int(service_id))
            all_service.status = '0'
            # print(all_service.status)
            all_service.save()
            return JsonResponse({"msg": "删除成功","code": 200})
        else:
            return JsonResponse({"msg": "删除服务失败，服务ID不存在！", "code": 500})
