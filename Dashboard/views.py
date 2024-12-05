from audioop import avg
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from pymongo import client_session
from bson.objectid import ObjectId
from NoSQLProject.utils import user_fitness_data, users

import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import ast


def FormatDate(date):

    month_lookup = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

    month, day, year = date.split(' ', 2)
    month = int(month_lookup[month])
    day = int(day)
    year = int(year)

    return datetime.datetime(year, month, day, 0, 0, 0)


def GetDateRenderQuery(u_id, workout_type, metrics):

    print(f'UID QUERY DEBUG: {type(u_id)} {u_id}')
    print(f'GET QUERY DEBUG:\nWorkout: {workout_type}\nMetrics: {metrics}\n')

    if (workout_type == 'All'):
        df = user_fitness_data.find(
            {"user_id": u_id['user_id']}).sort({"date": -1})
    else:
        df = user_fitness_data.find({"user_id": u_id['user_id'], "workout_type": workout_type}).sort(
            [("date", -1)])  # <---- change dict to a list of tuples

    if (len(metrics) == 1):
        # add if statement for additional metrics in list, make metrics[0] x-axis/values other than date
        df = [(doc['date'], doc[metrics[0]]) for doc in df]
        return pd.DataFrame(df)
        # df = pd.DataFrame(df)
        # df[1] = df[1] / (df[2]/60)
        # print(f'GET QUERY DATAFRAME CHECK:\n {df}')

    elif (len(metrics) == 2):
        df = user_fitness_data.find(
            {'user_id': u_id['user_id'], 'workout_type': workout_type}).sort({'date': -1})
        df = pd.DataFrame(
            [[doc['date'], doc[metrics[0]], doc[metrics[1]]] for doc in df])
        if (metrics[0] == 'active_minutes'):
            df[1] = df[1] / 60
        elif (metrics[1] == 'active_minutes'):
            df[2] = df[2] / 60
        print(f'DOUBLE METRICS CHECK:\n{df}')

        df[1] = df[1] / df[2]
        return df


def GetCountRenderQuery(u_id, workout_type, metrics):

    if (workout_type == 'All'):
        df = user_fitness_data.aggregate([{"$match": {"user_id": u_id['user_id']}}, {'$group': {
                                         '_id': f"${metrics[0]}", 'sumTotal': {'$sum': 1}}}, {"$sort": {'sumTotal': -1}}])
    else:
        df = user_fitness_data.aggregate([{"$match": {"user_id": u_id['user_id'], "workout_type": workout_type}}, {
                                         '$group': {'_id': f"${metrics[0]}", 'sumTotal': {'$sum': 1}}}, {"$sort": {'sumTotal': -1}}])

    df = pd.DataFrame(doc for doc in df)
    # print(f'DATAFRAME COUNT QUERY CHECK:\n{df}')
    return df


def RenderPlot(u_id, u_name, workout_type, metrics, agg_select):
    
    agg_name = {'date_agg' : 'Date', 'avg_agg' : '7 Day Average', 'count_agg' : 'Counts'}



    if (agg_select == 'date_agg'):
        df = GetDateRenderQuery(u_id, workout_type, metrics)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[0], y=df[1]))
        fig.update_layout(title=f'{u_name} Over Time for {
                          workout_type}, {metrics}')
        fig.update_xaxes(title='Date')
        fig.update_yaxes(title=f'{metrics[0]}')
        
        if (len(metrics) == 1):
            fig.update_layout(title=f'{workout_type} {metrics[0]} by {agg_name[agg_select]}')
        else:
            fig.update_layout(title=f'{workout_type} {metrics[0]} Per {metrics[1]} by {agg_name[agg_select]}')

        fig = fig.to_html()
        return fig

    elif (agg_select == 'count_agg'):
        df = GetCountRenderQuery(u_id, workout_type, metrics)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['_id'], y=df['sumTotal']))
        fig.update_layout(title=f'{u_name} Counts for {
                          workout_type}, {metrics}')
        fig.update_xaxes(title=f'{metrics[0]}')
        fig.update_yaxes(title='Counts')
        
        if(len(metrics) == 1):
            fig.update_layout(title=f'{workout_type} Counts for {metrics[0]}')
        else:
            fig.update_layout(title=f'{workout_type} Counts for {metrics[0]} Per {metrics[1]}')
            
        fig = fig.to_html()
        return fig
    
    elif(agg_select == 'avg_agg'):
        df = GetAverageRenderQuery(u_id, workout_type, metrics)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[0], y=df[1]))
        fig.update_xaxes(title='Date')
        fig.update_yaxes(title=f'{metrics[0]}')

        if(len(metrics) == 1):
            fig.update_layout(title=f'Weekly Average for {workout_type} {metrics[0]}')
        else:
            fig.update_layout(title=f'Weekly Average for {workout_type} {metrics[0]} Per {metrics[1]}')

        fig = fig.to_html()
        return fig


