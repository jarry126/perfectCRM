#!/usr/bin/env python
# -*- coding:utf-8 -*-
from crm import models
from django.forms import ModelForm
"""创建一个动态的ModelForm表"""


class TestModel(ModelForm):
    """这是一个固定的生成ModelForm表"""
    class Meta:
        model = models.CustomerInfo
        fields = '__all__'


def create_dynamic_model_form(admin_class, form_add=False):
    """创建一个动态的ModelForm表"""
    """form_add=False时候表示修改，form_add=True的时候表示添加"""
    class Meta:
        model = admin_class.model
        fields = '__all__'
        if not form_add:
            exclude = admin_class.readonly_fields
            admin_class.form_add = False
        else:
            admin_class.form_add = True
    """这里的__new__是给所有的字段对象，添加一个class属性"""
    def __new__(cls, *args, **kwargs):
        print("__new__",cls,args,kwargs)
        for field_name in cls.base_fields:
            filed_obj = cls.base_fields[field_name]
            filed_obj.widget.attrs.update({'class':'form-control'})
        return ModelForm.__new__(cls)
    dynamic_form = type("DynamicModelForm", (ModelForm,), {'Meta': Meta, '__new__': __new__})
    return dynamic_form
