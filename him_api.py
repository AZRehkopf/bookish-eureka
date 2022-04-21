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
        self.logger = logging.getLogger(__name__)

    def on_get(self, req, resp):
        resp_json = self.check_status()

        resp.status = falcon.HTTP_200  # This is the default status
        resp.media = resp_json

    def check_status(self):
        status = {
            'status': True,
            'data': {
                'api': True
            }
        }

        return status


### Main ###

if __name__ == '__main__':
    configure_logging(logging.INFO)
    
    app = falcon.App()
    status = SystemStatus()
    app.add_route('/status', status)
    
    with make_server('', API_PORT, app) as httpd:
        logging.info(f"HIM API is starting on port {API_PORT}")

        # Serve until process is killed
        httpd.serve_forever()