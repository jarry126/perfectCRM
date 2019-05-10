from kingadmin.sites import site
from . import models
from kingadmin.baseadmin import baseKingadmin


class CustomerAdmin(baseKingadmin):
    list_display = ['name','source','contact_type','contact','consultant','consult_content','status', 'date']
    list_filter = ['source','consultant','status', 'date']
    search_fields = ['contact','consultant__name']
    filter_horizontal = ['consult_courses', ]


site.register(models.Test, CustomerAdmin)

