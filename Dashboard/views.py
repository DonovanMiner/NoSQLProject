from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from NoSQLProject.utils import user_fitness_data, users

import plotly.graph_objects as go
import pandas as pd

def default_dashboard(request):
    
    context = {}

    return HttpResponse(render(request, 'Dashboard/default_dashboard.html', context))



def user_dashboard(request):
    
    #get username/password and check it in database
    #query u_id from u_nmae, pwd, put in context

    u_name = request.POST.get('username')
    password = request.POST.get('password')
    #print(f'UNAME CHECK: {type(u_name)} {u_name}')
    #print(f'PASSWORD CHECK: {type(password)} {password}')

    u_id = users.find_one({"u_name" : u_name, "password" : password}, {"_id" : 0, "user_id" : 1})
    #print(f'U_ID CHECK: {type(u_id)} {u_id}')
    
    #starting here, process to be put into a function call to create graphs
    df_1 = user_fitness_data.find({"user_id" : u_id['user_id'], "workout_type" : "Cycling"}).sort({"date" : -1})
    df_1 = [(doc['date'], doc['distance_km'], doc['active_minutes']) for doc in df_1] 
    df_1 = pd.DataFrame(df_1)
    df_1[1] = df_1[1] / (df_1[2]/60)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_1[0], y=df_1[1]))
    fig.update_layout(title=f'User {u_name} Cycling')
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Km/Hr')
    fig = fig.to_html()
    #ending here
    
    #print(f'DATA QUERY CHECK: {type(df_1)} {df_1}')

    context = {"u_id" : u_id, "fig" : fig}
    
    return HttpResponse(render(request, 'Dashboard/user_dashboard.html', context))