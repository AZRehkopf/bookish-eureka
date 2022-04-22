# him_api_tester.py
# Testing suite for the HIM API

### Imports ###

# Buit-ins
from distutils.log import error
import json
import sys
import os

# Local
from tester.tester import Test, TestSuit, Regression

# Third Party
import requests

### Constants ###

DEBUG = False
SERVER_HOSTNAME = 'plutus.local'
SERVER_PORT = 8765

### Functions ###

def test_get(**kwargs):
    r = requests.get(f'http://{SERVER_HOSTNAME}:{SERVER_PORT}/{kwargs["target"]}')
    if DEBUG:
        print(r.status_code)
    
    if r.status_code == kwargs['expected']:
        return True
    else:
        return False

def test_json_post(**kwargs):
    r = requests.post(f'http://{SERVER_HOSTNAME}:{SERVER_PORT}/{kwargs["target"]}', json=kwargs['payload'])
   
    if DEBUG:
        print(r.status_code)
        print(r.content.decode('utf-8'))
    
    if r.status_code == kwargs['expected']:
        resp_data = r.content.decode('utf-8')

        if kwargs['empty_resp'] and resp_data == "":
            return True
        elif not kwargs['empty_resp'] and resp_data != "":
            return True
        else:
            return False
    else:
        return False

def test_b2b_json_post(**kwargs):
    r = requests.post(f'http://{SERVER_HOSTNAME}:{SERVER_PORT}/{kwargs["target"]}', json=kwargs['payload'])
    resp_data = r.content.decode('utf-8')
    
    if DEBUG:
        print(r.status_code)
        print(resp_data)
    
    if r.status_code == kwargs['expected'][0]:
        if kwargs['empty_resp'][0] and resp_data == "":
            pass
        elif not kwargs['empty_resp'][0] and resp_data != "":
            pass
        else:
            return False
    else:
        return False

    resp_data = json.loads(resp_data)[0][0]
    r = requests.post(
        f'http://{SERVER_HOSTNAME}:{SERVER_PORT}/{kwargs["target"]}', 
        json={
            'method': 'DELETE',
            'db': 'cleaning',
            'id': resp_data
        }
    )
    resp_data = r.content.decode('utf-8')

    if DEBUG:
        print(r.status_code)
        print(resp_data)

    if r.status_code == kwargs['expected'][1]:
        if kwargs['empty_resp'][1] and resp_data == "":
            return True
        elif not kwargs['empty_resp'][1] and resp_data != "":
            return True
        else:
            return False
    else:
        return False
    
### Main ###

if __name__ == '__main__':
    stat_suite = TestSuit('System Status')
    stat_suite.add_tests(
        [
            Test(
                test_get, 
                {
                    'target': 'status', 
                    'expected': 200,
                },
                "get_status"
            ),
            Test(
                test_json_post, 
                {
                    'target': 'status', 
                    'expected': 405,
                    'empty_resp': False,
                    'payload': {},

                },
                "bad_method_status"
            ),
        ]
    )
    
    db_suite = TestSuit('Data Manipulation')
    db_suite.add_tests(
        [
            Test(
                test_json_post, 
                {
                    'target': 'data', 
                    'payload': {
                        'method': 'GET',
                        'db': 'cleaning'
                    }, 
                    'expected': 200,
                    'empty_resp': False
                },
                "post_valid_get_data"
            ),
            Test(
                test_json_post, 
                {
                    'target': 'data', 
                    'payload': {
                        'method': 'PUT',
                        'db': 'cleaning',
                        'data': {
                            'name': 'Test Dummy',
                            'size': 'Boat load',
                            'location': 'uranus',
                            'stock': 4,
                            'target': -90
                        }
                    }, 
                    'expected': 200,
                    'empty_resp': False
                },
                "post_valid_put_data"
            ),
            Test(
                test_json_post, 
                {
                    'target': 'data', 
                    'payload': {
                        'method': 'PUT',
                        'db': 'cleaning',
                        'data': {
                        }
                    }, 
                    'expected': 400,
                    'empty_resp': True
                },
                "post_missing_put_data"
            ),
            Test(
                test_b2b_json_post, 
                {
                    'target': 'data', 
                    'payload': {
                        'method': 'PUT',
                        'db': 'cleaning',
                        'data': {
                            'name': 'Test Dummy',
                            'size': 'Boat load',
                            'location': 'uranus',
                            'stock': 4,
                            'target': -90
                        }
                    }, 
                    'expected': [200, 200],
                    'empty_resp': [False, True]
                },
                "post_valid_del_data"
            ),
            Test(
                test_json_post, 
                {
                    'target': 'data', 
                    'payload': {
                        'bad': 'garbage',
                        'more': 'shit'
                    }, 
                    'expected': 400,
                    'empty_resp': True
                },
                "post_bad_data"
            ),
            Test(
                test_json_post, 
                {
                    'target': 'data', 
                    'payload': {
                        'method': 'PAN',
                        'db': 'cleaning'
                    }, 
                    'expected': 400,
                    'empty_resp': True
                },
                "post_bad_method"
            ),
            Test(
                test_json_post, 
                {
                    'target': 'data', 
                    'payload': {
                        'method': 'GET',
                        'db': 'sleeping'
                    }, 
                    'expected': 400,
                    'empty_resp': True
                },
                "post_bad_db"
            )
        ]
    )
    
    him_regr = Regression("House Inventory Mangement API")
    him_regr.add_suite(stat_suite)
    him_regr.add_suite(db_suite)
    him_regr.run()
