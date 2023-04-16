import logging

import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    URL = 'https://www.ndtv.com/fuel-prices/petrol-price-in-all-state'

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
        return func.HttpResponse(json.dumps({"distance":distance,"mileage":mileage,"state":state}),mimetype="application/json",status_code=200)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
