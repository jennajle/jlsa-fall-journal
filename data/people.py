MIN_USER_NAME_LEN = 2
NAME = 'name'
ROLES = 'roles'
AFFILIATION = 'affiliation'
EMAIL = 'email'

TEST_EMAIL = 'jl12631@nyu.edu'
DEL_EMAIL = 'delete@nyu.edu'

TEST_PERSON_DICT = {
    TEST_EMAIL: {
        NAME: 'Jenna Le',
        ROLES: [],
        AFFILIATION: 'NYU',
        EMAIL: TEST_EMAIL,
    },
    DEL_EMAIL: {
        NAME: 'Another Person',
        ROLES: [],
        AFFILIATION: 'NYU',
        EMAIL: DEL_EMAIL,
    },
}

people = TEST_PERSON_DICT

def get_people():
    return people


def delete_person(_id):
    people = get_people()
    if _id in people:
        del people[_id]
        return _id
    else:
        return None

def create_person(form_data):
    people = get_people()
    email = form_data.get('email')
    new_id = email
    name = form_data.get('name')

    if email in TEST_PERSON_DICT:
        print("Person already exists")
        return None

    people[new_id] = {
        NAME: name,
        ROLES: form_data.get('roles', []),
        AFFILIATION: form_data.get('affiliation', ''),
        EMAIL: email,
    }
    return people[new_id]