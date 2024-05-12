import redis
from sshtunnel import SSHTunnelForwarder
from dto.auth import JwtData


class Redis:
    def __init__(self, redis_config, ssh_tunnel=None):
        if ssh_tunnel:
            self.server = SSHTunnelForwarder(**ssh_tunnel)
            self.server.start()
        self.redis = redis.Redis(**redis_config)

    def get(self, jti):
        # print("Get jti", jti)
        return self.redis.get(str(jti))

    def set(self, jti, ex):
        # print("Set drop", jti)
        return self.redis.set(str(jti), 1, ex=ex)
