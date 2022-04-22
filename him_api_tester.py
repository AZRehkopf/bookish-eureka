# him_api_tester.py
# Testing suite for the HIM API

### Imports ###

# Buit-ins
from distutils.log import error
import sys
import os
import timeit

# Third Party
import requests

### Constants ###
DEBUG = False
SERVER_HOSTNAME = 'plutus.local'
SERVER_PORT = 8765

### Functions ###

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

### Classes ###

class TermColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Test:
    def __init__(self, func, args, name):
        self.tf = func
        self.args = args
        self.name = name

        self.result = None
        self.exception = None
    
    def run(self):
        print(f"Running test {self.name}... ", end="")
        
        try:
            self.result = self.tf(**self.args)
        except Exception as error: 
            self.exception = error

        self.print_result()

    def print_result(self):
        if self.exception == None:
            if self.result:
                print(f"{TermColors.OKGREEN}PASS{TermColors.ENDC}")
            else:
                print(f"{TermColors.FAIL}FAIL{TermColors.ENDC}")
        else:
            print(f"{TermColors.FAIL}ERROR{TermColors.ENDC}")
            print(self.exception)


class TestSuit:
    def __init__(self, name):
        self.name = name
        self.passes = 0
        self.tests = []

    def add_test(self, test):
        self.tests.append(test)

    def add_tests(self, tests):
        self.tests.extend(tests)

    def run(self):
        print(f"{TermColors.BOLD}Starting {self.name} Suite {TermColors.ENDC}\n")
        for test in self.tests:
            test.run()
            if test.result: self.passes += 1

        self.print_results()

    def print_results(self):
        print(f"\n{TermColors.BOLD}Finshed all ({len(self.tests)}) tests in {self.name} suite")
        percent_pass = round(self.passes/len(self.tests), 2) * 100
        if percent_pass == 100:
            print(f"{TermColors.BOLD}{TermColors.OKGREEN}{percent_pass}%{TermColors.ENDC}{TermColors.BOLD} ({self.passes}/{len(self.tests)}) of tests are passing{TermColors.ENDC}\n")
        elif percent_pass >= 50:
            print(f"{TermColors.BOLD}{TermColors.WARNING}{percent_pass}%{TermColors.ENDC}{TermColors.BOLD} ({self.passes}/{len(self.tests)}) of tests are passing{TermColors.ENDC}\n")
        else:
            print(f"{TermColors.BOLD}{TermColors.FAIL}{percent_pass}%{TermColors.ENDC}{TermColors.BOLD} ({self.passes}/{len(self.tests)}) of tests are passing{TermColors.ENDC}\n")
        

class Regression:
    def __init__(self, name):
        self.suites = []
        self.suite_times = {}
        self.tests = 0
        self.passes = 0
        self.name = name

    def add_suite(self, suite):
        self.suites.append(suite)

    def run(self):
        print(f"{TermColors.BOLD}{TermColors.HEADER}--- Starting {self.name} Regression ---{TermColors.ENDC}{TermColors.ENDC}\n")
        
        self.start = timeit.default_timer()
        
        for suite in self.suites:
            suite_start = timeit.default_timer()
            suite.run()
            suite_end = timeit.default_timer()
            
            self.suite_times[suite.name] = round(suite_end - suite_start, 4)
            self.passes += suite.passes
            self.tests += len(suite.tests)

        self.stop = timeit.default_timer()

        self.print_results()

    def print_results(self):
        for key in self.suite_times.keys():
            print(f"Suite {key}: {self.suite_times[key]} sec.")
        print(f"{TermColors.BOLD}--- Finshed all ({len(self.suites)}) test suites in {round(self.stop - self.start, 4)} sec.{TermColors.ENDC} ---")
        
        percent_pass = round(self.passes/self.tests, 2) * 100
        if percent_pass == 100:
            print(f"\n{TermColors.BOLD}{TermColors.OKGREEN}{percent_pass}%{TermColors.ENDC}{TermColors.BOLD} ({self.passes}/{self.tests}) of total tests are passing{TermColors.ENDC}")
        elif percent_pass >= 50:
            print(f"\n{TermColors.BOLD}{TermColors.WARNING}{percent_pass}%{TermColors.ENDC}{TermColors.BOLD} ({self.passes}/{self.tests}) of total are passing{TermColors.ENDC}")
        else:
            print(f"\n{TermColors.BOLD}{TermColors.FAIL}{percent_pass}%{TermColors.ENDC}{TermColors.BOLD} ({self.passes}/{self.tests}) of total are passing{TermColors.ENDC}")
        
        print(f"{TermColors.BOLD}{TermColors.HEADER}--- End of Regression ---{TermColors.ENDC}{TermColors.ENDC}\n")


### Main ###

if __name__ == '__main__':
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
    him_regr.add_suite(db_suite)
    him_regr.run()
