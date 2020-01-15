from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.contrib.auth.models import Group


class PermissionAdmin(admin.ModelAdmin):
    fields = ['name', 'content_type', 'codename']
    list_display = ['name', 'content_type', 'codename']
    list_per_page = 20
    search_fields = ('name', 'codename')


admin.site.register(Permission, PermissionAdmin)
admin.site.unregister(User)
admin.site.unregister(Group)
