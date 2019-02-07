import logging
import requests
import pprint
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

class Client:
        base_url = "https://api.automatic.com"
        def __init__(self, access_token=None, refresh_token=None, client_id=None, client_secret=None):
                self.access_token = access_token
                self.refresh_token = refresh_token
                self.client_id = client_id
                self.client_secret = client_secret
        def set_refresh_token_callback(self, cb):
                self.rf_cb = cb
        def refresh_token(self):
                cb(access_token, refresh_token, expiry_date)
        def get_tags(self, **kwargs):
                return Tag._fetch_all(self, **kwargs)
        def get_vehicles(self, **kwargs):
                return Vehicle._fetch_all(self, **kwargs)
        def get_trips(self, **kwargs):
                return Trip._fetch_all(self, **kwargs)
        def get_devices(self, **kwargs):
                return Device._fetch_all(self, **kwargs)
        def _get_protocol(self, cls):
                return Protocol(cls, self)
        def get_vehicle(self, _id):
                return Vehicle._fetch(_id, self)
        def get_trip(self, _id):
                return Trip._fetch(_id, self)
        def get_device(self, _id):
                return Device._fetch(_id, self)
        def get_user(self, _id):
                return User._fetch(_id, self)
        def get_me(self):
                return User._fetch("me", self)
        def _request(self, uri, params={}, headers={}):
                headers.update({"Authorization":"Bearer %s" % self.access_token})
                if not params.get("limit", None):
                        params["limit"] = "200"
                logging.info("GET %s" % uri)
                r = requests.get(uri, params=params, headers=headers)
                j = r.json()
                return j
        def _get_entity(self, cls, _id, params={}):
                 r = self._request(self.base_url+cls.path+"/"+_id, params=params)
                 return cls.build(r, client=self)
        def _get_entities(self, cls, params={}):
                r = self._request(self.base_url+cls.path, params=params)
                if r.get("results", None):
                       results = [cls.build(i, client=self) for i in r['results']]
                       while r['_metadata']['next']:
                               r = self._request(r['_metadata']['next'])
                               results.extend([cls.build(i, client=self) for i in r['results']])
                       return results
                else:
                       return cls.build(r)
        def _get_sub_entities(self, cls, parent_id, params={}):
                r = self._request(self.base_url+(cls.path % parent_id), params=params)
                if r.get("results", None):
                       results = [cls.build(i, parent_id, client=self) for i in r['results']]
                       while r['_metadata']['next']:
                               r = self._request(r['_metadata']['next'])
                               results.extend([cls.build(i, parent_id, client=self) for i in r['results']])
                       return results
                else:
                       return cls.build(r, parent_id)

        def _get_sub_entity(self, cls, parent_id, _id=None, params={}):
                r = self._request(self.base_url+(cls.path % parent_id), params=params)
                return cls.build(r, parent_id)

class Entity:
        def __init__(self):
                self.client = None
        def to_dict(self):
                return dict([(key, value) for key, value in self.__dict__.items() if key in self.keys])
        def _set_client(self, client):
                self.client = client
        @classmethod
        def _fetch_all(cls, client, **kwargs):
                return client._get_entities(cls, params=kwargs)
        @classmethod
        def _fetch(cls, _id, client):
                return client._get_entity(cls, _id=_id)
        @classmethod
        def build(cls, d, client=None):
                instance = cls.from_dict(d)
                if client:
                        instance._set_client(client)
                return instance
        @classmethod
        def from_dict(cls, d):
                instance = cls()
                for key in cls.keys:
                        if key in d:
                                setattr(instance, key, d[key])
                return instance
        def update(self):
                replacement = self.client._get_entity(_id=self.id)
                self.__dict__.update(replacement.__dict__)
        def __str__(self):
                return '%s(id=%s)' % (self.__class__.__name__, self.id)
        def __repr__(self):
                return self.__str__()
class Trip(Entity):
        path = '/trip'
        keys = ["url",
                "id",
                "driver",
                "user",
                "started_at",
                "ended_at",
                "distance_m",
                "duration_s",
                "vehicle",
                "start_location",
                "start_address",
                "end_location",
                "end_address",
                "path",
                "fuel_cost_usd",
                "fuel_volume_l",
                "average_kmpl",
                "average_from_epa_kmpl",
                "score_events",
                "score_speeding",
                "hard_brakes",
                "hard_accels",
                "duration_over_70_s",
                "duration_over_75_s",
                "duration_over_80_s",
                "vehicle_events",
                "start_timezone",
                "end_timezone",
                "city_fraction",
                "highway_fraction",
                "night_driving_fraction",
                "idling_time_s",
                "tags"]

        def get_tags(self):
                return self.tags
        def get_tag(self, tag):
                return TripTag._fetch(self.client, self.id, tag)._to_tag()

class Tag(Entity):
        path = '/tag'
        keys = ['tag']
class Vehicle(Entity):
        path = '/vehicle'
        def get_mil_events(self, **kwargs):
                return MILEvent._fetch_all(self.client, self.id, **kwargs)

class Device(Entity):
        path = '/user/me/device'
        keys = ['id', 'version', 'direct_access_token', 'url', 'app_encryption_key']

class User(Entity):
        path = '/user'
        keys = ['email','email_verified','first_name','id','last_name','url','username']
        def get_metadata(self):
                return UserMetadata._fetch(self.client,  self.id)
#        def get_profile(self):
#                return UserProfile._fetch(self.client, self.id)
class SubEntity(Entity):
        @classmethod
        def build(cls, d, parent_id, client=None):
                instance = cls.from_dict(d, parent_id)
                if client:
                        instance._set_client(client)
                return instance
        @classmethod
        def from_dict(cls, d, parent_id):
                instance = super().from_dict(d)
                instance.parent_id = parent_id
                return instance
        def to_dict(self):
                d = super(SubEntity, self).to_dict()
                d['parent_id'] = self.parent_id
                return d
        @classmethod
        def _fetch_all(cls, client, parent_id, **kwargs):
                return client._get_sub_entities(cls, parent_id, params=kwargs)
        @classmethod
        def _fetch(cls, client, parent_id):
                return client._get_sub_entity(cls, parent_id)

        def update(self):
                replacement = self.client._get_sub_entity(cls)
                self.__dict__.update(replacement.__dict__)

class SubEntityWithID(SubEntity):
        @classmethod
        def _fetch(cls, client, parent_id, _id):
                return client.get_sub_entity(cls, _id=_id)
        def update(self):
                replacement = self.client.get_sub_entity(cls, id=self.id)
                self.__dict__.update(replacement.__dict__)
class TripTag(SubEntityWithID):
        path = "/trip/%s/tag"
        keys = ['tag', 'created_at']
        def _to_tag(self):
                t = Tag.from_dict(self.__dict__)
                return t
#class UserProfile(SubEntity):
#        path = "/user/%s/profile"
class MILEvent(SubEntity):
        path = "/vehicle/%s/mil"
        keys = ['code', 'on', 'description', 'created_at']
class UserMetadata(SubEntity):
        path = "/user/%s/metadata"
        keys = ['app_version','authenticated_clients','device_type','firmware_version','is_latest_app_version','is_staff','os_version','phone_platform','url','user']
