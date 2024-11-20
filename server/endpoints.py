"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask  # , request
from flask_restx import Resource, Api, fields  # Namespace, fields
from flask_cors import CORS
import werkzeug.exceptions as wz

from flask import request

import data.people as ppl

app = Flask(__name__)
CORS(app)
api = Api(app)

person_model = api.model('Person', {
    'name': fields.String(required=True, description='The person\'s name',
                          min_length=2),
    'roles': fields.List(fields.String, description='The roles of the person',
                         default=[]),
    'affiliation': fields.String(description='The affiliation of the person',
                                 default=''),
    'email': fields.String(required=True,
                           description='The email of the person'),
})

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
        """
        This method lists all persons
        """
        return ppl.get_people()

    @api.doc('create_person')
    @api.expect(person_model)
    @api.response(201, 'Person created successfully')
    @api.response(400, 'Invalid input or person already exists')
    def post(self):
        """
        This method creates a person
        """
        form_data = request.json
        ret = ppl.create_person(form_data)
        if ret is None:
            return {'Message':
                    'Failed to create person, ' +
                    'person may already exist or data is invalid'
                    }, 400

        return {'Message': 'Person created successfully', 'Person': ret}, 201

    @api.doc('update_person')
    @api.expect(person_model)
    @api.response(201, 'Person created successfully')
    @api.response(400, 'Invalid input or person does not exist')
    def put(self):
        """
        This method updates an existing person
        """
        form_data = request.json
        ret = ppl.update_person(form_data)
        if ret is None:
            return {'Message':
                    'Failed to create person, ' +
                    'person may not exist yet!'
                    }, 400

        return {'Message': 'Person updated successfully', 'Person': ret}, 201


@api.route(f'{PEOPLE_EP}/<_id>')
class Person(Resource):
    def delete(self, _id):
        """
        This method deletes a person
        """
        ret = ppl.delete_person(_id)
        return {'Message': 'Person deleted successfully', 'Person': ret}

    def get(self, _id):
        """
        Retrieve a single person's info
        """
        person = ppl.read_one(_id)
        if person:
            return person
        else:
            return {'Message':
                    'Failed to retrieve person!'
                    }, 404


MASTHEAD = 'Masthead'


@api.route(f'{PEOPLE_EP}/masthead')
class Masthead(Resource):
    def get(self):
        return {MASTHEAD: ppl.get_masthead()}


@api.route(f'{PEOPLE_EP}/<_id>/roles/<role>')
class RoleManagement(Resource):
    def post(self, _id, role):
        """
        This method adds a role to a person.
        """
        person = ppl.read_one(_id)
        if not person:
            raise wz.NotFound(f"Person with email {_id} not found")

        try:
            ppl.add_role(_id, role)
            return {
                'Message': (
                    f"Role {role} added successfully "
                    f"to person with email {_id}")
            }, 200
        except ValueError as e:
            return {'Message': str(e)}, 400

    def delete(self, _id, role):
        """
         This method removes a role from a person.
        """
        person = ppl.read_one(_id)
        if not person:
            raise wz.NotFound(f"Person with email {_id} not found")

        try:
            ppl.remove_role(_id, role)
            return {
                'Message': (
                    f"Role {role} removed successfully "
                    f"from person with email {_id}")
            }, 200
        except ValueError as e:
            return {'Message': str(e)}, 400
