from django.shortcuts import render
import json
class baseKingadmin(object):
    def __init__(self):
        self.actions.extend(self.default_actions)

    list_display = []
    list_filter = []
    search_fields = []
    list_per_page = 20
    default_actions = ['delete_selected_objs']
    actions = []

# 当选中actions里面的 delete_selected_objs的时候，执行函数
    def delete_selected_objs(self, request, querysets):
        selected_id_list = json.dumps([i.id for i in querysets] )# 得到querysets里面所有的id
        return render(request, 'kingadmin/delete_obj.html', {'admin_class': self, 'objs': querysets,'selected_id_list': selected_id_list, })
