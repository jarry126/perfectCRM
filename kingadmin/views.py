from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from . import app_setup
from . import form_handle
from django.db.models import Q
from kingadmin.sites import site
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
app_setup.kingadmin_auto_discover()
import json
print(site)


@login_required
def app_index(request):
    return render(request, 'kingadmin/app_index.html', {'site': site})


def get_filter_result(request, queryset):
    filter_conditions = {}
    condition = request.GET
    for k, v in condition.items():
        if k in ('_page', '_o', '_q'): continue
        if v:
            filter_conditions[k] = v
    return queryset.filter(**filter_conditions), filter_conditions


def get_sorted_result(request, queryset, admin_class):
    current_sold_column = {}
    order_index = request.GET.get('_o')
    if order_index:
        order_key = admin_class.list_display[abs(int(order_index))]
        current_sold_column[order_key] = order_index
        if order_index.startswith('-'):
            order_key = '-' + order_key
        queryset = queryset.order_by(order_key)
        return queryset, current_sold_column
    else:
        return queryset, current_sold_column


def get_serached_result(request, queryset, admin_class):
    search_key = request.GET.get('_q')
    if search_key:
        q = Q()
        q.connector = 'OR'
        for search_filed in admin_class.search_fields:
            q.children.append(('%s__contains' % search_filed, search_key))
        return queryset.filter(q)
    return queryset


@login_required
def table_obj_list(request, app_name, model_name):
    admin_class = site.enable_admin[app_name][model_name]

    print('......', admin_class)

    queryset = admin_class.model.objects.all().order_by('-id')
# 判断是不是post类型(actions)
    if request.method == 'POST':
        selected_action = request.POST.get('action')  # action是actions里面的某个字符串
        selected_id_list = json.loads(request.POST.get('selected_id_list'))  # 被选中的CheckBox的这一行的id列表

        if not selected_action: # 如果不为真，就是没有action，多数据delete的POST请求
            print('.............................')
            if selected_id_list:
                admin_class.model.objects.filter(id__in=selected_id_list).delete()
        else:
            seleted_objs = admin_class.model.objects.filter(id__in=selected_id_list)
            admin_action_func = getattr(admin_class, selected_action)  # 这是一个函数对象
            response = admin_action_func(request, seleted_objs)
            if response:    # 如果返回的是一个页面，那么将会跳转到那个页面
                return response
# 过滤程序
    print(request.GET)
    queryset, filter_conditions = get_filter_result(request, queryset)
# 搜索
    queryset = get_serached_result(request, queryset, admin_class)
    admin_class.search_key = request.GET.get('_q', '')
# 排序
    queryset, sort_column = get_sorted_result(request, queryset, admin_class)
# 这里是分页
    paginator = Paginator(queryset, admin_class.list_per_page)  # Show 25 contacts per page
    page = request.GET.get('_page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    admin_class.filter_conditions = filter_conditions
    # print('111111111111:', admin_class_filter_conditions)
    return render(request, 'kingadmin/mtable_obj_list.html', {'queryset': queryset, 'admin_class': admin_class, 'sort_column': sort_column, 'model_name': model_name})


def acc_login(request):
    """登录验证"""
    error_msg = ''
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            # 如果用户名和密码正确就登录这个用户
            login(request, user)
            print('request.user:', request.user)
            return redirect(request.GET.get('next', '/kingadmin'))
        else:
            error_msg = 'Error Username or Password'

    return render(request, 'kingadmin/login.html', {'error_msg': error_msg})


def acc_logout(request):
    logout(request)
    return redirect('/kingadmin/login')


def table_obj_change(request, app_name, model_name, obj_id):
    """修改一行数据add"""
    # forms = form_handle.TestModel()

    admin_class = site.enable_admin[app_name][model_name]
# admin_class.model在site这个我们自定义的模块里面被设置成admin_class.model = model（就是等于表）
    obj = admin_class.model.objects.get(id=obj_id)
    model_form = form_handle.create_dynamic_model_form(admin_class)
    if request.method == 'GET':
        form_obj = model_form(instance=obj)
    elif request.method == 'POST':
        form_obj = model_form(instance=obj, data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/kingadmin/%s/%s' % (app_name, model_name))

    return render(request, 'kingadmin/table_obj_change.html', locals())


def table_obj_add(request, app_name, model_name):
    """添加一行数据add"""
    admin_class = site.enable_admin[app_name][model_name]
    # admin_class.model在site这个我们自定义的模块里面被设置成admin_class.model = model（就是等于表）
    model_form = form_handle.create_dynamic_model_form(admin_class, form_add=True)
    if request.method == 'GET':
        form_obj = model_form()
    elif request.method == 'POST':
        form_obj = model_form(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/kingadmin/%s/%s' % (app_name, model_name))
    """
    因为model_form里面没有实例化一个一行数据，所以model_form是字段对象(自己想的，所有的字段)，
    而不能拿到from_obj.instance(得到一行数据的返回值)，因为根本就没有这个
    """
    return render(request, 'kingadmin/table_obj_add.html', locals())


def obj_delete(request, app_name, model_name, from_obj_instance_id):
    """删除操作"""

    admin_class = site.enable_admin[app_name][model_name]
    obj = admin_class.model.objects.get(id=from_obj_instance_id)

    if request.method == 'POST':
        obj.delete()
        return redirect('/kingadmin/{app_name}/{model_name}'.format(app_name=app_name, model_name=model_name))
    return render(request, 'kingadmin/delete_obj.html', locals())
