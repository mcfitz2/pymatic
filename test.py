from pymatic import Client
import os
import pprint, json

creds = {}

with open(".creds.json", 'r') as f:
        creds = json.load(f)
def rf_cb(res):
        with open(".creds.json", 'w') as f:
                res['client_id'] = c.client_id
                res['client_secret'] = c.client_secret
                json.dump(res, f)

c = Client(client_id=os.environ['client_id'], client_secret=os.environ['client_secret'], access_token=creds['access_token'], refresh_token=creds['refresh_token'])
c.set_refresh_token_callback(rf_cb)
c.refresh()
print("get last trip")
pprint.pprint([t.to_dict() for t in c.get_trips(limit=1)])
print("get user")
user = c.get_me()
pprint.pprint(user.to_dict())
pprint.pprint(user.get_metadata().to_dict())
print("test limit on trips")
trips = c.get_trips(limit=10)
print("get trip tags")
pprint.pprint(trips[0].get_tags())
print("get first vehicle")
vehicle = c.get_vehicles(limit=1)[0]
pprint.pprint(vehicle.to_dict())
print("get MIL events")
pprint.pprint([e.to_dict() for e in vehicle.get_mil_events()])

