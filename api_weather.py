import requests
import json

TOKEN = 'zapt35xt1chgyamr9q03vkgs9rej8thil6zwqkgz'

URL_weather_base = 'https://www.meteosource.com/api/v1/free/'


def find_places_by_location(location):
    url = f"{URL_weather_base}find_places?text={location}&key={TOKEN}"
    response = json.loads(requests.get(url).text)
    if not response:
        res = {'error': True}
        return res

    index_choice = 1
    res = {'error': False, 'data': []}
    for item in response:
        data = {
            'id': index_choice,
            'name': item['name'],
            'place_id': item['place_id'],
            'country': item['country']
        }
        index_choice = index_choice + 1
        res['data'].append(data)

    return res


def get_weather_by_city(city_name):
    url = f"{URL_weather_base}point?place_id={city_name}&key={TOKEN}"
    response = json.loads(requests.get(url).text)
    weather_city = {'error': False, 'temperature': response['current']['temperature']}
    return weather_city

