import logging
import requests
import pprint
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

class Client:
        def __init__(self, access_token=None, refresh_token=None, client_id=None, client_secret=None):
                self.access_token = access_token
                self.refresh_token = refresh_token
                self.client_id = client_id
                self.client_secret = client_secret
        def set_refresh_token_callback():
                pass
        def refresh_token():
                pass
        def get_vehicles(self):
                return Vehicle._fetch_all(self)
        def get_trips(self):
                return Trip._fetch_all(self)
        def get_devices(self):
                return Device._fetch_all(self)
        def _get_protocol(self, cls):
                return Protocol(cls, self)
        def get_vehicle(self, id):
                return Vehicle._fetch(id, self)
        def get_trip(self, id):
                return Trip._fetch(id, self)
        def get_device(self, id):
                return Device._fetch(id, self)
class Protocol:
        base_url = "https://api.automatic.com"
        def __init__(self, cls, client):
                self.cls = cls
                self.client = client
                logging.info("Protocol init for class %s" % self.cls.__name__)
        def _request(self, uri, params={}, headers={}):
                headers.update({"Authorization":"Bearer %s" % self.client.access_token})
                if not params.get("limit", None):
                        params["limit"] = "200"
                logging.info("GET %s" % uri)
                r = requests.get(uri, params=params, headers=headers)
                j = r.json()
                return j
        def get(self, id=None):
                logging.info("fetching %s for %s" % (self.cls.path, self.cls.__name__))
                if id:
                        r = self._request(Protocol.base_url+self.cls.path+"/"+id)
                        return self.cls.build(r, client=self.client)
                else:
                        r = self._request(Protocol.base_url+self.cls.path)
                        results = [self.cls.build(i, client=self.client) for i in r['results']]
                        while r['_metadata']['next']:
                                r = self._request(r['_metadata']['next'])
                                results.extend([self.cls.build(i, client=self.client) for i in r['results']])
                        return results

class Entity:
        def __init__(self):
                self.client = None
        def to_dict(self):
                pass
        def _set_client(self, client):
                self.client = client
        @classmethod
        def _fetch_all(cls, client):
                p = client._get_protocol(cls)
                return p.get()
        @classmethod
        def _fetch(cls, id, client):
                p = client._get_protocol(cls)
                p.get(id=id)
        @classmethod
        def build(cls, d, client=None):
                instance = cls.from_dict(d)
                if client:
                        instance._set_client(client)
                return instance
        @classmethod
        def from_dict(cls, d):
                instance = cls()
                instance.id = d['id']
                return instance
        def _get_protocol(self):
                if self.client:
                        return self.client._get_protocol(self.__class__, self.client)
                else:
                        raise Exception("Entity does not have a valid client reference")
        def update(self):
                p = self._get_protocol()
                replacement = p.get(id=self.id)
                self.__dict__.update(replacement.__dict__)
        def __str__(self):
                return '%s(id=%s)' % (self.__class__.__name__, self.id)
        def __repr__(self):
                return self.__str__()
class Trip(Entity):
        path = '/trip'
        def __init__(self):
                pass
        def get_tags(self):
                return self.tags
        def get_tag(self, tag):
                p = self._get_protocol()

class Tag(Entity):
        path = '/tag'
        def __init__(self):
                pass
class Vehicle(Entity):
        path = '/vehicle'
        def __init__(self):
                pass

class Device(Entity):
        path = '/device'
        def __init__(self):
                pass




