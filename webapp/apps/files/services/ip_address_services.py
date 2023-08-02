from typing import Dict, Optional

import requests

from cache import cache
from config import Config


class IpAddress:
    def __init__(self, ip_address: Optional[str]) -> None:
        self.ip_address = ip_address

    def get_location(self) -> Dict:
        location_data = cache.get(self.ip_address)
        if location_data:
            return location_data

        response = requests.get(f'https://ipinfo.io/{self.ip_address}?token={Config.IPINFO_TOKEN}').json()

        location_data = {
            'ip': self.ip_address,
            'city': response.get('city'),
            'region': response.get('region'),
            'country': response.get('country')
        }

        cache.add(self.ip_address, location_data, timeout=(60*60)*4)

        return location_data