def GET_MOTIVATED(u_id, w1, w2, w3, w4, l1, l2, l3, l4):
    
    suggestions = []

    sugg_list = {'heart_rate_avg' : ['Keep working hard! Maintaing a good heartrate is the key to a good workout. Be sure to consult a physician on a healthy heart range to excersise in based on your age and current health.', 'Keep up the good work! Be sure to consult a physician on a healthy heart range to excersise in based on your age and current health.', 'Great job pushing yourself! Be sure to consult a physician on a healthy heart range to excersise in based on your age and current health.'], 
                 'active_minutes' : ['Keep at it! Exercising for 1-2 hours a day will keep you in good health!', 'Good job! You\'re keeping pace with yourself.', 'Good job! Working out for longer durations is a great way to improve cardiovascular health.'],
                 'sleep_hours' : ['Be sure to get enough sleep to recover from workouts!', 'Keep up the good work!', 'Great job resting! Getting enough sleep promotes a healthy mind and body.']}
    

    if(l1):
        most_recent1 = user_fitness_data.find({"user_id" : u_id['user_id'], "workout_type" : w1}, {'_id' : 0, f'{l1[0]}' : 1}).sort({"date" : -1}).limit(1)
        avg_q1 = user_fitness_data.find({"user_id" : u_id['user_id'], "workout_type" : w1}, {"_id" : 0, "date" : 1, f'{l1[0]}' : 1}).sort({"date" : -1}).limit(7)

        df1 = pd.DataFrame((doc['date'], doc[l1[0]]) for doc in avg_q1)
        avg1 = pd.DataFrame(data=df1.loc[::-1, 1]).rolling(7).mean()
        avg1 = avg1.loc[0]
        #print(f'AVG 1 CHECK:\n{avg1}')
        #print(f'MOST RECENT VALUE: {most_recent1[0][l1[0]]}')

        if(float(most_recent1[0][l1[0]]) == float(avg1)):
            suggestions.append(sugg_list[l1[0]][1])
        elif(float(most_recent1[0][l1[0]]) > float(avg1)):
            suggestions.append(sugg_list[l1[0]][0])
        else:
            suggestions.append(sugg_list[l1[0]][2])

    if(l2):
        most_recent2 = user_fitness_data.find({"user_id" : u_id['user_id'], "workout_type" : w2}, {'_id' : 0, f'{l2[0]}' : 1}).sort({"date" : -1}).limit(1)
        avg_q2 = user_fitness_data.find({"user_id" : u_id['user_id'], "workout_type" : w2}, {"_id" : 0, "date" : 1, f'{l2[0]}' : 1}).sort({"date" : -1}).limit(7)

        df2 = pd.DataFrame((doc['date'], doc[l2[0]]) for doc in avg_q2)
        avg2 = pd.DataFrame(data=df2.loc[::-1, 1]).rolling(7).mean()
        avg2 = avg2.loc[0]

        if(float(most_recent2[0][l2[0]]) == float(avg2)):
            suggestions.append(sugg_list[l2[0]][1])
        elif(float(most_recent2[0][l2[0]]) > float(avg2)):
            suggestions.append(sugg_list[l2[0]][0])
        else:
            suggestions.append(sugg_list[l2[0]][2])

    if(l3):
        most_recent3 = user_fitness_data.find({"user_id" : u_id['user_id'], "workout_type" : w3}, {'_id' : 0, f'{l3[0]}' : 1}).sort({"date" : -1}).limit(1)
        avg_q3 = user_fitness_data.find({"user_id" : u_id['user_id'], "workout_type" : w3}, {"_id" : 0, "date" : 1, f'{l3[0]}' : 1}).sort({"date" : -1}).limit(7)

        df3 = pd.DataFrame((doc['date'], doc[l3[0]]) for doc in avg_q3)
        avg3 = pd.DataFrame(data=df3.loc[::-1, 1]).rolling(7).mean()
        avg3 = avg3.loc[0]

        if(float(most_recent3[0][l3[0]]) == float(avg3)):
            suggestions.append(sugg_list[l3[0]][1])
        elif(float(most_recent3[0][l3[0]])> float(avg3)):
            suggestions.append(sugg_list[l3[0]][0])
        else:
            suggestions.append(sugg_list[l3[0]][2])

    if(l4):
        most_recent4 = user_fitness_data.find({"user_id" : u_id['user_id'], "workout_type" : w4}, {'_id' : 0, f'{l1[0]}' : 1}).sort({"date" : -1}).limit(1)
        avg_q4 = user_fitness_data.find({"user_id" : u_id['user_id'], "workout_type" : w4}, {"_id" : 0, "date" : 1, f'{l4[0]}' : 1}).sort({"date" : -1}).limit(7)

        df4 = pd.DataFrame((doc['date'], doc[l4[0]]) for doc in avg_q4)
        avg4 = pd.DataFrame(data=df4.loc[::-1, 1]).rolling(7).mean()
        avg4 = avg4.loc[0]

        if(float(most_recent4[0][l4[0]]) == float(avg4)):
            suggestions.append(sugg_list[l4[0]][1])
        elif(float(most_recent4[0][l4[0]]) > float(avg4)):
            suggestions.append(sugg_list[l4[0]][0])
        else:
            suggestions.append(sugg_list[l4[0]][2])
        
        return suggestions


