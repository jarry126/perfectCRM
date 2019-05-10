from kingadmin.sites import site
from . import models
from kingadmin.baseadmin import baseKingadmin


class CustomerAdmin(baseKingadmin):
    list_display = ['id', 'name','source','contact_type','contact','consultant','consult_content','status', 'date']
    list_filter = ['source','consultant','status', 'date']
    search_fields = ['contact','consultant__name']
    readonly_fields = ['status', 'contact']
    filter_horizontal = ['consult_courses', ]
    actions = ['change_status', ]

    def change_status(self, request, querysets):
        querysets.update(status=1)


site.register(models.CustomerInfo, CustomerAdmin)
site.register(models.Role)
site.register(models.Menus)
site.register(models.UserProfile)
site.register(models.Student)
site.register(models.CustomerFollowUp)
site.register(models.ClassList)
site.register(models.Branch)



