from django.template import Library
from django.utils.safestring import mark_safe
register = Library()
import time,datetime


@register.simple_tag
# <select></select>
def build_filter_ele(filter_column, admin_class):
    # 得到表里面filter_column这一队列  column_obj
    column_obj = admin_class.model._meta.get_field(filter_column)

    try:
        filter_ele = '<select name="%s">' % filter_column
        for choice in column_obj.get_choices():
            selected = ''
            print('test', admin_class.filter_conditions)
            if filter_column in admin_class.filter_conditions:
                if str(choice[0]) == admin_class.filter_conditions.get(filter_column):
                    selected = 'selected'
            option = '<option value="%s" %s>%s</option>' % (choice[0], selected, choice[1])
            filter_ele += option

    except AttributeError as e:
        """时间的表示和其他的都不相同"""
        filter_ele = "<select name='%s__gte'>" % filter_column

        if column_obj.get_internal_type() in ('DateField','DateTimeField'):
            time_obj = datetime.datetime.now()
            time_list = [['', '........'],
                         [time_obj, 'Today'],
                         [time_obj - datetime.timedelta(7), '七天内'],
                         [time_obj.replace(day=1), '本月'],
                         [time_obj - datetime.timedelta(90), '三个月内'],
                         [time_obj.replace(day=1, month=1), 'YearToDay'],
                         ['', 'ALL'],
                         ]
            # print('time_list:', time_list)

            for i in time_list:
                selected = ''
                time_to_str = '' if not i[0] else '%s-%s-%s' % (i[0].year, i[0].month, i[0].day)
                if "%s__gte" % filter_column in admin_class.filter_conditions:
                    if time_to_str == admin_class.filter_conditions.get("%s__gte" % filter_column):
                        selected = 'selected'
                option = "<option value='%s' %s>%s</option>" % (time_to_str, selected, i[1])
                filter_ele += option
    filter_ele += '</select>'
    return mark_safe(filter_ele)


@register.simple_tag
def build_table_row(obj,admin_class, model_name):
    ele = ""
    # 过滤删选
    if admin_class.list_display:
        for index, column_name in enumerate(admin_class.list_display):
            column_obj = admin_class.model._meta.get_field(column_name)
            if column_obj.choices:
                # choices的作用就是把字段都显示下拉列表
                column_date = getattr(obj,'get_%s_display' % column_name)()
            else:
                column_date = getattr(obj, column_name)
            td_ele = "<td>%s</td>" % (column_date)
            if index == 0:
                td_ele = "<td><a href='%s/%s/change/'>%s</a></td>" % (model_name, obj.id, column_date)
            ele += td_ele
    else:
        td_ele = "<td><a href='%s/%s/change/'>%s</a></td>" % (model_name, obj.id, obj)

        ele += td_ele

    return mark_safe(ele)


@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.model_name.upper()


@register.simple_tag
def render_paginator(queryset, admin_class, sort_column):
    ele = """<ul class = 'pagination'>"""
    for i in queryset.paginator.page_range:
        active = ''
        filter_ele = render_filtered_args(admin_class)
        if abs(queryset.number - i) < 2:
            sort_ele = ''
            if sort_column:
                sort_ele = '&_o=%s' % list(sort_column.values())[0]
            if queryset.number == i:
                active = 'active'
            p_ele = '<li class="%s"><a href="?_page=%s%s%s">%s</a></li>' % (active, i, filter_ele, sort_ele, i)
            ele += p_ele
    ele += """</ul>"""
    return mark_safe(ele)


@register.simple_tag
def get_sorted_column(column, sort_column, forloop):
    # 对排序进行操作
    if column in sort_column:
        last_sort_column = sort_column[column]

        if last_sort_column.startswith('-'):
            this_time_current_sort = last_sort_column.strip('-')
        else:
            this_time_current_sort = '-%s' % last_sort_column
        return this_time_current_sort
    else:
        return forloop


