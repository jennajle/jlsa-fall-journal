import data.manuscripts.fields as flds
import data.roles as rls

ACTION = 'action'
AUTHOR = 'author'
CURR_STATE = 'curr_state'
DISP_NAME = 'disp_name'
MANU_ID = '_id'
REFEREE = 'referee'
REFEREES = 'referees'
TITLE = 'title'

TEST_ID = 'fake_id'
TEST_FLD_NM = TITLE
TEST_FLD_DISP_NM = 'Title'

FIELDS = {
    TITLE: {
        DISP_NAME: TEST_FLD_DISP_NM,
    },
}

# states
REJECTED = 'REJ'
SUBMITTED = 'SUB'
WITHDRAWN = 'WIT'
IN_REF_REV = 'REV'
AUTHOR_REVISIONS = 'AUR'
EDITOR_REV = 'ERV'
COPY_EDIT = 'CED'
AUTHOR_REVIEW = 'ARE'
FORMATTING = "FMT"
PUBLISHED = "PUB"

TEST_STATE = SUBMITTED

VALID_STATES = [
    REJECTED,
    SUBMITTED,
    WITHDRAWN,
    IN_REF_REV,
    AUTHOR_REVISIONS,
    EDITOR_REV,
    COPY_EDIT,
    AUTHOR_REVIEW,
    FORMATTING,
    PUBLISHED,
]



SAMPLE_MANU = {
    flds.TITLE: 'Short module import names in Python',
    flds.AUTHOR: 'jlsa',
    flds.REFEREES: [],
    'history': [] # track what states the manuscript went through
}

SAMPLE_MANU_W_REF = {
    flds.TITLE: 'Short module import names in Python',
    flds.AUTHOR: 'jlsa',
    flds.REFEREES: ['Some ref'],
    'history': [] # track what states the manuscript went through
}

def get_states() -> list:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


# actions:
ASSIGN_REF = 'ARF'
DONE = 'DON'
REJECT = 'REJ'
DELETE_REF = 'DRF'
WITHDRAW = 'WIT'
ACCEPT = 'ACC'
ACCEPT_REV = 'ACR'
SUBMIT_REVIEW = 'SRV'
# for testing:
TEST_ACTION = ACCEPT

VALID_ACTIONS = [
    ASSIGN_REF,
    DONE,
    REJECT,
    WITHDRAW,
    DELETE_REF,
    ACCEPT,
    ACCEPT_REV,
    SUBMIT_REVIEW,
]

# used for the frontend display
STATE_DISPLAY_NAMES = {
    SUBMITTED: "Submitted",
    IN_REF_REV: "In Referee Review",
    AUTHOR_REVISIONS: "Author Revisions",
    EDITOR_REV: "Editor Review",
    COPY_EDIT: "Copy Editing",
    AUTHOR_REVIEW: "Author Review",
    FORMATTING: "Formatting",
    WITHDRAWN: "Withdrawn",
    REJECTED: "Rejected",
    PUBLISHED: "Published",
}

ACTION_DISPLAY_NAMES = {
    ASSIGN_REF: "Assign Referee",
    DELETE_REF: "Delete Referee",
    REJECT: "Reject",
    WITHDRAW: "Withdraw",
    DONE: "Done",
    ACCEPT: "Accept",
    ACCEPT_REV: "Accept with Revisions",
    SUBMIT_REVIEW: "Submit Review",
}

ROLE_PERMISSIONS = {
    rls.ED_CODE: {ASSIGN_REF, DELETE_REF, DONE, REJECT, ACCEPT, ACCEPT_REV},
    rls.CE_CODE: {ASSIGN_REF, DELETE_REF, DONE, REJECT, ACCEPT, ACCEPT_REV},
    rls.ME_CODE: {ASSIGN_REF, DELETE_REF, DONE, REJECT, ACCEPT, ACCEPT_REV},
    rls.AUTHOR_CODE: {WITHDRAW, DONE},
    rls.RE_CODE: {SUBMIT_REVIEW},
}


def get_actions() -> list:
    return VALID_ACTIONS


def is_valid_action(action: str) -> bool:
    return action in VALID_ACTIONS


def submitted(manu: dict):
    print(f"Manuscript '{manu[flds.TITLE]}' is SUBMITTED")
    manu['state'] = SUBMITTED
    add_to_history(manu, None, 'SUBMIT', SUBMITTED)
    return SUBMITTED


def assign_ref(manu: dict, referee: str, extra=None) -> str:
    manu[REFEREES].append(referee)
    return IN_REF_REV


def delete_ref(manu: dict, referee: str) -> str:
    if referee in manu[flds.REFEREES]:
        manu[REFEREES].remove(referee)
    if len(manu[flds.REFEREES]) == 0:
        return SUBMITTED
    else:
        return IN_REF_REV

# if kwargs is not added
# test_handle_action_valid_return -
# TypeError: accept_with_revisions() got an unexpected keyword argument 'referee'
def accept(manu: dict,  extra=None, **kwargs) -> str :
    return COPY_EDIT


FUNC = 'f'

COMMON_ACTIONS = {
    WITHDRAW: {
        FUNC: lambda **kwargs: WITHDRAWN,
    },
}

