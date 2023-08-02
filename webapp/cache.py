from flask_caching import Cache

from config import Config


cache = Cache(config=Config.CACHE)
