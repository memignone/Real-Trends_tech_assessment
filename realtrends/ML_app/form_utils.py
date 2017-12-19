"""
ML_app Form Utils Module
"""
from __future__ import unicode_literals

import json

from .views import Meli


def get_meli_obj(request):
    """
    Return an instance of a Meli object
    """
    return Meli(request.session['CLIENT_ID'], request.session['CLIENT_SECRET'],
                request.session['ACCESS_TOKEN'], request.session['REFRESH_TOKEN'])


def get_currencies(meli):
    """
    Retrieve currencies from https://api.mercadolibre.com/currencies
    """
    listing_types = list()
    
    response = meli.get('/currencies/')
    json_response = json.loads(response.content)
    
    for listing_type in json_response:
        listing_types.append((listing_type['id'], listing_type['description']))
    return listing_types


def get_listing_types(meli):
    """
    Retrieve listing types from https://api.mercadolibre.com/sites/MLA/listing_types
    """
    listing_types = list()
    
    response = meli.get('/sites/MLA/listing_types/')
    json_response = json.loads(response.content)
    
    for listing_type in json_response:
        listing_types.append((listing_type['id'], listing_type['name']))
    return listing_types
