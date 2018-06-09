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

print('bulk querying skipping 250 and dumping to file')

data = usl.bulk_query(user, 250)
with open('test_data.json', 'w') as outfile:
    json.dump(data, outfile)
    
input("Press Enter to continue...")

print('bulk querying skipping 2000 and dumping to file')

data = usl.bulk_query(user, 2000)
with open('test_data.json', 'w') as outfile:
    json.dump(data, outfile)


print('logging out...')
usl.logout(user)

print('logout success')