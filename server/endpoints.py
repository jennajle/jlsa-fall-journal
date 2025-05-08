"""
This is the file containing all the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
from http import HTTPStatus

from flask import Flask, request
from flask_restx import Resource, Api, fields
from flask_cors import CORS
from bson import ObjectId
import werkzeug.exceptions as wz
from werkzeug.security import generate_password_hash

import data.roles as rls
import data.people as ppl
import data.manuscripts as manu
from data.db_connect import create, read, delete, update, fetch_one

import subprocess  # Need for developer endpoint
import security.security as sec

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
    'password': fields.String(required=False, description='Password'),
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
TEXT_EP = '/text'
ROLES_EP = '/roles'

MESSAGE = 'Message'
RETURN = 'return'


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
                return {}, HTTPStatus.OK  # Return empty instead of error
            return people, HTTPStatus.OK
        except Exception as e:
            print(f"Error in get(): {e}")
            return ({MESSAGE: 'Internal server error'},
                    HTTPStatus.INTERNAL_SERVER_ERROR)

    @api.doc('create_person')
    @api.expect(multi_role_person_model)
    @api.response(HTTPStatus.CREATED, 'Person created successfully')
    @api.response(HTTPStatus.BAD_REQUEST,
                  'Invalid input or person already exists')
    def post(self):
        """
        This method creates a new person.
        """
        try:
            form_data = request.json
            name = form_data.get('name')
            affiliation = form_data.get('affiliation')
            email = form_data.get('email')
            roles = form_data.get('roles')
            password = form_data.get('password')
            if password:
                password_hash = generate_password_hash(password)
            else:
                password_hash = None
            ret = ppl.create_person(name, affiliation, email,
                                    roles, password_hash)
            return ({MESSAGE:
                    'Person created successfully', 'Person': ret},
                    HTTPStatus.CREATED)
        except ValueError as e:
            api.abort(HTTPStatus.BAD_REQUEST, message=str(e))

    @api.doc('update_person')
    @api.expect(multi_role_person_model)
    @api.response(HTTPStatus.OK, 'Person updated successfully')
    @api.response(HTTPStatus.BAD_REQUEST,
                  'Invalid input or person does not exist')
    @api.response(HTTPStatus.CREATED, 'Another person already has this email')
    def put(self):
        """
        This method updates an existing person and
        differentiates between old and new email.
        """
        form_data = request.json
        name = form_data.get('name')
        affiliation = form_data.get('affiliation')
        new_email = form_data.get('email')
        roles = form_data.get('roles')

        # Old email from query parameters
        old_email = request.args.get('old_email')

        current_person = ppl.read_one(old_email)
        if not current_person:
            raise wz.BadRequest(f"No person found with email {old_email}")

        # Check for duplicates
        if new_email != old_email:
            another_person = ppl.read_one(new_email)
            if another_person:
                raise wz.Conflict(
                    f"Another person already has the email {new_email}"
                )

        try:
            ret = ppl.update(old_email, name, affiliation, new_email, roles)
            return ({MESSAGE: 'Person updated successfully', 'Person': ret},
                    HTTPStatus.OK)
        except ValueError as e:
            raise wz.BadRequest(str(e))


@api.route(f'{PEOPLE_EP}/delete/<string:email>/<string:user_id>')
class DeletePerson(Resource):
    """
    Delete person with user SECURITY login check.
    """
    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_FOUND, 'No such person.')
    @api.response(HTTPStatus.FORBIDDEN, 'Not authorized.')
    def delete(self, email, user_id):
        """
        Delete a person from email and user id
        """
        kwargs = {sec.LOGIN_KEY: 'any-login-key-for-now'}
        if not sec.is_permitted(sec.PEOPLE, sec.DELETE, user_id, **kwargs):
            raise wz.Forbidden(
                'You do not have permission to delete this person.')

        ret = ppl.delete(email)
        if ret is not None:
            return {
                MESSAGE: 'Person deleted successfully',
                'Deleted': ret
            }, HTTPStatus.OK
        else:
            raise wz.NotFound(f'No such person: {email}')


@api.route(f'{PEOPLE_EP}/<string:email>')
class GetPerson(Resource):
    """
    Retrieve a journal person's info (no security).
    """
    def get(self, email):
        person = ppl.read_one(email)
        if person:
            return person
        else:
            raise wz.NotFound(f'No such record: {email}')


MASTHEAD = 'Masthead'


@api.route(f'{PEOPLE_EP}/masthead')
class Masthead(Resource):
    def get(self):
        """
        Returns the journal masthead.
        """
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
            }, HTTPStatus.OK
        except ValueError as e:
            return {MESSAGE: str(e)}, HTTPStatus.BAD_REQUEST

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
                }, HTTPStatus.OK
            else:
                ppl.clear_roles(_id)
                return {
                    MESSAGE: (
                        f"All roles removed successfully "
                        f"from person with email {_id}")
                }, HTTPStatus.OK
        except ValueError as e:
            return {MESSAGE: str(e)}, HTTPStatus.BAD_REQUEST


@api.route(f'{PEOPLE_EP}/roles/<role>')
class RolePeople(Resource):
    def get(self, role):
        """
        This method retrieves all people with a specific role
        """
        if not rls.is_valid(role):
            return {MESSAGE: f'Invalid role: {role}'}, HTTPStatus.BAD_REQUEST

        people = []
        for person in ppl.read().values():
            roles = person.get('roles', [])
            if role in roles:
                people.append(person)

        if not people:
            return ({
                MESSAGE: f'No people found with role: {role}'},
                    HTTPStatus.NOT_FOUND)
        return {role: people}, HTTPStatus.OK


MANU_ACTION_FLDS = api.model('ManuscriptAction', {
    manu.MANU_ID: fields.String,
    manu.CURR_STATE: fields.String,
    manu.ACTION: fields.String,
    manu.REFEREE: fields.String,
})


@api.route(f'{MANU_EP}/receive_action')
class ReceiveAction(Resource):
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
            referee = request.json.get(manu.REFEREE)

            manuscript = fetch_one("manuscripts", {"_id": ObjectId(manu_id)})
            if not manuscript:
                raise ValueError("Manuscript not found")

            history = manuscript.get("history", [])
            ret = manu.handle_action(
                manu_id, curr_state, action, manu=manuscript, referee=referee
            )
            new_state = ret.get("new_state")
            history.append(curr_state)
            update_fields = {
                "state": new_state,
                "history": history,
                "referees": manuscript.get("referees", [])
            }
            update_res = update(
                "manuscripts", {"_id": ObjectId(manu_id)}, update_fields
            )

        except Exception as err:
            raise wz.NotAcceptable(f'Bad action: ' f'{err=}')
        if update_res:
            return {
                MESSAGE: 'Action received!',
                RETURN: ret,
            }


manuscript_model = api.model('Manuscript', {
    'title': fields.String(required=True, description="Manuscript title"),
    'author': fields.String(required=True,
                            description="Author of the manuscript"),
    'author_email': fields.String(required=True,
                                  description="Author of the manuscript"),
    'state': fields.String(required=True, description="Current state"),
    'abstract': fields.String(required=True,
                              description="Manuscript abstract"),
    'text': fields.String(required=False,
                          description="Content of the manuscript"),
    'referees': fields.List(fields.String,
                            description="List of referees", default=[]),
    'history': fields.List(fields.Raw,
                           description="Manuscript history", default=[]),
})


@api.route(MANU_EP)
class Manuscripts(Resource):
    @api.expect(manuscript_model)
    def post(self):
        """Create a new manuscript"""
        data = request.json

        required_fields = ['title',
                           'author', 'author_email',
                           'abstract', 'text']
        missing_fields = [field
                          for field in required_fields
                          if not data.get(field)]

        if missing_fields:
            raise wz.BadRequest(
                f"Manuscript missing required fields: "
                f"{', '.join(missing_fields)}"
            )

        try:
            manuscript = {
                'title': data.get('title'),
                'author': data.get('author'),
                'author_email': data.get('author_email'),
                'state': data.get('state', 'SUB'),
                'abstract': data.get('abstract'),
                'text': data.get('text'),
                'referees': data.get('referees', []),
                'history': []
            }

            result = create('manuscripts', manuscript)
            return {MESSAGE: 'Manuscript created',
                    'id': str(result.inserted_id)}, HTTPStatus.CREATED
        except Exception:
            raise wz.InternalServerError(
                "Failed to create manuscript due to a server error.")

    def get(self):
        """Get all manuscripts"""
        try:
            manuscripts = read('manuscripts', no_id=False)
            for manuscript in manuscripts:
                manuscript['manu_id'] = str(manuscript['_id'])
            return manuscripts, HTTPStatus.OK
        except Exception as e:
            raise wz.InternalServerError(
                f"Error fetching manuscripts: {str(e)}")


@api.route(f'{MANU_EP}/<string:id>')
class ManuscriptById(Resource):
    def delete(self, id):
        """Delete a manuscript by MongoDB _id"""
        try:
            delete_count = delete('manuscripts', {'_id': ObjectId(id)})
            if delete_count > 0:
                return {MESSAGE: 'Manuscript deleted'}, HTTPStatus.OK
            else:
                return ({MESSAGE: 'Manuscript not found'},
                        HTTPStatus.NOT_FOUND)
        except Exception as e:
            print(f"Error in delete(): {e}")
            return ({MESSAGE: 'Internal server error'},
                    HTTPStatus.INTERNAL_SERVER_ERROR)

    def get(self, id):
        """Retrieve a manuscript by MongoDB _id"""
        try:
            manuscript = fetch_one("manuscripts", {"_id": ObjectId(id)})
            if manuscript:
                return manuscript, HTTPStatus.OK
            else:
                return ({MESSAGE: 'Manuscript not found'},
                        HTTPStatus.NOT_FOUND)
        except Exception as e:
            print(f"Error in get(): {e}")
            return ({MESSAGE: 'Invalid ID format or internal server error'},
                    HTTPStatus.BAD_REQUEST)


text_model = api.model('Text', {
    'title': fields.String(required=True, description="Text title"),
    'content': fields.String(required=True, description="Content of the text"),
})


@api.route(f"{MANU_EP}/<string:id>/available_actions")
class ActionsForManuscript(Resource):
    def get(self, id):
        """Return actions specific to manuscript's state and user role"""
        try:
            manuscript = fetch_one("manuscripts", {"_id": ObjectId(id)})
            if not manuscript:
                raise ValueError("Manuscript not found")

            email = request.args.get("user_id")
            user = ppl.read_one(email)
            if not user:
                raise wz.NotFound(f"No user found with email: {email}")

            role_codes = user.get("roles", [])
            available_actions = manu.get_available_actions(manuscript)

            # check if current user is author of manuscript
            if ((rls.AUTHOR_CODE in role_codes) and
                    (manuscript.get(manu.AUTHOR_EMAIL) != email)):
                author_only = manu.ROLE_PERMISSIONS.get(rls.AUTHOR_CODE, set())
                available_actions = [action for action in available_actions
                                     if action not in author_only]

            role_actions = manu.filter_actions_by_roles(available_actions,
                                                        role_codes)
            return role_actions, HTTPStatus.OK
        except Exception as e:
            return {"message": str(e)}, HTTPStatus.BAD_REQUEST


