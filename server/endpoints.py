"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask  # , request
from flask_restx import Resource, Api  # Namespace, fields
from flask_cors import CORS

# import werkzeug.exceptions as wz

import data.people as ppl

app = Flask(__name__)
CORS(app)
api = Api(app)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
TITLE_EP = '/title'
TITLE_RESP = 'Title'
TITLE = '...'
EDITORS_RESP = 'Editors'
EDITORS = 'Alex, Leo, Jenna, Sejuti'
DATE_RESP = 'Date'
DATE = '2024-10-02'
PEOPLE_EP = '/people'


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        It just answers with "hello world."
        """
        return {HELLO_RESP: 'world'}


@api.route('/endpoints')
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route(TITLE_EP)
class JournalTitle(Resource):
    """
    This class will give the name of the journal.
    """
    def get(self):
        """
        The 'get()' method will return the name of the journal.
        """
        return {
            TITLE_RESP: TITLE,
            EDITORS_RESP: EDITORS,
            DATE_RESP: DATE
        }


@api.route(PEOPLE_EP)
class People(Resource):
    def get(self):
        return ppl.get_people()


@api.route(f'{PEOPLE_EP}/<_id>')
class Person(Resource):
    def delete(self, _id):
        ret = ppl.delete_person(_id)
        return {'Message': ret}
    def post(self, _id):
        ret = ppl.create_person(_id)
        return {'Message': ret}

