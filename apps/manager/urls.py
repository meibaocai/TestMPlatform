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

from django.conf.urls import url
from manager.views import ProjectInfoView,AddProjectView,ModifyProjectView,VersionListView,AddVersionView,\
    ModifyVersionView,DelProjectView,DelVersionView,ServiceInfoView,AddServiceView,ModifyServiceView,DelServiceView
from users.views import UserListView,SearchUserView
urlpatterns = [
    url(r'plist$', ProjectInfoView.as_view(), name='plist'),
    url(r'AddProject$', AddProjectView.as_view(), name='AddProject'),
    url(r'ModifyProject/(?P<project_id>.*)/$', ModifyProjectView.as_view(), name='ModifyProject'),
    url(r'DelProject$', DelProjectView.as_view(), name='DelProject'),
    url(r'VersionList$', VersionListView.as_view(), name='VersionList'),
    url(r'AddVersion$', AddVersionView.as_view(), name='AddVersion'),
    url(r'ModifyVersion/(?P<version_id>.*)/$', ModifyVersionView.as_view(), name='ModifyVersion'),
    url(r'DelVersion$', DelVersionView.as_view(), name='DelVersion'),
    url(r'UserList$', UserListView.as_view(), name='UserList'),
    url(r'SearchUser$', SearchUserView.as_view(), name='SearchUser'),
    url(r'ServiceList$', ServiceInfoView.as_view(), name='ServiceList'),
    url(r'AddService$', AddServiceView.as_view(), name='AddService'),
    url(r'ModifyService/(?P<service_id>.*)/$', ModifyServiceView.as_view(), name='ModifyService'),
    url(r'DelService$', DelServiceView.as_view(), name='DelService'),

]
