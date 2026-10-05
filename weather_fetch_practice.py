import datetime, json , urllib.request

def url_builder(lat, lon):
    api ='4dfba26b744104c08dcd02c449cd4fa4'
    unit='metric'
    
# https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}
    
    return 'https://api.openweathermap.org/data/2.5/weather?' + \
            'lat=' + str(lat)+ \
            '&lon='+ str(lon) + \
            '&appid=' + api + \
            '&unit=' + unit
            
def fetch_data(url):
    url = urllib.request.urlopen(url)
    output = url.read().decode('utf-8')
    return json.loads(output)

def time_converter(timestamp):
    return datetime.datetime.fromtimestamp(timestamp). \
        strftime('%d %b %Y -- %H : %M %p')

print(fetch_data(url_builder(51.5074, -0.1278)))