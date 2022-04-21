# him_api.py
# Restful API implemntation for the House Inventory Managment (HIM) 

### Imports ###

# Built-ins
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from wsgiref.simple_server import make_server

# Third Party
import falcon
import psycopg2
from psycopg2 import Error

### Constants ###
API_PORT = 8765
LOG_DIRECTORY = "/home/pi/python/him_api/logs"
LOG_FILE_NAME = "him.log"

### Functions ###

def configure_logging(verbosity):
    logging.basicConfig(
        level=verbosity,
        format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(
                os.path.join(LOG_DIRECTORY, LOG_FILE_NAME),
                maxBytes=100000,
                backupCount=5
            )
        ]
    )

### Classes ###
class RequireJSON:
    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                description='This API only supports responses encoded as JSON.'
            )

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    title='This API only supports requests encoded as JSON.'
                )


class SystemStatus:
    def __init__(self):
        self.logger = logging.getLogger('status')

    def on_get(self, req, resp):
        resp_json = self.check_status()

        resp.status = falcon.HTTP_200  # This is the default status
        resp.media = resp_json
        self.logger.info(f"Served status to {req.remote_addr} via {req.scheme}")

    def check_status(self):
        api_status = True
        db_status = self.check_db_connection()
        sys_status = api_status & db_status
        
        status = {
            'status': sys_status,
            'data': {
                'api': api_status,
                'db': db_status
            }
        }

        return status

    def check_db_connection(self):
        try:
            connection = psycopg2.connect(
                user="pi",
                password="evolution-finch-genes",
                host="127.0.0.1",
                port="5432",
                database="him_db")

            cursor = connection.cursor()
            cursor.execute("SELECT version();")
            cursor.fetchone()
            cursor.close()
            connection.close()
            return True

        except (Exception, Error) as error:
            self.logger.error(f"Error while connecting to DB: {error}")
            return False


class DatabaseEngine:
    def __init__(self):
        self.logger = logging.getLogger('dbe')

    def on_post(self, req, resp):
        self.connect_to_db()
        self.logger.info(f"post with {req.media} received")
        
        try:
            print(req.media['method'])
        except KeyError:
            resp.status = falcon.HTTP_BAD_REQUEST

        self.disconnect_from_db()

    def connect_to_db(self):
        try:
            self.connection = psycopg2.connect(
                user="pi",
                password="evolution-finch-genes",
                host="127.0.0.1",
                port="5432",
                database="him_db")

            self.cursor = self.connection.cursor()
            db_info = self.connection.get_dsn_parameters()
            self.db_name = db_info['dbname']
            self.logger.info(f"Connected to {self.db_name} as user {db_info['user']} on port {db_info['port']}")
            self.cursor.execute("SELECT version();")
            self.cursor.fetchone()

        except (Exception, Error) as error:
            self.logger.error(f"Error while connecting to DB: {error}")

    def disconnect_from_db(self):
        if (self.connection):
            self.cursor.close()
            self.connection.close()
            self.logger.info(f"Closed connection to {self.db_name}")
        

### Main ###

if __name__ == '__main__':
    configure_logging(logging.INFO)
    
    him = falcon.App(
        middleware=[
            RequireJSON()
        ]
    )
    
    status = SystemStatus()
    dbe = DatabaseEngine()
    
    him.add_route('/status', status)
    him.add_route('/data', dbe)
    
    with make_server('', API_PORT, him) as httpd:
        logging.info(f"HIM API is starting on port {API_PORT}")

        # Serve until process is killed
        httpd.serve_forever()