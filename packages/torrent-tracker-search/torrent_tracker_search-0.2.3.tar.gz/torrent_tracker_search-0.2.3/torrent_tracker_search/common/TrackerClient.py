from typing import Optional

from aiohttp import ClientSession

from torrent_tracker_search.common.TrackerResponse import TrackerResponse


class TrackerClient:
	
	session: Optional[ClientSession] = None
	
	async def get(self, url: str, params: Optional[dict] = None, allow_redirects: bool = True) -> TrackerResponse: ...
	
	async def post_raw(self, url: str, body: dict, params: Optional[dict] = None, allow_redirects: bool = True) -> TrackerResponse: ...
	
	async def post_form_data(self, url: str, body: dict, params: Optional[dict] = None, allow_redirects: bool = True) -> TrackerResponse: ...
	
	async def post_form_data_encoded(self, url: str, body: dict, params: Optional[dict] = None, allow_redirects: bool = True) -> TrackerResponse: ...
	