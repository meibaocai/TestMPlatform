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
# ÒýÈë»º´æ
# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import cache_page
from case.views import CaseListView,AddCaseView,ModifyCaseView,DelCaseView,VersionCaseListView,\
    AddVersionCaseView,ModifyVersionCaseView,DelVersionCaseView,TestCaseSuitListView,AddTestCaseSuitView,\
    ModifyTestCaseSuitView,MyTestCaseSuitListView,MyTestCaseSuitDetailView,SuitCaseDetailView,\
    DelTestCaseSuitListView,StopTestCaseSuitListView,ChangeSuitCaseStatusView,ChangeSuitCaseDetailView,TestCaseSuitMonitorView\
    ,XMindCaseListView,AddXMindCaseView,ModifyXMindCaseView,XMindCaseDetailView,DelXMindCaseView,SearchXMindCaseView,IntoProductCaseView
urlpatterns = [
    url(r'CaseList$', CaseListView.as_view(), name='CaseList'),
    url(r'AddCase$', AddCaseView.as_view(), name='AddCase'),
    url(r'ModifyCase$', ModifyCaseView.as_view(), name='ModifyCase'),
    url(r'DelCase$', DelCaseView.as_view(), name='DelCase'),
    url(r'VersionCList$', VersionCaseListView.as_view(), name='VersionCList'),
    url(r'AddVersionCase$', AddVersionCaseView.as_view(), name='AddVersionCase'),
    url(r'IntoProductCase$', IntoProductCaseView.as_view(), name='IntoProductCase'),
    url(r'ModifyVersionCase$', ModifyVersionCaseView.as_view(), name='ModifyVersionCase'),
    url(r'DelVersionCase$', DelVersionCaseView.as_view(), name='DelVersionCase'),
    url(r'TestCaseSuitList$', TestCaseSuitListView.as_view(), name='TestCaseSuitList'),
    url(r'AddSuit$', AddTestCaseSuitView.as_view(), name='AddSuit'),
    url(r'ModifySuit/(?P<suit_id>.*)/$', ModifyTestCaseSuitView.as_view(), name='ModifySuit'),
    url(r'MySuitList$', MyTestCaseSuitListView.as_view(), name='MySuitList'),
    url(r'CaseSuitDetail/(?P<suit_id>.*)/$', MyTestCaseSuitDetailView.as_view(), name='CaseSuitDetail'),
    url(r'SuitCaseDetail', SuitCaseDetailView.as_view(), name='SuitCaseDetail'),
    url(r'DelSuit$', DelTestCaseSuitListView.as_view(), name='DelSuit'),
    url(r'StopSuit', StopTestCaseSuitListView.as_view(), name='StopSuit'),
    url(r'ChangeCaseStatus', ChangeSuitCaseStatusView.as_view(), name='ChangeCaseStatus'),
    url(r'ChangeCaseDetail', ChangeSuitCaseDetailView.as_view(), name='ChangeCaseDetail'),
    url(r'TestCaseSuitMonitor$', TestCaseSuitMonitorView.as_view(), name='TestCaseSuitMonitor'),
    url(r'XMCList$', XMindCaseListView.as_view(), name='XMCList'),
    url(r'AddXMindCase$', AddXMindCaseView.as_view(), name='AddXMindCase'),
    url(r'ModifyXMindCase/(?P<XMindCase_id>.*)/$', ModifyXMindCaseView.as_view(), name='ModifyXMindCase'),
    url(r'XMindCaseDetail/(?P<XMindCase_id>.*)/$', XMindCaseDetailView.as_view(), name='XMindCaseDetail'),
    url(r'DelXMind$', DelXMindCaseView.as_view(), name='DelXMind'),
    url(r'SearchXMind$', SearchXMindCaseView.as_view(), name='SearchXMind'),

]
