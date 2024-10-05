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


def get_people():
    people = TEST_PERSON_DICT
    return people


def delete_person(_id):
    people = get_people()
    if _id in people:
        del people[_id]
        return _id
    else:
        return None
