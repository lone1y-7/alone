import time
import fnmatch

class MockRedis:
    def __init__(self, host='localhost', port=6379, db=0, decode_responses=False):
        self.host = host
        self.port = port
        self.db = db
        self.decode_responses = decode_responses
        self.data = {}
        self.expiry = {}

    def config_set(self, key, value):
        return True

    def set(self, key, value):
        self.data[key] = value
        return True

    def setex(self, key, seconds, value):
        self.data[key] = value
        self.expiry[key] = time.time() + seconds
        return True

    def get(self, key):
        if key in self.expiry and time.time() > self.expiry[key]:
            del self.data[key]
            del self.expiry[key]
            return None
        return self.data.get(key)

    def keys(self, pattern):
        return [k for k in self.data.keys() if fnmatch.fnmatch(k, pattern)]

    def delete(self, *keys):
        count = 0
        for key in keys:
            if key in self.data:
                del self.data[key]
                if key in self.expiry:
                    del self.expiry[key]
                count += 1
        return count

    def memory_purge(self):
        pass

class exceptions:
    class ResponseError(Exception):
        pass

redis = MockRedis