@api.route(f"{MANU_EP}/<string:id>/history")
class ManuscriptHistory(Resource):
    def get(self, id):
        """Return the state history of manuscript"""
        try:
            manuscript = fetch_one("manuscripts", {"_id": ObjectId(id)})
            if not manuscript:
                raise ValueError("Manuscript not found")
            return manu.get_history(manuscript), HTTPStatus.OK
        except Exception as e:
            return {"message": str(e)}, HTTPStatus.BAD_REQUEST


@api.route(f'{MANU_EP}/metadata')
class ManuscriptMetadata(Resource):
    def get(self):
        """
        Return mappings of state and action codes for frontend display
        """
        return {
            "state_names": manu.get_state_display_names(),
            "action_names": manu.get_action_display_names()
        }, HTTPStatus.OK


@api.route(TEXT_EP)
class Texts(Resource):
    @api.expect(text_model)
    def post(self):
        """Create a new text document"""
        data = request.json
        text_doc = {
            'title': data.get('title'),
            'content': data.get('content'),
        }

        result = create('texts', text_doc)
        if result is not None:
            return {MESSAGE: 'Text created'}, HTTPStatus.CREATED

    def get(self):
        """Get all text documents"""
        try:
            texts = read('texts')
            return texts, HTTPStatus.OK
        except Exception as e:
            print(f"Error in get(): {e}")
            return ({MESSAGE: 'Internal server error'},
                    HTTPStatus.INTERNAL_SERVER_ERROR)


