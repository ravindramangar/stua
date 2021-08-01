import requests, csv, datetime, math, time
import gtfs_realtime_pb2, nyct_subway_pb2
from flask import Flask, render_template, Response

API = 'p4G33OQzU8acTdI6FbwCQ3C4bXKbmLFla5ZSDvdc'

def start(stop_ids, direction, interval):
    #result = []
    #stop_ids = input('Stop IDs: ')
    #stop_ids = 'G08'
    #stop_ids = stop_ids.split(' ')
    #for stop_id in stop_ids:
        #result.append(transit(stop_id, 'N'))
        #result.append(transit(stop_id, 'S'))
    result = transit(stop_ids, direction, interval)
    return result
    

def url(line):
    if line == 'SIR':
        link = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si'
    elif line in 'ACE':
        link = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace'
    elif line in 'BDFM':
        link = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm'
    elif line in 'NQRW':
        link = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw'
    elif line in 'JZ':
        link = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz'
    elif line in 'G':
        link = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g'
    elif line in 'L':
        link = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l'
    else:
        link = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs'
    return link


def transit(stop, direction, interval):
    times = []
    current_time = datetime.datetime.now()
    with open("stops.txt") as file:
        file = csv.reader(file)
        for row in file:
            if stop == row[2]:
                lines = row[7].split(" ")
                for line in lines:
                    destination = []
                    link = url(line)
                    feed = gtfs_realtime_pb2.FeedMessage()
                    response = requests.get(link, headers={'x-api-key' : API})
                    feed.ParseFromString(response.content)
                    for entity in feed.entity:
                        if entity.trip_update:
                            for update in entity.trip_update.stop_time_update:
                                if update.stop_id == (stop+direction):
                                    time = update.arrival.time
                                    if time <= 0:
                                            time = update.departure.time
                                    time = datetime.datetime.fromtimestamp(time)
                                    time = math.trunc(((time - current_time).total_seconds()) / 60)
                                    if time < interval:
                                        pass
                                    else:
                                        for update in entity.trip_update.stop_time_update:
                                                destination.append(update.stop_id)
                                        if entity.trip_update.trip.route_id == line:
                                            times.append([time,entity.trip_update.trip.route_id, destination[-1][:-1]])
    times.sort()
    for element in times:
        with open('stops.txt','r') as csv_file:
                csv_file = csv.reader(csv_file)
                for row in csv_file:
                        if row[2] == element[2]:
                                element.append(f'{row[5]} ({row[2]})')
                                element.pop(2)
    with open('stops.txt','r') as csv_file:
        csv_file = csv.reader(csv_file)
        for row in csv_file:
                if row[2] == stop:
                        name = row[5]
    times = times[:5]
    result = f'{stop+direction} ({name}), {times}'
    return result 

#print(start('G08'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/broadway')
def broadway():
    def generate():
        value = True
        while (value == True):
            yield "data:" + start('137','N', 5) + "\n\n"
            time.sleep(2)
            #print('Restart B')
    return Response(generate(), mimetype= 'text/event-stream')

@app.route('/cityhall')
def cityhall():
    def generate():
        value = True
        while (value == True):
            yield "data:" + start('M21','S', 7) + "\n\n"
            time.sleep(2)
            #print('Restart C')
    return Response(generate(), mimetype= 'text/event-stream')

if __name__ in "__main__":
    app.run()
