
# fields
KEY = 'key'
TITLE = 'title'
TEXT = 'text'
EMAIL = 'email'

TEST_KEY = 'HomePage'
SUBM_KEY = 'SubmissionsPage'
DEL_KEY = 'DeletePage'
texts = {}


text_dict = {
    TEST_KEY: {
        TITLE: 'Home Page',
        TEXT: 'This is a journal about building API servers.',
    },
    SUBM_KEY: {
        TITLE: 'Submissions Page',
        TEXT: 'All submissions must be original work in Word format.',
    },
    DEL_KEY: {
        TITLE: 'Delete Page',
        TEXT: 'This is a text to delete.',
    },
}


def create(key: str, title: str, text: str, email: str = None) -> bool:
    """
    Creates a new entry in text_dict if it is a unique key.
    """
    if key in text_dict:
        print(f"Key '{key}' already exists.")
        return False

    new_entry = {
        TITLE: title,
        TEXT: text,
    }

    if email:
        new_entry[EMAIL] = email
    text_dict[key] = new_entry
    return True


def delete(key):
    """
    Deletes a text entry.
    """
    if key not in texts:
        raise ValueError(f"Entry for '{key}' does not exist.")
    del texts[key]
    return f"Entry '{key}' deleted."


def update(key, value):
    """
    Updates an existing text entry.
    """
    if key not in texts:
        raise ValueError(f"Entry for '{key}' does not exist.")
    texts[key] = value
    return f"Entry '{key}' updated."


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each user email must be the key for another dictionary.
    """
    text = text_dict
    return text


def read_one(key: str) -> dict:
    # This should take a key and return the page dictionary
    # for that key. Return an empty dictionary of key not found.
    result = {}
    if key in text_dict:
        result = text_dict[key]
    return result


def main():
    print(read())


if __name__ == '__main__':
    main()
