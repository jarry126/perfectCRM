# print(conf.settings.INSTALLED_APPS)
# ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'crm.apps.CrmConfig', 'kingadmin', 'students']
from django import conf


def kingadmin_auto_discover():
    """从各个app里面有kindadmin这个文件下面执行里面的程序"""
    for app_name in conf.settings.INSTALLED_APPS:
        try:
            mod = __import__('%s.kingadmin' % app_name)
            print(mod.kingadmin)
        except ImportError:

            pass
