from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import State, Transition, Workflow, HotUpdateTemplate, HotUpdateTemplateItems


class WorkflowAdmin(admin.ModelAdmin):
    fields = ['name', 'describtion', 'init_state', 'allow_users', 'workflow_type']
    list_display = ['name', 'describtion', 'init_state', 'workflow_type']


class StateAdmin(admin.ModelAdmin):
    fields = ['name', 'workflow', 'transition', 'specified_users']
    list_display = ['name', 'workflow']


class TransitionAdmin(admin.ModelAdmin):
    fields = ['name', 'workflow', 'destination', 'condition']
    list_display = ['name', 'workflow', 'destination', 'condition']


class HotUpdateTemplatesItemsAdmin(admin.TabularInline):

    def image_data(self, obj):
        image_url = obj.image.url[4:]
        return mark_safe(u'<a href="%s" target="_blank"><img src="%s" width="100px" /></a>' % (image_url, image_url))

    model = HotUpdateTemplateItems
    extra = 0
    fieldsets = [
        (None, {'fields': ['image', 'image_data']}),
    ]
    list_display = ('image', 'image_data')
    list_per_page = 20
    readonly_fields = ('image_data',)
    image_data.short_description = u'预览'


class HotUpdateTemplatesAdmin(admin.ModelAdmin):
    fields = ['name', 'tag', 'type', 'remark']
    list_display = ['name', 'tag', 'type', 'remark']
    inlines = [HotUpdateTemplatesItemsAdmin]
    exclude = ('template',)
    list_filter = ('type',)
    search_fields = ('name', 'type', 'remark')
    ordering = ('name', 'type')


admin.site.register(State, StateAdmin)
admin.site.register(Transition, TransitionAdmin)
admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(HotUpdateTemplate, HotUpdateTemplatesAdmin)
