# uslapi
This is the python wrapper around universalscammerlist.com

## Usage

In general, this is meant to provide a very thin python wrapper around the universalscammerlist.com api, so you don't have to worry about figuring out the exact parameters that you need to pass to the functions, but instead you have to figure out how to use the python class that is provided for you.

Since the universal scammer list is mostly a list, the main thing that you want to do on the website is get that list. However, the list is too big for you to fetch all at once, and it typically can't be stored entirely in memory. Thus the simplest solution of just downloading the entire list and then searching it locally whenever you need to is not particularly trivial.

You have two options, the first is to query user-by-user. This is great if you have a relatively low number of searches (less than one per second on average) and you won't blow up the server (less than 10 peak burst queries per second, separated by at least a minute between bursts). The second option is to download the whole database in stages, then update it periodically (you won't have to redownload the whole database to get new bans).

## Creating an account

This is going to assume that you are trying to make some kind of bot, which is run on it's own server and managed by a single person. Thus, whoever is managing the bot has a reddit account. That person should go to [this page](https://universalscammerlist.com/create_account.php) and following the instructions for registering his account. This *does not* add you to the universal scammer list, it simply lets me know who is using the api in case the server has to be upgraded in the future.

## Getting started

First, download the [latest release](https://github.com/Tjstretchalot/uslapi/releases/latest) and extract it into your python environments Lib folder (if you want it to work everywhere), or just adjacent to your project folder (if you want it to work for just this project).

Then, to get started with the api you should import it and select your user agent. Your user agent must start with `bot` or `interface`, and the choice depends on your type of project. If you are the only one running the code, `bot` is the correct choice. It should also include your username. 

```python

import uslapi

usl = uslapi.UniversalScammerList('bot testing stuff by /u/myusernamehere')
```

Next you need to login with the username and password from the website. You are encouraged to always logout at the end of the script. A nice way to do this is with `atexit` and it is included here as well:

```python

user = usl.login('username', 'password')

def _logout():
  usl.logout(user)

import atexit
atexit.register(_logout)
```

Alright, now we have everything we need to query the database. If we just want to check if johndoe is banned, that's pretty easy:

```python

# is johndoe banned?
data = usl.query(user, 'johndoe')
if data['banned']:
  print('He\'s up to no good!')
else:
  print('He seems like a fine guy')
```

Of course, you might want a bit more information than if johndoe is banned. However, the universal scammer list is a coalition of subreddits, and while typically a user is banned in one spot and then everyone else just copies that ban (the automatic way), there are a sizeable number of people banned for different reasons on many subreddits. For this endpoint, you can simply get the list of all of the reasons they were banned by passing the format parameter:

```python
from datetime import datetime 

# let's get some more information
data = usl.query(user, 'johndoe', format = 2)

if data['grandfathered']:
  print('He was on the old usl list when we migrated to the new database')
elif not data['history']:
  print('he has no history on the usl')
else:
  for history in data['history']:
    print('on ' + history['subreddit'] + ' they performed ' + history['kind'])
    if history['kind'] == 'ban':
      print('  reason:   ' + history['description'])
      print('  duration: ' + history['details'])
    print('  when:     ' + datetime.fromtimestamp(history['time'] / 1000.0))
```

Alright, that's everything for querying the database for a single user. For getting everything, it's slightly more complicated. First, we have to fetch all the grandfathered users:

```python
# be careful running this in idle, it will freeze if you try to print this out. Depending on what you're trying 
# to do, it might be a good idea to look at the source code for this function and parse the response using a smaller
# buffer. However most servers can handle keeping this small section completely in memory for a bit while you do something
# with it

data = usl.bulk_query(user)

print('got ' + len(data) + ' grandfathered users. each has a key 'username' and they are all banned. the reason is just grandfathered')
```

Next we have to fetch the normal list, which is much larger. Luckily, it's paginated to about 250 responses per query. You just need to provide an offset for where you're at. The following loops over everyone and prints the username and reason for ban (this will not work in idle but will work in a command prompt with limited history, though it'd be very slow)

Note that you don't get the full history of each guy like in the query endpoint, you just get my heuristic for the best message to display. This is because the full history takes too long to fetch for most people and is typically not used in an automated fashion. If you need the full history of everything, please tell me about your usecase in a new issue.

```python
import time

offset = 0
data = usl.bulk_query(user, offset = offset)
while data:
  print('got another ' + len(data) + ' normal responses')
  
  for banned_dude in data:
  
    print(banned_dude['username'] + ' was banned for ' + banned_dude['ban_reason'] + ' at ' + datetime.fromtimestamp(banned_dude['banned_at'] / 1000.0))
  
  offset = offset + len(data) # you should really subtract a small amount of buffer, like 5, and verify you see at least one duplicate
  time.sleep(5) # please don't blow up the server :(
  
  data = usl.bulk_query(user, offset = offset)
```

You can also update your database once you've finished fetching everything by using the since parameter. You are strongly encouraged to go back in time a bit before you last updated, because these are based on reddit times but you fetch based on what the uslbot knows about at the time. Thus, if you last updated at `last_updated_utc` then you could loop through the new stuff by doing the exact some thing but with

```python
fetch_from_time = last_updated_utc - 1000 * 60 * 60 # allow duplicates up to an hour old to make sure we don't miss anything
data = usl.bulk_query(user, offset = offset, since = fetch_from_time)
```

in both of the loop spots. As a warning, this function doesn't ever return unbans (which occur, though very infrequently, like once per week). So you should refetch the database to clear those maybe once every 1-3 months, or just verify hits against the query endpoint.
