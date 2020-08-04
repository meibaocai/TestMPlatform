import xadmin
from mptt.admin import MPTTModelAdmin
from .models import TestCase


class CaseInfoAdmin(object):
    list_display = ['name', 'get_parent_area', 'level']
    search_fields = ['name']
    list_filter = ['name']
    model_icon = 'fa fa-university'
    relfield_style = 'fk-ajax'

#获取外键对应的名称
    def get_parent_area(self, obj):
        return '%s' % obj.case_name
    get_parent_area.short_description = '父目录'

xadmin.site.register(TestCase, CaseInfoAdmin)
