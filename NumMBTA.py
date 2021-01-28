import time, os, re, datetime, json
import requests
from datetime import datetime, timedelta

# This program:
# 1. Asks user to choose from the list of train routes
# 2. Validates the entered route and asks to choose from the list of stations
# 3. Validates the entered station and asks to choose a direction
# 4. Validates the entered direction and displays the next predicted departure time

def main():

# get list of train routes , display, ask to choose and return selection

    route_select_id,route_direct_id = route()
    if route_select_id:
        pass
    else:
        return None

    # get list of stops  , display, ask to choose and return selection

    stop_select_id = stop(route_select_id)
    if stop_select_id:
        pass
    else:
        return None

    #if terminal stop - shoud only one possible destination?

    # get list of directions  , display, ask to choose and return selection

    direct_select_id = direct(route_direct_id)
    if str(direct_select_id).isnumeric():
        pass
    else:
        return None

    # get and display next departure time

    next_departure_time(route_select_id,direct_select_id,stop_select_id)

def send_request(req):

    url = 'https://api-v3.mbta.com/'+ req

    r = requests.get(url)

    if r.status_code != 200:
        print ('Bad Return from {} api - {} {}'.format(req,r.status_code,r.text))
        return None

    apiresult = r.json()

    return apiresult

def route():
    route_name_id_lst = []
    route_lst = get_routes()

    print (' ')
    print ('List of routes: ')
    for i in range(0,len(route_lst)):
        route_name_id = route_lst[i].split(',')
        route_name_id_lst.append(route_name_id)
        print(str(i+1) + '. ' + route_name_id[0])

    while True:
        route_num = input('Please select a route ' + '[1-' + str(len(route_lst)) + '] :')
        if validate(route_num,len(route_lst)):
            route_num = int(route_num)
            break
        else:
            if input('Your input is invalid, do you want to correct and continue Y/N? ').lower() != 'y':
                return None

    route_selected_name = route_name_id_lst[route_num-1][0]
    route_selected_id = route_name_id_lst[route_num-1][1]
    route_direct_id = route_name_id_lst[route_num-1][3]
    print ('Route selected: ',route_selected_name)
    return route_selected_id,route_direct_id

def get_routes():

    route_lst = []
    req = 'routes?filter[type]=0,1'
    r = send_request(req)

    r = r['data']
    for d in r:
        route_lst.append(d['attributes']['long_name']
        + ',' + d['id'] + ','
        + (':').join(d['attributes']['direction_destinations']) + ','
        + (':').join(d['attributes']['direction_names']))

    return route_lst

def stop(route_select_id):
    stop_name_id_lst = []
    stop_lst = get_stops(route_select_id)

    print (' ')
    print ('List of stops: ')
    for i in range(0,len(stop_lst)):
        stop_name_id = stop_lst[i].split(',')
        stop_name_id_lst.append(stop_name_id)
        print(str(i+1) + '. ' + stop_name_id[0])

    while True:
        stop_num = input('Please select a stop ' + '[1-' + str(len(stop_lst)) + '] :')
        if validate(stop_num,len(stop_lst)):
            stop_num = int(stop_num)
            break
        else:
            if input('Your input is invalid, do you want to correct and continue Y/N? ').lower() != 'y':
                return None

    stop_selected_name = stop_name_id_lst[stop_num-1][0]
    stop_selected_id = stop_name_id_lst[stop_num-1][1]
    print ('Stop selected: ',stop_selected_name)
    return stop_selected_id

def get_stops(route_id):

    stop_lst = []

    req = 'stops?filter[route]='+route_id

    r = send_request(req)

    r = r['data']
    for d in r:
        stop_lst.append(d['attributes']['name'] + ',' + d['id'])

    return stop_lst

def direct(route_direct):

    dest_name = route_direct.split(':')
    print (' ')
    print ('List of directions: ')
    for i in range(0,len(dest_name)):
        print(str(i+1) + '. ' + dest_name[i])

    while True:
        dest_num = input('Please select a direction ' + '[1-' + str(len(dest_name)) + '] :')
        if validate(dest_num,len(dest_name)):
            dest_num = int(dest_num)
            break
        else:
            if input('Your input is invalid, do you want to correct and continue Y/N? ').lower() != 'y':
                return None

    direct_name = dest_name[dest_num-1]
    direct_num = dest_num-1
    print ('Direction selected: ',direct_name)

    return direct_num

def next_departure_time(route_select_id,direct_select_id,stop_select_id):
    next_departure_raw = get_next_departure(route_select_id,direct_select_id,stop_select_id)

    next_departure = next_departure_raw[(next_departure_raw.index(' ') + 1):(next_departure_raw.index(' ') + 6)]
    if next_departure[:2] == '12':
        us_next_departure = next_departure + ' PM'
    elif next_departure[:2] > '12':
        us_next_departure = str(int(next_departure[:2])-12) + next_departure[2:] + ' PM'
    else:
        us_next_departure = next_departure + ' AM'
    print (' ')
    print ('Next predicted departure time: ', us_next_departure)

def get_next_departure(route_id,direct_id,stop_id):

    req = 'predictions?filter[route]=' + route_id + '&[stop]=' + stop_id

    r = send_request(req)

    r = r['data']
    for d in r:
        if d['attributes']['direction_id'] == direct_id and d['attributes']['departure_time']:
            next_departure = d['attributes']['departure_time'].replace('T', ' ')
            if next_departure > str(datetime.now()):

                return next_departure
    return None

def validate(selection,boundary):

    if selection.isnumeric():
        if int(selection) > 0 and int(selection) <= boundary:
            return True
    return False

if __name__ == '__main__':

    print ("WELCOME TO NUMERATED MBTA!")

    while True:
        main()
        print (' ')
        if input('Do you want to check another departure - Y/N? ').lower() == 'y':
            pass
        else:
            print ("Thank you for using NUMERATED MBTA!")
            break
