import data.manuscripts.fields as flds

COPY_EDIT = 'CED'
IN_REF_REV = 'REV'
REJECTED = 'REJ'
SUBMITTED = 'SUB'
TEST_STATE = SUBMITTED

VALID_STATES = [
    AUTHOR_REV,
    COPY_EDIT,
    IN_REF_REV,
    REJECTED,
    SUBMITTED,
]



SAMPLE_MANU = {
    flds.TITLE: 'Short module import names in Python',
    flds.AUTHOR: '',
    flds.REFEREES: [],
}


def get_states() -> list:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


# actions:
ACCEPT = 'ACC'
ASSIGN_REF = 'ARF'
DONE = 'DON'
REJECT = 'REJ'
# for testing:
TEST_ACTION = ACCEPT

VALID_ACTIONS = [
    ACCEPT,
    ASSIGN_REF,
    DONE,
    REJECT,
]

# can redefine and append more valid actions later on
VALID_ACTIONS_FOR_STATE = {
    'SUB': ['ARF', 'REJ'],
    'REV': ['ACC', 'REJ'],
    'CED': [],
    'REJ': [],
}


def get_actions() -> list:
    return VALID_ACTIONS


def is_valid_action(action: str) -> bool:
    return action in VALID_ACTIONS


def sub_assign_ref(manu: dict) -> str:
    return IN_REF_REV


FUNC = 'f'

STATE_TABLE = {
    SUBMITTED: {
        ASSIGN_REF: {
            FUNC: lambda m: IN_REF_REV,
        },
        REJECT: {
            FUNC: lambda m: REJECTED,
        },
    },
    IN_REF_REV: {
    },
    COPY_EDIT: {
        DONE: {
            FUNC: lambda m: AUTHOR_REV,
        },
    },
    AUTHOR_REV: {
    },
    REJECTED: {
    },
}
