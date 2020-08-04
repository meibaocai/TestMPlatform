# -*- coding: utf-8 -*-
__author__ = 'bobby'
__date__ = '2016/10/25 21:07'

import xadmin
from xadmin import views
from xadmin.plugins.auth import UserAdmin
from xadmin.layout import Fieldset, Main, Side, Row

from .models import EmailVerifyRecord,UserProfile
import xadmin

from .models import UserProfile

class UserProfileAdmin(object):
    list_display = ['username','belong_department__name','birday', 'gender', 'address', 'birday', 'mobile', 'add_time']
    search_fields = ['address', 'birday', 'mobile']
    list_filter = ['belong_department', 'username', 'birday', 'gender', 'address', 'birday', 'mobile', 'add_time']
    model_icon = 'fa fa-university'

# xadmin.site.register(UserProfile, UserProfileAdmin)