def default_dashboard(request):

    context = {}

    return HttpResponse(render(request, 'Dashboard/default_dashboard.html', context))


def user_dashboard(request):

    # get username/password and check it in database
    # query u_id from u_nmae, pwd, put in context
    u_name = ''
    password = ''
    u_id = ''

    if (request.POST.get('username')):
        print('Here 1')
        u_name = request.POST.get('username')
        password = request.POST.get('password')
        u_id = users.find_one({"u_name": u_name, "password": password}, {
                              "_id": 0, "user_id": 1})
    else:
        print('Here 2')
        u_name = request.session.get('u_name')
        tmp = request.session.get('u_id')
        u_id = {'user_id': tmp}

    print(f'U_ID CHECK: {type(u_id)} {u_id}')
    print(f'UNAME CHECK: {type(u_name)} {u_name}')
    print(f'PASSWORD CHECK: {type(password)} {password}')

    request.session['u_name'] = u_name
    request.session['u_id'] = u_id

    init_workout_type = "Walking"
    init_metric = ["active_minutes"]
    init_agg_select = 'date_agg'

    fig1 = RenderPlot(u_id, u_name, init_workout_type,
                      init_metric, init_agg_select)
    fig2 = RenderPlot(u_id, u_name, init_workout_type,
                      init_metric, init_agg_select)
    fig3 = RenderPlot(u_id, u_name, init_workout_type,
                      init_metric, init_agg_select)
    fig4 = RenderPlot(u_id, u_name, init_workout_type,
                      init_metric, init_agg_select)

    request.session['fig1'] = fig1
    request.session['fig2'] = fig2
    request.session['fig3'] = fig3
    request.session['fig4'] = fig4

    context = {"u_id": u_id, "u_name": u_name, "fig1": fig1,
               "fig2": fig2, "fig3": fig3, "fig4": fig4}

    return HttpResponse(render(request, 'Dashboard/user_dashboard.html', context))


