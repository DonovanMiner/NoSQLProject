from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from pymongo import client_session
from NoSQLProject.utils import user_fitness_data, users

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import ast


def GetQuery(u_id, workout_type, metrics):
    
    print(f'GET QUERY DEBUG:\nWorkout: {workout_type}\nMetrics: {metrics}\n')
    df = user_fitness_data.find({"user_id" : u_id['user_id'], "workout_type" : workout_type}).sort({"date" : -1})
    df = [(doc['date'], doc[metrics[0]]) for doc in df] #add if statement for additional metrics in list, make metrics[0] x-axis/values other than date 
    df = pd.DataFrame(df)
    #df[1] = df[1] / (df[2]/60)
    print(f'GET QUERY DATAFRAME CHECK:\n {df}')

    return df

def RenderPlot(u_id, u_name, workout_type, metrics):
    
    df = GetQuery(u_id, workout_type, metrics)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[0], y=df[1]))
    fig.update_layout(title=f'{u_name} {workout_type}')
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title=f'{metrics[0]}')
    fig = fig.to_html()
    
    return fig



def default_dashboard(request):
    
    context = {}

    return HttpResponse(render(request, 'Dashboard/default_dashboard.html', context))



def user_dashboard(request):
    
    #get username/password and check it in database
    #query u_id from u_nmae, pwd, put in context

    u_name = request.POST.get('username')
    password = request.POST.get('password')
    u_id = users.find_one({"u_name" : u_name, "password" : password}, {"_id" : 0, "user_id" : 1})
    print(f'U_ID CHECK: {type(u_id)} {u_id}')
    print(f'UNAME CHECK: {type(u_name)} {u_name}')
    print(f'PASSWORD CHECK: {type(password)} {password}')
   
    request.session['u_name'] = u_name
    request.session['u_id'] = u_id

    init_workout_type = "Walking" 
    init_metric = ["active_minutes"]
    
    fig1 = RenderPlot(u_id, u_name, init_workout_type, init_metric)
    fig2 = RenderPlot(u_id, u_name, init_workout_type, init_metric)
    fig3 = RenderPlot(u_id, u_name, init_workout_type, init_metric)
    fig4 = RenderPlot(u_id, u_name, init_workout_type, init_metric)
    
    request.session['fig1'] = fig1
    request.session['fig2'] = fig2
    request.session['fig3'] = fig3
    request.session['fig4'] = fig4
    
    context = {"u_id" : u_id, "u_name" : u_name, "fig1" : fig1, "fig2" : fig2, "fig3" : fig3, "fig4" : fig4}
    
    return HttpResponse(render(request, 'Dashboard/user_dashboard.html', context))



def update_user_dashboard(request):
    
    #form info
    # u_id = request.POST.get('u_id')
    # u_id = ast.literal_eval(u_id)
    # u_name = request.POST.get('u_name')
    #print(f'U_ID UPDATE CHECK: {type(u_id)} {u_id}')
    
    #session info
    u_name = request.session.get('u_name')
    u_id = request.session.get('u_id')

    fig1, fig2, fig3, fig4 = '', '', '', ''
    workout_type_1, workout_type_2, workout_type_3, workout_type_4 = '', '', '', ''
    metric_1, metric_2, metric_3, metric_4 = ([] for i in range(4))

    #get rest of info to query with
    #need function to query data, return data frame to be passed to render graph
    #put metrics into a list? 1st x-axis, 2nd y-axis, 3rd optional this per that
    if (request.method == "POST"):
        workout_type_1 = request.POST.get('workout_type_1')
        workout_type_2 = request.POST.get('workout_type_2')
        workout_type_3 = request.POST.get('workout_type_3')
        workout_type_4 = request.POST.get('workout_type_4')

        metric_1.append(request.POST.get('metric_1_1')) 
        metric_2.append(request.POST.get('metric_2_1'))
        metric_3.append(request.POST.get('metric_3_1'))
        metric_4.append(request.POST.get('metric_4_1'))
        print(f'FORM CHECK: {metric_1}')
        
        fig1 = RenderPlot(u_id, u_name, workout_type_1, metric_1)
        fig2 = RenderPlot(u_id, u_name, workout_type_2, metric_2)
        fig3 = RenderPlot(u_id, u_name, workout_type_3, metric_3)
        fig4 = RenderPlot(u_id, u_name, workout_type_4, metric_4)
 
        request.session['fig1'] = fig1
        request.session['fig2'] = fig2
        request.session['fig3'] = fig3
        request.session['fig4'] = fig4
        
    else:
        fig1 = request.session.get('fig1')
        fig2 = request.session.get('fig2')
        fig3 = request.session.get('fig3')
        fig4 = request.session.get('fig4')
       
    

    context = {"u_id" : u_id, "u_name" : u_name, "fig1" : fig1, "fig2" : fig2, "fig3" : fig3, "fig4" : fig4}

    return HttpResponse(render(request, 'Dashboard/user_dashboard.html', context))


def update_workout(request):
   
    u_name = request.session.get('u_name')
    u_id = request.session.get('u_id')
    print(f'U_ID CHECK: {type(u_id)} {u_id}')
    print(f'UNAME CHECK: {type(u_name)} {u_name}')


    context = {"u_id" : u_id, "u_name" : u_name}
    
    return HttpResponse(render(request, 'Dashboard/update_workout.html', context))

