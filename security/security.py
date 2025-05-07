from functools import wraps

# import data.db_connect as dbc

"""
Our record format to meet our requirements will be:

{
    feature_name1: {
        create: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        read: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        update: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        delete: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
    },
    feature_name2: # etc.
}
"""

COLLECT_NAME = 'security'
CREATE = 'create'
READ = 'read'
UPDATE = 'update'
DELETE = 'delete'
USER_LIST = 'user_list'
CHECKS = 'checks'
LOGIN = 'login'
LOGIN_KEY = 'login_key'
IP_ADDR = 'ip_address'
DUAL_FACTOR = 'dual_factor'
SESSION = 'session'  # New check type for session validation

# Features:
PEOPLE = 'people'
BAD_FEATURE = 'baaaad feature'
JOURNAL = 'journal'  # New feature for journal entries

PEOPLE_MISSING_ACTION = READ
GOOD_USER_ID = 'jl12631@nyu.edu'
TEST_USER_ID = 'test@nyu.edu'  # Add test user

# Mock session storage - in real implementation, this would be in a database
active_sessions = {}


def create_session(user_id: str) -> str:
    """
    Creates a new session for a user and returns the session ID.
    In a real implementation, this would generate a secure session token.
    """
    session_id = (
        f"session_{user_id}_{len(active_sessions)}"  # Generate session ID
    )
    active_sessions[session_id] = {
        'user_id': user_id,
        'created_at': 'timestamp'  # Real implementation: use timestamp
    }
    return session_id


def check_session(user_id: str, **kwargs) -> bool:
    """
    Verifies if a user has a valid active session.
    """
    if 'session_id' not in kwargs:
        return False

    session_id = kwargs['session_id']
    if session_id not in active_sessions:
        return False

    session = active_sessions[session_id]
    return session['user_id'] == user_id


def invalidate_session(session_id: str) -> bool:
    """
    Invalidates a user's session.
    """
    if session_id in active_sessions:
        del active_sessions[session_id]
        return True
    return False


security_recs = None


# These will come from the DB soon:
TEST_RECS = {
    PEOPLE: {
        CREATE: {
            USER_LIST: [GOOD_USER_ID, TEST_USER_ID],  # Add test user
            CHECKS: {
                LOGIN: True,  # Only require login check
            },
        },
        DELETE: { # ADD TO USER LIST TO ALLOW DELETING
            USER_LIST: [GOOD_USER_ID, 'sejutinm@gmail.com'],
            CHECKS: {
                LOGIN: True,
            },
        },
    },
    BAD_FEATURE: {
        CREATE: {
            USER_LIST: [GOOD_USER_ID, TEST_USER_ID],  # Add test user
            CHECKS: {
                'Bad check': True,
            },
        },
    },
    JOURNAL: {
        CREATE: {
            USER_LIST: [GOOD_USER_ID, TEST_USER_ID],  # Add test user
            CHECKS: {
                LOGIN: True,
                SESSION: True,  # Require valid session
            },
        },
        READ: {
            USER_LIST: [GOOD_USER_ID, TEST_USER_ID],  # Add test user
            CHECKS: {
                LOGIN: True,
                SESSION: True,  # Require valid session
            },
        },
        UPDATE: {
            USER_LIST: [GOOD_USER_ID, TEST_USER_ID],  # Add test user
            CHECKS: {
                LOGIN: True,
                SESSION: True,  # Require valid session
            },
        },
        DELETE: {
            USER_LIST: [GOOD_USER_ID, TEST_USER_ID],  # Add test user
            CHECKS: {
                LOGIN: True,
                SESSION: True,  # Require valid session
            },
        },
    },
}


def is_valid_key(user_id: str, login_key: str):
    """
    This is just a mock of the real is_valid_key() we'll write later.
    """
    return True


def check_login(user_id: str, **kwargs):
    if LOGIN_KEY not in kwargs:
        return False
    return is_valid_key(user_id, kwargs[LOGIN_KEY])


def check_ip(user_id: str, **kwargs):
    if IP_ADDR not in kwargs:
        return False
    return True


def dual_factor(user_id: str, **kwargs):
    return True


CHECK_FUNCS = {
    LOGIN: check_login,
    IP_ADDR: check_ip,
    DUAL_FACTOR: dual_factor,
    SESSION: check_session,  # Add session check to available checks
}


def read() -> dict:
    global security_recs
    # dbc.read()
    security_recs = TEST_RECS
    return security_recs


def needs_recs(fn):
    """
    Should be used to decorate any function that directly accesses sec recs.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        global security_recs
        if not security_recs:
            security_recs = read()
        return fn(*args, **kwargs)
    return wrapper


@needs_recs
def read_feature(feature_name: str) -> dict:
    if feature_name in security_recs:
        return security_recs[feature_name]
    else:
        return None


@needs_recs
def is_permitted(
        feature_name: str, action: str, user_id: str, **kwargs
) -> bool:
    prot = read_feature(feature_name)
    if prot is None:
        return True
    if action not in prot:
        return True
    if USER_LIST in prot[action]:
        if user_id not in prot[action][USER_LIST]:
            return False
    if CHECKS not in prot[action]:
        return True
    for check in prot[action][CHECKS]:
        if check not in CHECK_FUNCS:
            raise ValueError(f'Bad check passed to is_permitted: {check}')
        if not CHECK_FUNCS[check](user_id, **kwargs):
            return False
    return True
