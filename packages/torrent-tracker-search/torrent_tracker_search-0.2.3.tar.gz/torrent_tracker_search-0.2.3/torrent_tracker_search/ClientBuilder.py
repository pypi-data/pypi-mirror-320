from typing import List, Optional, Final, Dict

from aiohttp import ClientSession

from torrent_tracker_search.common.TrackerClient import TrackerClient


class ClientBuilder:
	
	DEFAULT_HEADERS: Final[Dict[str, str]] = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
	}
	
	def __init__(self, session: Optional[ClientSession] = None):
		self.session: ClientSession = session or ClientSession(headers=self.DEFAULT_HEADERS)
	
	def build(self, clients: List[TrackerClient]) -> List[TrackerClient]:
		for client in clients:
			client.session = self.session
		return clients
