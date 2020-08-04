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
from requirement.views import RequirementListView,AddRequirementView,ModifyRequirementView,RequirementDetailView,\
    DelRequirementView,MyRequirementListView,SearchMyRequirementView,RequirementMonitorView,ChangeRequirementStatusView
from users.views import UserListView,SearchUserView
urlpatterns = [
    url(r'RequirementList$', RequirementListView.as_view(), name='RequirementList'),
    url(r'AddRequirement$', AddRequirementView.as_view(), name='AddRequirement'),
    url(r'ModifyRequirement/(?P<requirement_id>.*)/$', ModifyRequirementView.as_view(), name='ModifyRequirement'),
    url(r'RequirementDetail/(?P<requirement_id>.*)/$', RequirementDetailView.as_view(), name='RequirementDetail'),
    url(r'DelRequirement$', DelRequirementView.as_view(), name='DelRequirement'),
    url(r'MyRequireList$', MyRequirementListView.as_view(), name='MyRequireList'),
    url(r'SearchMyRequirement$', SearchMyRequirementView.as_view(), name='SearchMyRequirement'),
    url(r'RequirementMonitor$', RequirementMonitorView.as_view(), name='RequirementMonitor'),
    url(r'ChangeRequirementStatus$', ChangeRequirementStatusView.as_view(), name='ChangeRequirementStatus'),

]
