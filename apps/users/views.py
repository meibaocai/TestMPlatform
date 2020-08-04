# _*_ encoding:utf-8 _*_
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseRedirect
from .forms import LoginForm,RegisterForm,ForgetForm,ModifyPwdForm
from utils.email_send import send_register_email
from django.urls import reverse
from users.models import UserProfile,EmailVerifyRecord
from manager.models import ProjectInfo
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

class IndexView(View):
    def get(self, request):
        # 返回默认项目名称和项目ID，default_pname，default_pid
        all_project = ProjectInfo.objects.all().order_by("-add_time")
        # project_id = request.COOKIES["p_id"]
        # print("project_id:",project_id)
        return render(request, "index.html", {
            "all_project":all_project,
        })

class LogoutView(View):
    """
    用户登出
    """
    def get(self, request):
        logout(request)
        return render(request, "login.html", {})

class LoginView(View):
    def get(self, request):
        return render(request, "login.html", {})
    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "login.html", {"msg":"用户未激活！"})
            else:
                return render(request, "login.html", {"msg":"用户名或密码错误！"})
        else:
            return render(request, "login.html", {"login_form":login_form})

class RegisterView(View):
    def get(self, request):
        # register_form = RegisterForm()
        return render(request, "register.html", {})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")
            rpassword = request.POST.get("rpassword")

            if UserProfile.objects.filter(username=username):
                return render(request, "register.html", {"register_form":register_form,"msg":"注册失败,用户已经存在!"})

            if password != rpassword:
                return render(request,"register.html", {"register_form":register_form,"msg":"注册失败,两次密码不一致"})

            email = request.POST.get("email", "")
            mobile = request.POST.get("mobile","")
            user_profile = UserProfile()
            user_profile.username = username
            user_profile.email = email
            user_profile.mobile = mobile
            user_profile.is_active = False
            user_profile.password = make_password(password)
            user_profile.save()
            send_register_email(email, "register")
            return render(request, "register.html",{"register_form":register_form,"msg":"注册成功,请去邮箱激活账号！"})
        else:
            return render(request, "register.html", {"register_form":register_form,"msg":"注册失败！"})

class AciveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, "active_status.html", {"msg":"链接无效！ "})

        return render(request, "active_status.html", {"msg":"您的账户 "+email +" 激活成功，可以去登录啦！"})

class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forgetpwd.html", {"forget_form":forget_form})

    def post(self, request):
        # forget_form = ForgetForm(request.POST)
        email = request.POST.get("email", "")
        # if forget_form.is_valid():
        if UserProfile.objects.filter(email=email):
            send_register_email(email, "forget")
            return render(request, "send_success.html")
        else:
            return render(request, "forgetpwd.html", {"msg":"邮箱格式不正确或邮箱不存在！"})

class ResetView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {"email":email})
        else:
            return render(request, "active_status.html")
        return render(request, "login.html")

class ModifyPwdView(View):
    """
    修改用户密码
    """
    def post(self, request):

        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email":email, "msg":"密码不一致"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()

            return render(request, "login.html", {"email":email, "msg":"密码成功！"})
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email":email, "modify_form":modify_form})

class UserListView(View):
    def get(self,request):
        all_project = ProjectInfo.objects.all().order_by("-add_time")
        default_pname = all_project[0].project_name
        default_pid = all_project[0].id
        all_user = UserProfile.objects.all().order_by("-add_time")
        page_num = request.GET.get('page_num','')
        pa = Paginator(all_user,10)
        try:
            pages = pa.page(page_num)
        except PageNotAnInteger:
            pages = pa.page(1)
        except EmptyPage:
            pages = pa.page(pa.num_pages)
        return render(request, 'manager/user_list.html', {
            "pages":pages,
            "all_project":all_project,
            "default_pname":default_pname,
            "default_pid":default_pid,
        })

class SearchUserView(View):
    def get(self,request):
        keywords = request.GET.get("keywords", "")
        page_num = request.GET.get('page_num', '')
        all_users = UserProfile.objects.all().order_by("-add_time")
        if keywords:
            all_users = all_users.filter(Q(username__icontains=keywords) | Q(email__icontains=keywords) | Q(mobile__icontains=keywords))
        pa = Paginator(all_users, 10)
        try:
            pages = pa.page(page_num)
        except PageNotAnInteger:
            pages = pa.page(1)
        except EmptyPage:
            pages = pa.page(pa.num_pages)
        return render(request, 'manager/user_list.html', {
            "pages": pages,
            "keywords":keywords,
        })

def page_not_found(request):
    #全局404处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response

def page_error(request):
    #全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response