from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout


def acc_login(request):
    """登录验证"""
    error_msg = ''
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            print('request.user:', request.user)
            return redirect(request.GET.get('next', '/'))
        else:
            error_msg = 'Error Username or Password'

    return render(request, 'login.html', {'error_msg': error_msg})


def acc_logout(request):
    logout(request)
    return redirect('/login')