@api.route(f'{TEXT_EP}/<string:title>')
class TextByTitle(Resource):
    def get(self, title):
        """Get the content of a text by title"""
        try:
            texts = read('texts')
            text_doc = next((text for text in texts if text['title'] == title),
                            None)
            if text_doc:
                return {
                    'title': text_doc['title'], 'content': text_doc['content']
                }, HTTPStatus.OK
            else:
                return {MESSAGE: 'Text not found'}, HTTPStatus.NOT_FOUND
        except Exception as e:
            print(f"Error in get(): {e}")
            return ({MESSAGE: 'Internal server error'},
                    HTTPStatus.INTERNAL_SERVER_ERROR)

    def delete(self, title):
        """Delete a text by its title"""
        try:
            existing_text = fetch_one('texts', {'title': title})
            if existing_text:
                delete('texts', {'title': title})
                return ({MESSAGE: 'Text deleted successfully'},
                        HTTPStatus.OK)
            else:
                return {MESSAGE: 'Text not found'}, HTTPStatus.NOT_FOUND
        except Exception as e:
            print(f"Error in delete(): {e}")
            return ({MESSAGE: 'Internal server error'},
                    HTTPStatus.INTERNAL_SERVER_ERROR)

    @api.expect(text_model)
    def put(self, title):
        """Update the content of a text by title"""
        try:
            existing_text = fetch_one('texts', {'title': title})
            if existing_text:
                new_content = request.json.get('content')
                if new_content:
                    update('texts', {'title': title}, {'content': new_content})
                    return ({MESSAGE: 'Text updated successfully'},
                            HTTPStatus.OK)
                else:
                    return ({MESSAGE: 'New content not provided'},
                            HTTPStatus.BAD_REQUEST)
            else:
                return {MESSAGE: 'Text not found'}, HTTPStatus.NOT_FOUND
        except Exception as e:
            print(f"Error in put(): {e}")
            return ({MESSAGE: 'Internal server error'},
                    HTTPStatus.INTERNAL_SERVER_ERROR)


@api.route(ROLES_EP)
class Roles(Resource):
    """
    This class handles reading person roles.
    """
    def get(self):
        """
        Retrieve the journal person roles.
        """
        return rls.read()


LOG_DIR = '/var/log'
DEV_ERROR_LOG_EP = '/dev/error_logs'
ELOG_LOC = '/var/log/sejutimannan.pythonanywhere.com.error.log'


@api.route(DEV_ERROR_LOG_EP)
class DevLogs(Resource):
    def get(self):
        """
        Developer endpoint to view the error log from Python Anywhere.
        """
        try:
            # show last 50 lines of the error log file
            result = subprocess.run(f'tail -n 50 {ELOG_LOC}', shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)

            if result.returncode != 0:
                return {
                    MESSAGE: 'Failed to read logs',
                    'error': result.stderr.strip()
                }, HTTPStatus.INTERNAL_SERVER_ERROR

            return ({'log_output': result.stdout.strip().split('\n')},
                    HTTPStatus.OK)

        except Exception as e:
            return ({MESSAGE: f'Error reading logs: {str(e)}'},
                    HTTPStatus.INTERNAL_SERVER_ERROR)
