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
from django.urls import path
from django.conf.urls import url, include
from bugs.views import BugListView,MyBugListView,AddBugView,BugDetailView,ModifyBugView,DelBugView,SearchBugView

from django.contrib import admin
from django.views.generic import TemplateView
import xadmin
from django.views.static import serve
urlpatterns = [
    url(r'BugList$', BugListView.as_view(), name='BugList'),
    url(r'MyBugs$', MyBugListView.as_view(), name='MyBugs'),
    url(r'AddBug$', AddBugView.as_view(), name='AddBug'),
    url(r'ModifyBug/(?P<bug_id>.*)/$', ModifyBugView.as_view(), name='ModifyBug'),
    url(r'BugDetail/(?P<bug_id>.*)/$', BugDetailView.as_view(), name='BugDetail'),
    url(r'DelBug$', DelBugView.as_view(), name='DelBug'),
    url(r'SearchBug$', SearchBugView.as_view(), name='SearchBug'),

]
