from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from . import models
from . import forms
from django import conf
import os,json
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import datetime

@login_required
def dashboard(request):
    crm_obj_all = models.Menus.objects.all()
    return render(request, 'crm/dashboard.html', locals())


@login_required
def stu_enrollment(request):
    """生成学生报名链接的页面"""
    customers = models.CustomerInfo.objects.all()
    class_lists = models.ClassList.objects.all()

    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        class_grade_id = request.POST.get('class_grade_id')

        try:
            enrollment_obj = models.StudentEnrollment.objects.create(
                customer_id=customer_id,
                class_grade_id=class_grade_id,
                consultant_id=request.user.userprofile.id,  # request.user.userprofile.id
                #  这一条代码不是很理解
            )
        except Exception as e: # 不知道为什么不能用IntegrityError
            enrollment_obj = models.StudentEnrollment.objects.get(customer_id=customer_id,
                                                                  class_grade_id=class_grade_id,)
            if enrollment_obj.contract_agreed:
                return redirect('/crm/stu_enrollment/%s/contract_audit/' % enrollment_obj.id)

        enrollment_link = 'http://127.0.0.1:8002/crm/stu_enrollment/%s' % enrollment_obj.id
    return render(request, 'crm/stu_enrollment.html', locals())


def enrollment(request, enrollment_obj_id):
    """报名表"""
# 生成StudentEnrollment中的一条数据enrollment_obj
    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_obj_id)
# POST的时候，再生成一个新的表单
    if request.method == 'POST':
        print(request.POST)
        # 数据更新用data，后面跟一个字典, customer_form是一个报名表
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer, data=request.POST)
        if customer_form.is_valid():
            customer_form.save()
            # 当customer_form这个表提交成功之后，需要改变enrollment_obj的状态，并且保存
            enrollment_obj.contract_agreed = True
            enrollment_obj.contract_signed_date = datetime.now()
            enrollment_obj.save()
            return HttpResponse('这表示报名成功，状态信息已经改变!!!')
# 生成customer表单
    else:
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer)

    uploaded_files = []
    enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UPLOAD_DIR, enrollment_obj_id)
    if os.path.isdir(enrollment_upload_dir):
        uploaded_files = os.listdir(enrollment_upload_dir)

    return render(request, 'crm/enrollment.html', locals())


@csrf_exempt
def enrollment_fileupload(request, enrollment_obj_id):
    """必须要在上面加这个东西csrf_exempt是免认证的东西，文件过来的时候是POST请求"""
    # enrollment_upload_dir是一个目录(结尾是这个enrollment_obj_id)
    enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UPLOAD_DIR, enrollment_obj_id)
    # 如果不存在这个目录,创建
    if not os.path.isdir(enrollment_upload_dir):
        os.mkdir(enrollment_upload_dir)
    # 得到传过来的文件
    file_obj = request.FILES.get('file')

    # 将文件名加在目录下面, 判断目录下面列表是否小于2
    if len(os.listdir(enrollment_upload_dir)) <= 2:
        with open(os.path.join(enrollment_upload_dir, file_obj.name), "wb") as f:

            for chunks in file_obj.chunks():
                f.write(chunks)
    else:
        return HttpResponse(json.dumps({'status': False, 'err_msg': 'max upload limit is 2'}))
    return HttpResponse(json.dumps({'status': True}))


@login_required
def contract_audit(request, enrollment_obj_id):
    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_obj_id)
    if request.method == 'POST':
        # 表中进行数据更新的时候，只会找自己的字段的值，进行更新
        enrollment_form = forms.Enrollment(instance=enrollment_obj, data=request.POST)
        if enrollment_form.is_valid():
            enrollment_form.save()
            # 如果有Student有customer=enrollment_obj.customer这一行数据，就得到，没有就生成
            stu_obj = models.Student.objects.get_or_create(customer=enrollment_obj.customer)[0]
            # 为stu_obj这一行数据添加一个class_grades的值为enrollment_obj.class_grade_id
            stu_obj.class_grades.add(enrollment_obj.class_grade_id)
            stu_obj.save()
        # 改变customer表中的状态，变成已报名(1)    , 与老师不同的是，用enrollment_obj.customer.save()有用，而不是enrollment_obj.save()
            enrollment_obj.customer.status = 1
            enrollment_obj.customer.save()
            return redirect('/kingadmin/crm/customerinfo/%s/change/' % enrollment_obj.customer.id)
    else:
        # 得到enrollment一行数据的表
        enrollment_form = forms.Enrollment(instance=enrollment_obj)
        # 德奥customer一行数据的报表
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer)
    return render(request, 'crm/contract_audit.html', locals())