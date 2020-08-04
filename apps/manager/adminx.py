# -*- coding: utf-8 -*-
__author__ = 'bobby'
__date__ = '2016/10/25 21:07'
from xadmin import views

import xadmin

from .models import ProjectInfo,VersionInfo,DepartmentInfo

class ProjectInfoAdmin(object):
    list_display = ['project_name', 'project_desc', 'add_time']
    search_fields = ['project_name', 'project_desc']
    list_filter = ['project_name', 'project_desc', 'add_time']
    model_icon = 'fa fa-university'
    relfield_style = 'fk-ajax'



class VersionInfoAdmin(object):
    list_display = ['version_name', 'get_project','version_desc', 'add_time']
    search_fields = ['version_name', 'belong_project__project_name','version_desc']
    list_filter = ['version_name', 'belong_project__project_name']
    model_icon = 'fa fa-university'
    relfield_style = 'fk-ajax'

#获取外键对应的名称
    def get_project(self, obj):
        return '%s' % obj.belong_project.project_name
    get_project.short_description = '所属项目'

class DepartmentInfoAdmin(object):
    list_display = ['name','get_name', 'add_time']
    search_fields = ['name','parent__name']
    list_filter = ['name','parent__name']
    model_icon = 'fa fa-user-md'
    relfield_style = 'fk-ajax'

    def get_name(self, obj):
        return '%s' % obj.parent.name
    get_name.short_description = '上级部门'

class GlobalSettings(object):
    site_title = '测试管理平台'
    site_footer = '测试管理平台'
    menu_style = 'accordion'  # 设置菜单可收缩,手风琴 accordion

class BaseSettings(object):
    enable_themes = True
    use_bootswatch = True# 一个主题插件


xadmin.site.register(views.BaseAdminView, BaseSettings)
xadmin.site.register(views.CommAdminView, GlobalSettings)

xadmin.site.register(ProjectInfo, ProjectInfoAdmin)
xadmin.site.register(VersionInfo, VersionInfoAdmin)
xadmin.site.register(DepartmentInfo, DepartmentInfoAdmin)
