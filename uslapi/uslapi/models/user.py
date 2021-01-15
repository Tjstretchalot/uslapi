class User(object):
    """Describes a currently logged in user"""

    def __init__(self, username, session_id, session_expires_at):
        self.username = username
        self.session_id = session_id
        self.session_expires_at = session_expires_at
