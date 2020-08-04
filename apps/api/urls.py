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
from api.views import EnvListView,AddEnvView,ModifyEnvView,DelEnvView,GlobalParameterListView,AddGlobalParameterView\
    ,DelGlobalParameterView,ModifyGlobalParameterView,ApiCaseListView,DelApiCaseView,AddApiCaseView,ModifyApiCaseView,\
    OperationListView,AddOperationView,ModifyOperationView,DelOperationView,RunSingleCaseView, RunAllCaseView, \
    RunApiResultListView, SingleResultDetailView, RunApiPlanInfoView, DelRunApiPlanView



urlpatterns = [
    # 环境列表
    url(r'EnvList$', EnvListView.as_view(), name='EnvList'),
    url(r'AddEnv$', AddEnvView.as_view(), name='AddEnv'),
    url(r'ModifyEnv/(?P<env_id>.*)/$', ModifyEnvView.as_view(), name='ModifyEnv'),
    url(r'DelEnv$', DelEnvView.as_view(), name='DelEnv'),
    # 全局参数url
    url(r'GlobalParameterList$', GlobalParameterListView.as_view(), name='GlobalParameterList'),
    url(r'AddGlobalParameter$', AddGlobalParameterView.as_view(), name='AddGlobalParameter'),
    url(r'DelGlobalParameter$', DelGlobalParameterView.as_view(), name='DelGlobalParameter'),
    url(r'ModifyGParam/(?P<param_id>.*)/$', ModifyGlobalParameterView.as_view(), name='ModifyGParam'),
    # API接口用例
    url(r'ApiCaseList$', ApiCaseListView.as_view(), name='ApiCaseList'),
    url(r'DelApiCase$', DelApiCaseView.as_view(), name='DelApiCase'),
    url(r'AddApiCase$', AddApiCaseView.as_view(), name='AddApiCase'),
    url(r'ModifyApiCase/(?P<api_id>.*)/$', ModifyApiCaseView.as_view(), name='ModifyApiCase'),

    #前后置操作
    url(r'OperationList$', OperationListView.as_view(), name='OperationList'),
    url(r'AddOperation$', AddOperationView.as_view(), name='AddOperation'),
    url(r'DelOperation$', DelOperationView.as_view(), name='DelOperation'),
    url(r'ModifyOperation/(?P<opt_id>.*)/$', ModifyOperationView.as_view(), name='ModifyOperation'),
    # 运行单个用例
    url(r'RunSingleCase/$', RunSingleCaseView.as_view(), name='RunSingleCase'),

    url(r'RunAllCase/$', RunAllCaseView.as_view(), name='RunAllCase'),

    url(r'RunApiResultList/$', RunApiResultListView.as_view(), name='RunApiResultList'),
    url(r'SingleResultDetail/$', SingleResultDetailView.as_view(), name='SingleResultDetail'),
    url(r'RunApiPlanInfo/$', RunApiPlanInfoView.as_view(), name='RunApiPlanInfo'),
    url(r'DelRunApiPlan/$', DelRunApiPlanView.as_view(), name='DelRunApiPlan'),

]
