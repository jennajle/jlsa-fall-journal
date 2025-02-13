"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
from http import HTTPStatus

from flask import Flask  # , request
from flask_restx import Resource, Api, fields  # Namespace, fields
from flask_cors import CORS
import werkzeug.exceptions as wz
import data.roles as rls

from flask import request

import data.people as ppl
import data.manuscripts as manu

app = Flask(__name__)
CORS(app)
api = Api(app)

person_model = api.model('Person', {
    'name': fields.String(required=True, description='The person\'s name',
                          min_length=2),
    'role': fields.String(description='The roles of the person',
                         default=''),
    'affiliation': fields.String(description='The affiliation of the person',
                                 default=''),
    'email': fields.String(required=True,
                           description='The email of the person'),
})

multi_role_person_model = api.model('MultiRolePerson', {
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
MANU_EP = '/manuscripts'


MESSAGE = 'Message'
RETURN = 'return'


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


@api.route(ENDPOINT_EP)
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
    This class handles creating, reading, updating
    and deleting the journal title.
    """
    def get(self):
        """
        This method provides the title, editor names,
        and publication date of the journal.
        """
        return {
            TITLE_RESP: TITLE,
            EDITORS_RESP: EDITORS,
            DATE_RESP: DATE
        }


@api.route(PEOPLE_EP)
class People(Resource):
    """
    This class handles creating, reading, updating
    and deleting journal people.
    """
    def get(self):
        """
        This method lists all persons.
        """
        try:
            people = ppl.read()
            if not people:
                return {MESSAGE: 'No people found in the database.'}, 404
            return people, 200
        except Exception as e:
            print(f"Error in get(): {e}")
            return {MESSAGE: 'Internal server error'}, 500

    @api.doc('create_person')
    @api.expect(person_model)
    @api.response(201, 'Person created successfully')
    @api.response(400, 'Invalid input or person already exists')
    def post(self):
        """
        This method creates a new person.
        """
        try:
            form_data = request.json
            name = form_data.get('name')
            affiliation = form_data.get('affiliation')
            email = form_data.get('email')
            role = form_data.get('role')
            ret = ppl.create_person(name, affiliation, email, role)
            return {MESSAGE:
                    'Person created successfully', 'Person': ret}, 201
        except ValueError as e:
            return {MESSAGE: str(e)}, 400

    @api.doc('update_person')
    @api.expect(multi_role_person_model)
    @api.response(201, 'Person created successfully')
    @api.response(400, 'Invalid input or person does not exist')
    def put(self):
        """
        This method updates an existing person.
        """
        form_data = request.json
        name = form_data.get('name')
        affiliation = form_data.get('affiliation')
        email = form_data.get('email')
        roles = form_data.get('roles')
        ret = ppl.update(name, affiliation, email, roles)
        if ret is None:
            return {MESSAGE:
                    'Failed to create person, ' +
                    'person may not exist yet!'
                    }, 400

        return {MESSAGE: 'Person updated successfully', 'Person': ret}, 201


@api.route(f'{PEOPLE_EP}/<email>')
class Person(Resource):
    def get(self, email):
        """
        Retrieve a single person's info
        """
        person = ppl.read_one(email)
        if person:
            return person
        else:
            raise wz.NotFound(f'No such record: {email}')

    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_FOUND, 'No such person.')
    def delete(self, email):
        ret = ppl.delete(email)
        if ret is not None:
            return {
                MESSAGE: 'Person deleted successfully',
                'Deleted': ret
            }, HTTPStatus.OK
        else:
            raise wz.NotFound(f'No such person: {email}')


MASTHEAD = 'Masthead'


@api.route(f'{PEOPLE_EP}/masthead')
class Masthead(Resource):
    def get(self):
        return {MASTHEAD: ppl.get_masthead()}


@api.route(f'{PEOPLE_EP}/<_id>/roles/<role>')
class RoleManagement(Resource):
    def post(self, _id, role):
        """
        This method adds a specific role to a person.
        """
        person = ppl.read_one(_id)
        if not person:
            raise wz.NotFound(f"Person with email {_id} not found")

        try:
            ppl.add_role(_id, role)
            return {
                MESSAGE: (
                    f"Role {role} added successfully "
                    f"to person with email {_id}")
            }, 200
        except ValueError as e:
            return {MESSAGE: str(e)}, 400

    def delete(self, _id, role=None):
        """
         This method removes a specified role from a person,
         and all roles from a person if not specified.
        """
        person = ppl.read_one(_id)
        if not person:
            raise wz.NotFound(f"Person with email {_id} not found")

        try:
            if role:
                ppl.remove_role(_id, role)
                return {
                    MESSAGE: (
                        f"Role {role} removed successfully "
                        f"from person with email {_id}")
                }, 200
            else:
                ppl.clear_roles(_id)
                return {
                    MESSAGE: (
                        f"All roles removed successfully "
                        f"from person with email {_id}")
                }, 200
        except ValueError as e:
            return {MESSAGE: str(e)}, 400


@api.route(f'{PEOPLE_EP}/roles/<role>')
class RolePeople(Resource):
    def get(self, role):
        """
        This method retrieves all people with a specific role
        """
        if not rls.is_valid(role):
            return {MESSAGE: f'Invalid role: {role}'}, 400

        people = []
        for person in ppl.read().values():
            roles = person.get('roles', [])
            if role in roles:
                people.append(person)

        if not people:
            return {
                MESSAGE: f'No people found with role: {role}'}, 404
        return {role: people}, 200


MANU_ACTION_FLDS = api.model('ManuscriptAction', {
    manu.MANU_ID: fields.String,
    manu.CURR_STATE: fields.String,
    manu.ACTION: fields.String,
    manu.REFEREE: fields.String,
})


@api.route(f'{MANU_EP}/receive_action')
class ReceiveAction(Resource):
    """
    Receive an action for a manuscript.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(MANU_ACTION_FLDS)
    def put(self):
        """
        Receive an action for a manuscript.
        """
        try:
            manu_id = request.json.get(manu.MANU_ID)
            curr_state = request.json.get(manu.CURR_STATE)
            action = request.json.get(manu.ACTION)
            kwargs = {}
            kwargs[manu.REFEREE] = request.json.get(manu.REFEREE)
            ret = manu.handle_action(
                manu_id, curr_state, action, **kwargs)
        except Exception as err:
            raise wz.NotAcceptable(f'Bad action: ' f'{err=}')
        return {
            MESSAGE: 'Action received!',
            RETURN: ret,
        }


@api.route(f"{PEOPLE_EP}/search")
class PersonSearch(Resource):
    def get(self):
        """
        Search for people based on query parameters (name, email, or role).
        """
        query = request.args.get("query")
        if not query:
            return {MESSAGE: "No search query"}, HTTPStatus.BAD_REQUEST
        results = ppl.search(query)
        if not results:
            return {MESSAGE: "No matching people found"}, HTTPStatus.NOT_FOUND

        return results, HTTPStatus.OK
