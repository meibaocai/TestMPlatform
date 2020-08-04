"""TestMPlatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import include,url
from django.views import static
from .settings import MEDIA_ROOT, STATIC_ROOT

import xadmin
from users.views import IndexView,LoginView,LogoutView,RegisterView,ForgetPwdView,AciveUserView,ResetView,ModifyPwdView
urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^ueditor/', include('DjangoUeditor.urls')),
    url('^static/(?P<path>.*)$', static.serve, {'document_root':STATIC_ROOT}, name='static'),
    url(r'^media/(?P<path>.*)$',static.serve,{"document_root":MEDIA_ROOT},name='media'),
    url(r'^users/', include(('users.urls', "users"), namespace="users")),
    url(r'^case/', include(('case.urls', "case"), namespace="case")),
    url(r'^api/', include(('api.urls', "api"), namespace="api")),
    url(r'^bugs/', include(('bugs.urls', "bugs"), namespace="bugs")),
    url(r'^manager/', include(('manager.urls', "manager"), namespace="manager")),
    url(r'^requirement/', include(('requirement.urls', "requirement"), namespace="requirement")),
    url(r'^index/$', IndexView.as_view(), name="index"),
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url(r'^register/$', RegisterView.as_view(), name="register"),
    url(r'^active/(?P<active_code>.*)/$', AciveUserView.as_view(), name="user_active"),
    url(r'^forget/$', ForgetPwdView.as_view(), name="ForgetPwd"),
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name="reset_pwd"),
]

