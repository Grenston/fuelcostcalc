import logging
import requests
import math
from bs4 import BeautifulSoup
import urllib3
import azure.functions as func
import json

def get_all_state_prices(URL):
    page = requests.get(URL, verify=False)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table")
    table_body = table.find("tbody")
    rows = table_body.findAll('tr')
    fuel_price_dict = {}
    i = 1
    while i<len(rows):
        cols = rows[i].findAll('td')
        state = cols[0].find('a')
        fuel_price = cols[1]
        key_value = state.contents[0].replace(' ','')
        value = float(fuel_price.contents[0].split(' ')[0])
        fuel_price_dict[key_value]= value
        i=i+1
    return fuel_price_dict

def calculate_total_fuel_cost(price_per_litre, total_distance, avg_mileage):
    required_fuel = total_distance/avg_mileage
    total_fuel_cost = required_fuel * price_per_litre
    return round(required_fuel,2), round(total_fuel_cost,2)

def roundup(x):
    return int(math.ceil(x / 50.0)) * 50

def get_response(all_state_prices, total_distance, avg_mileage, state_name, diesel=False):
    if all_state_prices.get(state_name, -1) == -1:
        response = {'message':'Provide proper values for state',
                    'availableStates': list(all_state_prices.keys())}
        return response, 422
    else:
        price_per_litre = float(all_state_prices[state_name])
        if total_distance <= 0.0 or avg_mileage <= 0.0:
            response = {'message':'Provide proper values for distance and mileage'}
            return response, 422
        else:
            required_fuel, total_fuel_cost = calculate_total_fuel_cost(price_per_litre,total_distance,avg_mileage)
            rounded_fuel_cost = roundup(total_fuel_cost)
            response = { 'current_petrol_price': price_per_litre,
                        'total_petrol_required_in_litres': required_fuel,
                        'total_petrol_cost': total_fuel_cost,
                        'total_petrol_cost_rounded': rounded_fuel_cost
                        }
            if diesel:
                response = { 'current_diesel_price': price_per_litre,
                        'total_diesel_required_in_litres': required_fuel,
                        'total_diesel_cost': total_fuel_cost,
                        'total_diesel_cost_rounded': rounded_fuel_cost
                        }
            return response, 200

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    URL = 'https://www.ndtv.com/fuel-prices/petrol-price-in-all-state'
    all_state_prices = get_all_state_prices(URL)
    distance = req.params.get('distance')
    if not distance:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            distance = req_body.get('distance')
        distance = req.params.get('distance')

    mileage = req.params.get('mileage')
    if not mileage:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            mileage = req_body.get('mileage')

    state = req.params.get('state')
    if not state:
        try:
            req_body = req.get_json()
        except ValueError:
            state = 'Kerala'
        else:
            state = req_body.get('state')   

    if distance and mileage:
        URL = 'https://www.ndtv.com/fuel-prices/petrol-price-in-all-state'
        all_state_prices = get_all_state_prices(URL)
        response, status_code = get_response(all_state_prices, float(distance), float(mileage), state)
        return func.HttpResponse(json.dumps(response),mimetype="application/json",status_code=status_code)
    else:
        return func.HttpResponse(
             "Call this API to calculate the petrol required for your trip.<br>"+ \
             "Provide values for distance, mileage and state. Example url?distance=400&mileage=15&state=Kerala.<br>"+ \
             "State is not mandatory, Kerala is taken by default.<br><br>"+ \
             "All state values:<br><br>"+ \
             "AndamanAndNicobar<br>AndhraPradesh<br>ArunachalPradesh<br>Assam<br>Bihar<br>Chandigarh<br>Chhatisgarh<br>"+ \
             "DadraAndNagarHaveli<br>DamanAndDiu<br>Delhi<br>Goa<br>Gujarat<br>Haryana<br>HimachalPradesh<br>"+ \
             "JammuAndKashmir<br>Jharkhand<br>Karnataka<br>Kerala<br>MadhyaPradesh<br>Maharashtra<br>Manipur<br>"+ \
             "Meghalaya<br>Mizoram<br>Nagaland<br>Odisha<br>Pondicherry<br>Punjab<br>Rajasthan<br>Sikkim<br>"+ \
             "TamilNadu<br>Telangana<br>Tripura<br>UttarPradesh<br>Uttarakhand<br>WestBengal",
             mimetype="text/html",
             status_code=200
        )
