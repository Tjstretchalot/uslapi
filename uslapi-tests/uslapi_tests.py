import uslapi
import json

usl = uslapi.UniversalScammerList('bot uslapi_tests by tjstretchalot')


input("Press Enter to continue...")

print('logging in...')
user = usl.login('username', 'password', '1day') # you need to fill this in with your data

print('login success')
print(user.session_id)
print(user.session_expires_at)

input("Press Enter to continue...")

print('checking if SGSMods is banned..')

data = usl.query(user, 'SGSMods')

print('result: ' + str(data))

input("Press Enter to continue...")

print('checking if tjstretchalot is banned..')

data = usl.query(user, 'tjstretchalot')

print('result: ' + str(data))

input("Press Enter to continue...")

print('checking if wildcard is banned..')

data = usl.query(user, '%%%')

print('result: ' + str(data))

input("Press Enter to continue...")

print('bulk querying first 50 using version 2 query')
data = usl.bulk_query2(user, 0, 50)
with open('test_data.json', 'w') as outfile:
    json.dump(data, outfile, sort_keys=True, indent=2)

input("Press Enter to continue...")

print('bulk querying next 50')
data = usl.bulk_query2(user, data['next_id'], 50)
with open('test_data.json', 'w') as outfile:
    json.dump(data, outfile, sort_keys=True, indent=2)

print('logging out...')
usl.logout(user)

print('logout success')
