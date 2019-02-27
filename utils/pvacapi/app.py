#!/usr/bin/env python3

import connexion
import os
import sys
import time
import argparse

from flask_cors import CORS
from utils.pvacapi.controllers.utils import initialize
from utils.pvacapi.controllers.utils import getIpAddress

#FIXME: sanitize sample name
def main():
    parser = argparse.ArgumentParser(description='pVACapi provides a REST API to pVACtools')
    parser.add_argument('--ip_address', help='IP address for the HTTP server to bind. If not provided, the default socket address will be used.')
    parser.add_argument('--debug', default=False, action='store_true', help='Start sever in debug mode.')
    args = parser.parse_args()

    app = connexion.App(
        "pVAC-Seq Visualization Server",
        specification_dir=os.path.join(
            os.path.dirname(__file__),
            'config'
        ),
    )

    from werkzeug.routing import IntegerConverter as BaseIntConverter
    class IntConverter(BaseIntConverter):
        regex = r'-?\d+'

    # determine IP address and setup CORS
    IP_ADDRESS = None
    if args.ip_address is None:
        IP_ADDRESS = getIpAddress()
    else:
        IP_ADDRESS = args.ip_address

    app.app.url_map.converters['int'] = IntConverter
    initialize(app.app, IP_ADDRESS) #initialize the app configuration
    app.add_api('swagger.yaml', arguments={'title': 'API to support pVacSeq user interface for generating reports on pipeline results'})
    app.app.secret_key = os.urandom(1024)

    # remove all CORS restrictions
    CORS(app.app)

    # should match IP address at with any port, path, or protocol
    # CORS(
    #     app.app,
    #     origins=r'^(.+://)?' + IP_ADDRESS + r'(:\d+)?(/.*)?$'
    # )

    print(time.asctime(), "Starting pVACapi server at http://" + IP_ADDRESS + ":8080")
    app.run(port=8080, debug=args.debug, threaded=True)

if __name__ == '__main__':
    main()