@register.simple_tag
def render_sorted_arrow (column, sorted_column):
    if column in sorted_column:
        last_sort_column = sorted_column[column]

        if last_sort_column.startswith('-'):
            arrow_direction = 'bottom'
        else:
            arrow_direction = 'top'
        ele = '''<span class="glyphicon glyphicon-triangle-%s" aria-hidden="true"></span>''' % arrow_direction

        return mark_safe(ele)
    else:
        return ''


@register.simple_tag
def render_filtered_args(admin_class, render_html=True):
    if admin_class.filter_conditions:
        ele = ''
        for k, v in admin_class.filter_conditions.items():
            ele += '&%s=%s' % (k, v)
        if render_html:
            return mark_safe(ele)
        else:
            return ele
    else:
        return ''


@register.simple_tag
def get_current_sorted_column_index(sorted_column) :
    if sorted_column:
        return list(sorted_column.values())[0]
    else:
        return ''


@register.simple_tag
def get_model_name(admin_class):
    """得到表的名字"""
    return admin_class.model._meta.model_name.upper()


@register.simple_tag
def get_obj_filed (form_obj, field):
    return getattr(form_obj.instance, field)


@register.simple_tag
def get_available_m2m_date(field_name, admin_class, form_obj):
    """通过一个字段，得到它关联的表的数据(m2m)"""
    field_obj = admin_class.model._meta.get_field(field_name)
    # 两个queryset相减，需要在各自的前面加上set
    obj_list = set(field_obj.related_model.objects.all())
    selected_date = set(getattr(form_obj.instance, field_name).all())  # 这里的selected_date是jquery对象

    return obj_list - selected_date


@register.simple_tag
def get_selected_m2m_data (field_name, admin_class, form_obj):
    """得到一行数据的某个字段的值，用getattr反射来做"""
    selected_date = getattr(form_obj.instance, field_name).all()  # 这里的selected_date是jquery对象
    # 因为add和select是2个页面，add中没有instance,所以需要做一个判断
    if selected_date:
        return selected_date
    else:
        return ''


@register.simple_tag
def display_all_related_objs(obj):
    ele = '<ul>'
    """obj._meta.related_objects得到所有 对  obj行数据 关联的 一对多、多对多表"""
    for reversed_find_obj in obj._meta.related_objects:   # reversed_find_obj是一个个表对象
        reversed_model_name = reversed_find_obj.name        # reversed_model_name是表对象的名字
        ele += "<li>%s3333<ul> " % reversed_model_name     # ul是块级元素，所以会往下排

        related_lookup_key = '%s_set' % reversed_model_name   # 反向查找需要  表名_set
        reversed_model_obj_content = getattr(obj, related_lookup_key).all()  # reversed_model_obj_content 里面是反向表的所有 行数据集合


        if reversed_find_obj.get_internal_type == 'ManyToManyField':  # 通过一张表，可以判断出里面有么有多对多(get_internal_type)
            for i in reversed_model_obj_content:
                ele += "<li><a href='/kingadmin/%s/%s/%s/change/'>%s</a> 记录里与[%s]相关的的数据将被删除</li>" \
                       % (i._meta.app_label, i._meta.model_name, i.id, i, obj)  # i(一行数据), i._meta.app_label可以得到\
                # 这行数据的app，i._meta.model.name可以得到这行数据表的名字。

        else:
            for i in reversed_model_obj_content:
                ele += '<li><a href="/kingadmin/%s/%s/%s/change">%s</a></li>' % (i._meta.app_label, i._meta.model_name, i.id, i)
                ele += display_all_related_objs(i)
        ele += "</ul></li>"
    ele += "</ul>"
    return mark_safe(ele)


@register.simple_tag
def get_model_verbose_name(admin_class):
    return admin_class.model._meta.verbose_name


from crm import models
@register.simple_tag
def helplessaction():
    crm_obj_all = models.Menus.objects.all()
    return crm_obj_all



