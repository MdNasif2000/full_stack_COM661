import datetime
import json
import urllib.request

def url_builder(lat , lon):
    api = "4dfba26b744104c08dcd02c449cd4fa4"
    unit = "metric"
    
    return 'http://api.openweathermap.org/data/2.5/weather?' + \
                'unit=' + unit + \
                '&APPID=' + api + \
                '&lat=' + str(lat) + \
                '&lon=' + str(lon)

def fetch_data(full_url):
    url = urllib.request.urlopen(full_url)
    output = url.read().decode('utf-8')
    return json.loads(output)

def time_converter(timestamp):
    return datetime.datetime.fromtimestamp(timestamp). \
            strftime('%d %b %I:%M %p')
            
            
lat = 51.5074
lon = - 0.1278


jason_data= fetch_data(url_builder(lat , lon))

temperature = str(jason_data['main']['temp'])
timestamp = time_converter(jason_data['dt'])

description = jason_data['weather'][0]['description']

print(jason_data)
print('\n Current Weather Temparature and Description \n')
print(timestamp + " - " + temperature + "° : " + \
        description)