import base64
import json

import requests

from ratehawk_sdk import config


class RateHawkSDK:
    HOTEL_URI = 'https://api.worldota.net/api/b2b/v3'
    API_ID = config.RATEHAWK_CONFIG.get('ID')
    API_KEY = config.RATEHAWK_CONFIG.get('API_KEY')
    HEADERS = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic %s' % base64.b64encode(bytes(f'{API_ID}:{API_KEY}', 'utf-8')).decode('utf-8')
    }
    TOKEN = None
    LANGUAGE = None
    ENDPOINTS = {
        'HOTEL_SEARCH_AUTOCOMPLETE': f'{HOTEL_URI}/search/multicomplete/',
        'HOTEL_INFORMATION': f'{HOTEL_URI}/hotel/info/',
        'HOTEL_SEARCH_BY_REGION': f'{HOTEL_URI}/search/serp/region/',
        'HOTEL_SEARCH_BY_HOTEL': f'{HOTEL_URI}/search/serp/hotels/',
        'HOTEL_ORDER': f'{HOTEL_URI}/hotel/order/booking/form/',
    }
    CURRENCY = 'USD'

    def __init__(self, lang='es'):
        self.LANGUAGE = lang.lower()

    @staticmethod
    def handle_error(response):
        if response.status_code != 200:
            error = response.json()
            if error.get('status') == 'error':
                message = [f"[{error.get('error')}]"]
                if error.get('debug', {}).get('validation_error'):
                    message += [error.get('debug', {}).get('validation_error')]
                return {'status': response.status_code, 'message': '. '.join(message)}
        return None

    def autocomplete_search_hotel_criteria(self, text: str):
        json_data = {
            'query': text,
            'language': self.LANGUAGE
        }
        response = requests.post(
            self.ENDPOINTS.get('HOTEL_SEARCH_AUTOCOMPLETE'), data=json.dumps(json_data), headers=self.HEADERS
        )

        error = self.handle_error(response)
        if error:
            return error

        data = response.json().get('data', {})
        return {
            'hotels': data.get('hotels', []),
            'regions': data.get('regions', []),
        }

    def hotel_information(self, hotel_id: str):
        json_data = {
            'id': hotel_id,
            'language': self.LANGUAGE
        }
        response = requests.post(
            self.ENDPOINTS.get('HOTEL_INFORMATION'), data=json.dumps(json_data), headers=self.HEADERS
        )

        error = self.handle_error(response)
        if error:
            return error

        return response.json().get('data', {})

    def availability_by_region(self, start_date: str, end_date: str, region_id: int, guests: list):
        json_data = {
            'checkin': start_date,
            'checkout': end_date,
            'language': self.LANGUAGE,
            'guests': guests,
            'region_id': region_id,
            'currency': self.CURRENCY,
        }

        response = requests.post(
            self.ENDPOINTS.get('HOTEL_SEARCH_BY_REGION'), data=json.dumps(json_data), headers=self.HEADERS
        )

        error = self.handle_error(response)
        if error:
            return error

        return response.json().get('data', {})

    def availability_by_hotel(self, start_date: str, end_date: str, hotel_id: str, guests: list):
        json_data = {
            'checkin': start_date,
            'checkout': end_date,
            'language': self.LANGUAGE,
            'guests': guests,
            'ids': [hotel_id],
            'currency': self.CURRENCY,
        }

        response = requests.post(
            self.ENDPOINTS.get('HOTEL_SEARCH_BY_HOTEL'), data=json.dumps(json_data), headers=self.HEADERS
        )

        error = self.handle_error(response)
        if error:
            return error

        return response.json().get('data', {})

    def order(self, offer_hash: str, partner_id: str):
        json_data = {
            'partner_order_id': partner_id,
            'book_hash': offer_hash,
            'language': self.LANGUAGE,
            'user_ip': '82.29.0.86'
        }

        response = requests.post(
            self.ENDPOINTS.get('HOTEL_ORDER'), data=json.dumps(json_data), headers=self.HEADERS
        )
        print(response.json())

        error = self.handle_error(response)
        if error:
            return error

        return response.json().get('data', {})
