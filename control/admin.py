from atexit import register
from django.contrib import admin
from control.models import *

admin.site.register(Region)
admin.site.register(UserTag)
admin.site.register(Tag)
admin.site.register(UserProfile)