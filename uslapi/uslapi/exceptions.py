"""USL exception classes

Includes two new types of exceptions.

The first is :class:`.StandardAPIException`, which occurs when we get a success: false response from the universalscammerlist
The second is :class:`.MalformedAPIException`, which occurs when we get a response that we don't know what to do with
"""

class USLException(Exception):
    """The base USL Exception class that all other exception classes extend"""

    def __init__(self, *args, **kwargs):
        """Initialize a new generic usl exception"""

        super(USLException, self).__init__(*args, **kwargs)

class StandardAPIException(USLException):
    """Indicates that we got a success: false response from the USL"""

    def __init__(self, error_type, error_message):
        """Initialize a new StandardAPIException

        :param error_type: a string constant for detecting the specific type of error, based on the response
        :param error_message: a human-readable description of the error
        """

        super(StandardAPIException, self).__init__(error_type + ': ' + error_message)
        self.error_type = error_type
        self.error_message = error_message

class MalformedAPIException(USLException):
    """Indicates that we got a response that we don't know what to do with"""

    def __init__(self, error_str, data):
        """Initialize a new MalformedAPIException

        :param error_str: the reason we didn't expect this
        :param data: the returned data, in json form if available
        """

        super(MalformedAPIException, self).__init__(error_str)

        self.data = data
