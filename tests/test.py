from pymatic.client import Client
import os
import pprint
c = Client(client_id=os.environ['client_id'], client_secret=os.environ['client_secret'], access_token=os.environ['access_token'])


pprint.pprint(c.get_trips())
