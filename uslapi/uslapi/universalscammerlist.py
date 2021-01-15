"""Provides the usl class which is an extremely light wrapper around the usl endpoints"""

import requests
import json
from datetime import datetime
from .exceptions import *
from .models import User

class UniversalScammerList(object):
    """The UniversalScammerList class provides convenient access to the universalscammerlist API

    You can obtain this class via

    .. code-block:: python

        import uslapi

        usl = uslapi.UniversalScammerList('bot by /u/myusername for <reason for bot>')

    """

    def __init__(self, useragent = None):
        self.site_url = 'https://universalscammerlist.com/'
        self.api_url = self.site_url + 'api/'

        headers = requests.utils.default_headers()
        if useragent:
            if not useragent.startswith('bot') and not useragent.startswith('interface'):
                raise USLException('Your user agent should start with \'bot\' if its an automated process, or \'interface\' if its acting as an alternative to '\
                                   'the website frontend. It should also include your reddit username or your email')

            headers['User-Agent'] = useragent
        elif not headers['User-Agent'].startswith('bot') and not headers['User-Agent'].startswith('interface'):
            raise USLException('You must set the user-agent to start with \'bot\' if its an automated process or \'interface\' if its acting as an alternative to '\
                               'the website frontend. It should also include your reddit username or your email. You may set it via the requests api directly, '\
                               'or you can pass it as an argument to this constructor, ie usl = uslapi.UniversalScammerList(\'bot by /u/myusername for <reason>\')')



    def login(self, username, password, duration='forever'):
        """
        Logs in to the website using the given username and password. Returns
        a user which can be passed around for authentication.

        Valid durations are '1day', '30days', and 'forever'
        """

        rawresponse = requests.post(self.api_url + 'login.php', data = { 'username': username, 'password': password, 'duration': duration })

        jsonresponse = rawresponse.json()

        if not jsonresponse['success']:
            raise StandardAPIException(jsonresponse['error_type'], jsonresponse['error_message'])

        session_id_cookie = None
        for cookie in rawresponse.cookies:
            if cookie.name == 'session_id':
                session_id_cookie = cookie
                break

        if not session_id_cookie:
            raise MalformedAPIException('Got success response from login but no session id cookie was set', rawresponse)

        session_id = session_id_cookie.value
        session_expires_at = session_id_cookie.expires

        return User(username, session_id, session_expires_at)

    def logout(self, user):
        """
        Logs the specified user out. His token will no longer work until the next call to login
        """

        rawresponse = requests.post(self.site_url + 'logout.php', cookies = { 'session_id': user.session_id })

        if rawresponse.status_code < 200 or rawresponse.status_code >= 300:
            raise USLException('Got bad status code from logout page', rawresponse.status_code, rawresponse)

        user.session_id = None
        user.session_expires_at = None

    def query(self, user, query, format = 1, hashtags = None):
        """
        Query the database for a single person which matches the given query. By default,
        this returns if that user is banned and a best-guess for the most pertinent message
        to go along with the ban.

        If format is 2, this returns a list of a persons and their history on every subreddit that
        matches the hashtags.

        If hashtags is set, it can be a list of tags, for example [ '#scammer', '#sketchy' ]. If your
        tags are not in the whitelisted set ([ '#scammer', '#sketchy', '#troll' ]) then you must have
        elevated permission. By default, the hashtags are just all the allowed whitelisted hashtags.

        Return value is { person: 'actual_username_checked', banned: True or False }
        """

        if hashtags is None:
            hashtags = [ '#scammer', '#sketchy', '#troll' ]

        rawresponse = requests.get(self.api_url + 'query.php', params = { 'format': format, 'hashtags': ','.join(hashtags), 'query': query }, cookies = { 'session_id': user.session_id })

        jsonresponse = rawresponse.json()

        if not jsonresponse['success']:
            raise StandardAPIException(jsonresponse['error_type'], jsonresponse['error_message'])

        return jsonresponse['data']

    def bulk_query(self, user, offset = None, since = None):
        """
        Query the database in bulk.

        If both the offset and since are None, then this gets a list of all the grandfathered users in the database, in the form
        [ { username: 'johndoe', traditional: True, ban_reason: 'grandfathered' }, ... ]

        If the offset is not null but since is null, then if offset is 0 then this returns the first batch of people in the banlist that
        were not grandfathered. After that, the offset returns a batch but skips the first offset people.

        If offset is not null and since is not null, then this returns in the same manner as when since is null but ignores any bans that
        occurred after since. Note that this method will never seem to unban people, so you should periodically (perhaps once a month)
        refresh the database from scratch. Alternatively, if you don't get many hits, just verify using the query endpoint.

        Since should be a utc timestamp in milliseconds to be passed to the api, but datetimes are converted on your behalf. The returned
        values are in milliseconds utc
        """
        if since is not None and since is datetime:
            since = math.floor((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)

        rawresponse = requests.get(self.api_url + 'bulk_query.php', params = { 'offset': offset, 'since': since })

        jsonresponse = rawresponse.json()

        if not jsonresponse['success']:
            raise StandardAPIException(jsonresponse['error_type'], jsonresponse['error_message'])

        return jsonresponse['data']

    def bulk_query2(self, user, start_id = 0, limit = 250):
        """Uses the new version of the bulk query endpoint, which tends to
        timeout less often when being walked.

        Performs a bulk query of users who are on the universal scammer list.
        Only available while the bot is not propagating.

        This endpoint assumes you are querying for the common tags '#scammer',
        '#sketchy', and '#troll'. The returned "next_id" is used as the
        start_id of the next request, until it is None.

        Returns:
        {
          bans: [ { ... }, { ... }, ... ],
          next_id: int
        }
        """
        rawresponse = requests.get(
            self.api_url + 'bulk_query.php',
            params = {
                'version': 2,
                'start_id': start_id,
                'limit': limit
            }
        )

        jsonresponse = rawresponse.json()

        if not jsonresponse['success']:
            raise StandardAPIException(jsonresponse['error_type'], jsonresponse['error_message'])

        return jsonresponse['data']