STATE_TABLE = {
    SUBMITTED: {
        ASSIGN_REF: {
            FUNC: assign_ref,
        },
        REJECT: {
            FUNC: lambda **kwargs: REJECTED,
        },
        **COMMON_ACTIONS,
    },
    IN_REF_REV: {
        ASSIGN_REF: {
            FUNC: assign_ref,
        },
        DELETE_REF: {
            FUNC: delete_ref,
        },
        REJECT: {
            FUNC: lambda **kwargs: REJECTED,
        },
        ACCEPT: {
            FUNC: accept,
        },
        ACCEPT_REV: {
            FUNC: lambda **kwargs: AUTHOR_REVISIONS,
        },
        SUBMIT_REVIEW: {
            FUNC: lambda **kwargs: IN_REF_REV
        },
        **COMMON_ACTIONS,
    },
    AUTHOR_REVISIONS: {
        DONE: {
            FUNC: lambda **kwargs: EDITOR_REV,
        },
        **COMMON_ACTIONS,
    },
    REJECTED: {
        **COMMON_ACTIONS,
    },
    WITHDRAWN: {
        **COMMON_ACTIONS,
    },
    EDITOR_REV: {
        ACCEPT: {
            FUNC: accept,
        },
        **COMMON_ACTIONS,
    },
    COPY_EDIT: {
        DONE: {
            FUNC: lambda **kwargs: AUTHOR_REVIEW,
        },
        **COMMON_ACTIONS,
    },
    AUTHOR_REVIEW:{
        DONE: {
            FUNC: lambda **kwargs: FORMATTING,
        },
        **COMMON_ACTIONS,
    },
    FORMATTING: {
        DONE: {
            FUNC: lambda **kwargs: PUBLISHED,
        },
        **COMMON_ACTIONS,
    },
    PUBLISHED: {
        **COMMON_ACTIONS,
    },
}



def get_valid_actions_by_state(state: str):
    valid_actions = STATE_TABLE[state].keys()
    print(f'{valid_actions=}')
    return valid_actions


def add_to_history(manuscript: dict, curr_state: str, action: str, new_state: str):
    history = manuscript.setdefault('history', [])
    history.append({
        'from': curr_state,
        'action': action,
        'to': new_state,
    })


def reset_history(manuscript: dict):
    manuscript['history'] = []
    print("History has been reset.")


def handle_action(manu_id, curr_state, action, **kwargs) -> dict:
    if 'manu' not in kwargs:
        raise ValueError("Manuscript not provided")
    manu_dict = kwargs['manu']

    if curr_state not in STATE_TABLE:
        raise ValueError(f'Bad state: {curr_state}')
    if action not in STATE_TABLE[curr_state]:
        raise ValueError(f'{action} not available in {curr_state}')
    new_state = STATE_TABLE[curr_state][action][FUNC](**kwargs)
    if not isinstance(new_state, str):
        raise ValueError(f'Invalid state transition: {new_state}')
    return {"new_state": new_state}


def get_history(manu: dict):
    return manu.get('history', [])


def get_current_state(manu: dict) -> str:
    return manu.get('state', 'Unknown')


def get_available_actions(manu: dict):
    state = get_current_state(manu)
    if state in STATE_TABLE:
        return list(STATE_TABLE[state].keys())
    return []

def get_state_display_names():
    return STATE_DISPLAY_NAMES

def get_action_display_names():
    return ACTION_DISPLAY_NAMES

def filter_actions_by_roles(actions, role_codes):
    allowed = set()
    for code in role_codes:
        allowed.update(ROLE_PERMISSIONS.get(code, []))

    return [action for action in actions if action in allowed]


def main():
    print("Submitted")
    print(handle_action(TEST_ID, SUBMITTED, WITHDRAW))
    print(handle_action(TEST_ID, SUBMITTED, REJECT))
    print(handle_action(TEST_ID, SUBMITTED, ASSIGN_REF, referee='Jack'))

    print("Referee Review")
    print(handle_action(TEST_ID, IN_REF_REV, ASSIGN_REF,
                        referee='Jill', extra='Extra!'))
    print(handle_action(TEST_ID, IN_REF_REV, DELETE_REF,
                        referee='Jill'))
    print(handle_action(TEST_ID, IN_REF_REV, ACCEPT))
    print(handle_action(TEST_ID, IN_REF_REV, ACCEPT_REV))

    print("Author Revisions")
    print(handle_action(TEST_ID, AUTHOR_REVISIONS, DONE))

    print("Editor Review")
    print(handle_action(TEST_ID, EDITOR_REV, ACCEPT))
    print(handle_action(TEST_ID, EDITOR_REV, WITHDRAW))

    print("Copy Edit")
    print(handle_action(TEST_ID, COPY_EDIT, DONE))

    print("Author Review")
    print(handle_action(TEST_ID, AUTHOR_REVIEW, DONE))
    print(handle_action(TEST_ID, AUTHOR_REVIEW, WITHDRAW))

    print("Formatting")
    print(handle_action(TEST_ID, FORMATTING, DONE))


if __name__ == '__main__':
    main()