def update_user_dashboard(request):

    # form info
    # u_id = request.POST.get('u_id')
    # u_id = ast.literal_eval(u_id)
    # u_name = request.POST.get('u_name')
    # print(f'U_ID UPDATE CHECK: {type(u_id)} {u_id}')

    # session info
    u_name = request.session.get('u_name')
    u_id = request.session.get('u_id')

    fig1, fig2, fig3, fig4 = '', '', '', ''
    workout_type_1, workout_type_2, workout_type_3, workout_type_4 = '', '', '', ''
    metric_1, metric_2, metric_3, metric_4 = ([] for i in range(4))
    MOTIVATION = []

    # get rest of info to query with
    # need function to query data, return data frame to be passed to render graph
    # put metrics into a list? 1st x-axis, 2nd y-axis, 3rd optional this per that
    if (request.method == "POST"):
        workout_type_1 = request.POST.get('workout_type_1')
        workout_type_2 = request.POST.get('workout_type_2')
        workout_type_3 = request.POST.get('workout_type_3')
        workout_type_4 = request.POST.get('workout_type_4')

        metric_1.append(request.POST.get('metric_1_1'))
        metric_2.append(request.POST.get('metric_2_1'))
        metric_3.append(request.POST.get('metric_3_1'))
        metric_4.append(request.POST.get('metric_4_1'))
        # print(f'FORM CHECK: {metric_1}')

        agg_select_1 = request.POST.get('agg_select_1')
        agg_select_2 = request.POST.get('agg_select_2')
        agg_select_3 = request.POST.get('agg_select_3')
        agg_select_4 = request.POST.get('agg_select_4')
        
    
        if(request.POST.get('metric_1_2') != 'none'):
            metric_1.append(request.POST.get('metric_1_2'))
        if(request.POST.get('metric_2_2') != 'none'):
            metric_2.append(request.POST.get('metric_2_2'))
        if(request.POST.get('metric_3_2') != 'none'):
            metric_3.append(request.POST.get('metric_3_2'))
        if(request.POST.get('metric_4_2') != 'none'):
            metric_4.append(request.POST.get('metric_4_2'))
                

        if (request.POST.get('metric_1_2') != 'none'):
            metric_1.append(request.POST.get('metric_1_2'))
        if (request.POST.get('metric_2_2') != 'none'):
            metric_2.append(request.POST.get('metric_2_2'))
        if (request.POST.get('metric_3_2') != 'none'):
            metric_3.append(request.POST.get('metric_3_2'))
        if (request.POST.get('metric_4_2') != 'none'):
            metric_4.append(request.POST.get('metric_4_2'))

        # elif(agg_select == 'count_agg'):
        #   print(f'COUNT AGG CHECK')

        fig1 = RenderPlot(u_id, u_name, workout_type_1, metric_1, agg_select_1)
        fig2 = RenderPlot(u_id, u_name, workout_type_2, metric_2, agg_select_2)
        fig3 = RenderPlot(u_id, u_name, workout_type_3, metric_3, agg_select_3)
        fig4 = RenderPlot(u_id, u_name, workout_type_4, metric_4, agg_select_4)

        request.session['fig1'] = fig1
        request.session['fig2'] = fig2
        request.session['fig3'] = fig3
        request.session['fig4'] = fig4
        
        motiv_metrics = {'heart_rate_avg', 'active_minutes', 'sleep_hours'}
        mm_1 = set(metric_1) & motiv_metrics
        mm_2 = set(metric_2) & motiv_metrics
        mm_3 = set(metric_3) & motiv_metrics
        mm_4 = set(metric_4) & motiv_metrics

        mm_1 = list(mm_1)[:1]
        mm_2 = list(mm_2)[:1]
        mm_3 = list(mm_3)[:1]
        mm_4 = list(mm_4)[:1]

        MOTIVATION = GET_MOTIVATED(u_id, workout_type_1, workout_type_2, workout_type_3, workout_type_4, mm_1, mm_2, mm_3, mm_4)
        print(f'MOTIV CHECK: {MOTIVATION}')

        # request.session[''] =

    else:
        fig1 = request.session.get('fig1')
        fig2 = request.session.get('fig2')
        fig3 = request.session.get('fig3')
        fig4 = request.session.get('fig4')
    context = {"u_id" : u_id, "u_name" : u_name, "fig1" : fig1, "fig2" : fig2, "fig3" : fig3, "fig4" : fig4, "MOTIVATION" : MOTIVATION}
    context = {"u_id": u_id, "u_name": u_name, "fig1": fig1,
               "fig2": fig2, "fig3": fig3, "fig4": fig4}

    return HttpResponse(render(request, 'Dashboard/user_dashboard.html', context))


