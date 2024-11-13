from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from NoSQLProject.utils import user_fitness_data

def default_dashboard(request):
    
    context = {}

    return HttpResponse(render(request, 'Dashboard/default_dashboard.html', context))



def user_dashboard(request):
    
    #get username/password and check it in database
    #query u_id from u_nmae, pwd, put in context

    u_name = request.POST.get('username')
    password = request.POST.get('password')
    print(f'UNAME CHECK: {type(u_name)} {u_name}')
    print(f'PASSWORD CHECK: {type(password)} {password}')


    u_id = user_fitness_data.find({"u_name" : u_name, "password" : password})
    context = {"u_id" : u_id}
    print(f'U_ID CHECK: {type(u_id)} {u_id}')
    
    return HttpResponse(render(request, 'Dashboard/user_dashboard.html', context))