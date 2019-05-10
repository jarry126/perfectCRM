from kingadmin.baseadmin import baseKingadmin


class AdminSite(object):
    """注册"""
    def __init__(self):
        self.enable_admin = {

        }

    def register(self, model_class, admin_class=None):
        # app_name是各个App的名字，model_name是表的名字
        app_name = model_class._meta.app_label
        model_name = model_class._meta.model_name
        # 对admin_class进行实例化，不然None是不能进行  admin_class.model = model_class

        if not admin_class:
            admin_class = baseKingadmin()
        else:
            admin_class = admin_class()

        admin_class.model = model_class
        if app_name not in self.enable_admin:
            self.enable_admin[app_name] = {}
        self.enable_admin[app_name][model_name] = admin_class


site = AdminSite()