def GetUpdateWorkoutQuery(u_id, search_by, search_query):

    # lookup = {'date' : 'date', 'distance_km' : 'distance_km'}

    if (search_by == '_id'):
        search_query = ObjectId(f'{search_query}')
    elif (search_by == 'date'):
        search_query = FormatDate(search_query)
    else:
        try:
            search_query = float(search_query)
        except ValueError:
            pass

    # print(f'U_ID CHECK: {u_id} {search_by} {type(search_query)} {search_query}')
    ret_doc = user_fitness_data.find(
        {"user_id": u_id['user_id'], str(search_by): search_query})
    return [doc for doc in ret_doc]

    # print(f'FIN DOC CHECK:\n{docs}')


def update_workout(request):

    u_name = request.session.get('u_name')
    u_id = request.session.get('u_id')
    # print(f'U_ID CHECK: {type(u_id)} {u_id}')
    # print(f'UNAME CHECK: {type(u_name)} {u_name}')

    docs = []
    # df = [(doc['date'], doc[metrics[0]]) for doc in df]
    if (request.method == "POST"):
        # CACHE THE RETURNED LIST
        search_by = request.POST.get('search_by')
        search_query = request.POST.get('search_query')
        docs = GetUpdateWorkoutQuery(u_id, search_by, search_query)

    context = {"u_id": u_id, "u_name": u_name, "docs": docs}

    return HttpResponse(render(request, 'Dashboard/update_workout.html', context))


def AddDocField(doc_id, field, value):

    add_val = {"$set": {f'{field}': value}}
    # print(add_val)

    try:
        value = float(value)
    except ValueError:
        try:
            value = int(value)
        except ValueError:
            pass

    if (isinstance(value, str)):
        value = value.strip()

    user_fitness_data.update_one({'_id': ObjectId(doc_id)}, add_val)


def RemoveDocField(doc_id, field):

    user_fitness_data.update_one({'_id': ObjectId(doc_id)}, {
                                 "$unset": {f'{field}': ""}})


def DeleteWholeDoc(doc_id):

    user_fitness_data.delete_one({'_id': ObjectId(doc_id)})


def TrimObjID(doc):

    id_start = doc.find('(')
    id_stop = doc.find(')', id_start)

    obj_id = doc[id_start+2: id_stop-1]

    return obj_id


def UpdateEditDoc(new_doc, doc_id):

    update_vals = {"$set": {}}

    for k, v in new_doc:
        if k != 'csrfmiddlewaretoken' and k != 'doc_id' and k != 'edit_delete_select':

            if (k == 'date'):
                v = FormatDate(v)
            else:
                try:
                    v = float(v)
                except ValueError:
                    try:
                        v = int(v)
                    except ValueError:
                        pass

                if (isinstance(v, str)):
                    v = v.strip()

            # print(f'Key: {k} {type(k)}')
            # print(f'Value: {v} {type(v)}')

            update_vals['$set'].update({k: v})

    # print(f'UPDATE VALS CHECK: {update_vals}')
    user_fitness_data.update_one({'_id': ObjectId(doc_id)}, update_vals)

    # new_doc = user_fitness_data.find_one({'_id' : ObjectId(doc_id)})
    # print(f'NEW DOC CHECK: {new_doc}')

    # make sure query updates doc correctly


def CreateNewDoc(doc_info, u_id):

    insert_fields = {}

    for field, value in doc_info:

        if (field != 'csrfmiddlewaretoken'):

            if (field == 'date'):
                value = FormatDate(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    try:
                        value = int(value)
                    except ValueError:
                        pass

                if (isinstance(value, str)):
                    value = value.strip()

            insert_fields.update({field: value})

    insert_fields.update({'user_id': u_id['user_id']})
    print(insert_fields)
    user_fitness_data.insert_one(insert_fields)


def edit_workout(request):

    u_name = request.session.get('u_name')
    u_id = request.session.get('u_id')

    context = {"u_id": u_id, "u_name": u_name}

    if (request.method == "POST"):

        # try except here for only one value for created value
        if (request.POST.get('created_field') and request.POST.get('created_value')):
            action = 'create_field'
            field = request.POST.get('created_field')
            value = request.POST.get('created_value')

        elif (request.POST.get('remove_field')):
            action = 'remove_field'
            field = request.POST.get('remove_field')

        else:
            action = request.POST.get('edit_delete_select')

        print(f'ACTION CHECK: {action}')

        if (action == 'edit'):
            doc = request.POST.get('doc_info')
            obj_id = TrimObjID(doc)
            doc = user_fitness_data.find_one({'_id': ObjectId(obj_id)})
            doc_id = {'_id': doc['_id'], 'user_id': doc['user_id']}
            del doc['_id']
            del doc['user_id']

            context.update({"action": action})
            context.update({"doc": doc})
            context.update({"doc_id": doc_id})

        elif (action == 'update'):
            doc_id = request.POST.get('doc_id')
            new_doc = request.POST.items()

            doc_id = TrimObjID(doc_id)
            UpdateEditDoc(new_doc, doc_id)
            # print(f'DOC ID: {doc_id}')
            updated_doc = user_fitness_data.find_one({'_id': ObjectId(doc_id)})
            doc_id = {'_id': updated_doc['_id'],
                      'user_id': updated_doc['user_id']}
            del updated_doc['_id']
            del updated_doc['user_id']

            context.update({"action": action})
            context.update({"doc": updated_doc})
            context.update({"doc_id": doc_id})

        elif (action == 'create_field'):
            # CREATE WHOLE NEW DOCUMENT?
            doc_id = request.POST.get('doc_id')
            doc_id = TrimObjID(doc_id)
            # print(f'CREATE DOC CHECK: {type(doc_id)} {doc_id}')

            AddDocField(doc_id, field, value)

            updated_doc = user_fitness_data.find_one({'_id': ObjectId(doc_id)})
            doc_id = {'_id': updated_doc['_id'],
                      'user_id': updated_doc['user_id']}
            del updated_doc['_id']
            del updated_doc['user_id']

            context.update({"action": action})
            context.update({"doc": updated_doc})
            context.update({"doc_id": doc_id})

        elif (action == 'delete'):

            try:
                doc_id = request.POST.get('doc_id')
            except:
                doc_info = request.POST.get('doc_info')
                doc_id = TrimObjID(doc)

            DeleteWholeDoc(doc_id)

            context.update({"action": action})

        elif (action == 'remove_field'):
            doc_id = request.POST.get('doc_id')
            doc_id = TrimObjID(doc_id)

            RemoveDocField(doc_id, field)

            updated_doc = user_fitness_data.find_one({'_id': ObjectId(doc_id)})
            doc_id = {'_id': updated_doc['_id'],
                      'user_id': updated_doc['user_id']}
            del updated_doc['_id']
            del updated_doc['user_id']

            context.update({"action": action})
            context.update({"doc": updated_doc})
            context.update({"doc_id": doc_id})

    return HttpResponse(render(request, 'Dashboard/edit_workout.html', context))


def create_workout(request):

    u_name = request.session.get('u_name')
    u_id = request.session.get('u_id')
    context = {"u_id": u_id, "u_name": u_name}

    if (request.method == 'POST'):

        doc_info = request.POST.items()
        CreateNewDoc(doc_info, u_id)

    return HttpResponse(render(request, 'Dashboard/create_workout.html', context))
